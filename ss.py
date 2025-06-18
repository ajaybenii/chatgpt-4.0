from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from collections import deque
from google import genai
from google.genai import types
import re
from fastapi.encoders import jsonable_encoder
from difflib import SequenceMatcher
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './sqy-prod.json'

# Initialize Gemini client
gemini_client = genai.Client(
    http_options=types.HttpOptions(api_version="v1beta1"),
    vertexai=True,
    project='sqy-prod',
    location='us-central1'
)

app = FastAPI()

# Store the last 3 descriptions
previous_descriptions = deque(maxlen=3)

# Pydantic model for request body
class ListingDescriptionRequest(BaseModel):
    listing_data: dict | str | list

# Listing Description Prompt (must be defined externally or replaced with your actual prompt)
Listing_description_prompt = """
Role:
You are an expert content writer specializing in real estate descriptions for a diverse audience.

Objective:
Craft a compelling, informative, and unique real estate description based on the provided data. The description should feel fresh, engaging, and tailored to the property type and target audience (home buyers, tenants, or investors).

Instructions:
1. Use all provided data accurately. Do not omit or alter factual details such as price, size, or amenities.
2. Format prices as '50 lakh,' '3.20 crore,' or '25 thousand' without currency prefixes like 'INR' or 'Rs.'.
3. Do not mention any real estate organization names, project names, or specific locations (e.g., 'Fort Oasis', 'MG Road', neighborhoods, cities, or landmarks like 'nearby schools'). Use generic terms like 'this apartment,' 'this shop,' or 'this home'.
4. Write in a natural, conversational tone with simple, beginner-level language. Avoid fancy or repetitive words like 'harmonious,' 'serene,' 'tranquil,' 'blend,' 'oasis,' 'vibrant,' 'opportunity,' 'well-being,' 'prime,' or 'bustling.'
5. The description must be a single flowing paragraph.
6. Ensure the first sentence is unique for each listing. Avoid phrases like 'Step into...', 'Discover...', 'Imagine...', 'Envision...', 'Nestled in...', or 'In the heart of...'. Use varied themes (e.g., lifestyle, investment potential, comfort) and sentence structures (e.g., questions, statements).
7. Ensure the last sentence is distinct and natural, avoiding terms like 'opportunity,' 'soughtafter,' or 'don’t miss out.' Conclude with a call to action or emotional hook aligned with the property’s appeal.
8. To maximize variety, alternate emotional appeals (e.g., excitement, calm, ambition) and focus areas (e.g., amenities, investment value) across listings.
9. If provided with previous descriptions, ensure the new description’s first and last sentences use entirely different phrasing and themes.
10. Highlight lifestyle benefits (e.g., spacious living, modern design, natural light) and exclude null or irrelevant details.
11. Return only the paragraph without any introductory text, suggestions, notes, or additional commentary.
"""

def format_description(description):
    """
    Breaks the paragraph into: first_paragraph, body (list), and last_paragraph.
    """
    description = str(description)
    description = (
        description.replace("*", "")
        .replace("?", ". ")
        .replace(";", " ")
        .replace("Rs.", "")  # Remove currency prefix
        .replace("INR", "")  # Remove INR if present
        .replace("sq.ft", "sqft")
        .replace("sq.", "sq")
        .replace("sqft.", "sqft")
        .replace("sq.ft.", "square feet")
        .replace("-", "")
        .replace("#", "")
        .replace("'", "")
    )

    # Split into sentences
    raw_sentences = re.split(r'(?<=[.])\s+', description.strip())
    sentences = [s.strip() for s in raw_sentences if s.strip()]

    if len(sentences) < 3:
        return {
            'first_paragraph': sentences[0] if sentences else '',
            'body': [],
            'last_paragraph': sentences[-1] if len(sentences) > 1 else ''
        }

    return {
        'first_paragraph': sentences[0],
        'body': sentences[1:-1],
        'last_paragraph': sentences[-1]
    }

def create_listing_description(content):
    """Generates a real estate description using Gemini with past output awareness."""
    max_attempts = 3
    banned_phrases = [
        "step into", "discover", "imagine", "nestled in", "in the heart of",
        "exceptional opportunity", "soughtafter", "dont miss out"
    ]

    for attempt in range(max_attempts):
        try:
            content = jsonable_encoder(content)

            context_message = ""
            if previous_descriptions:
                context_message = "These are the opening and closing lines of the last 3 descriptions. Ensure the new description’s opening and closing lines are entirely different in phrasing and theme:\n"
                for i, desc in enumerate(previous_descriptions, 1):
                    structured = format_description(desc)
                    context_message += f"Description {i}:\nOpening: {structured['first_paragraph']}\nClosing: {structured['last_paragraph']}\n\n"

            # Prepare prompt for Gemini
            full_query = f"{Listing_description_prompt}\n\n{context_message}\nNow write a new description for the following listing:\n{content}"

            # Call Gemini API
            response = gemini_client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=full_query,
                config=types.GenerateContentConfig(
                    max_output_tokens=2048,
                    system_instruction="You are a helpful real-estate agent. Return only a single paragraph, using simple, natural, realistic language. Do not include suggestions, notes, or additional commentary.",
                    temperature=0.9,  # Match OpenAI's temperature
                )
            )

            description = response.text.strip()
            description = re.sub(r"[\([{})\]]", "", description)

            structured = format_description(description)

            # Validate for banned phrases
            first_para = structured['first_paragraph'].lower()
            last_para = structured['last_paragraph'].lower()
            if any(phrase in first_para or phrase in last_para for phrase in banned_phrases):
                if attempt < max_attempts - 1:
                    continue
                raise Exception("Generated description contains banned phrases after max attempts")

            # Check similarity with previous openings/closings
            for prev_desc in previous_descriptions:
                prev_structured = format_description(prev_desc)
                prev_first = prev_structured['first_paragraph'].lower()
                prev_last = prev_structured['last_paragraph'].lower()
                logging.info(f"Opening similarity with prev: {SequenceMatcher(None, first_para, prev_first).ratio()}")
                logging.info(f"Closing similarity with prev: {SequenceMatcher(None, last_para, prev_last).ratio()}")
                if SequenceMatcher(None, first_para, prev_first).ratio() > 0.6 or \
                   SequenceMatcher(None, last_para, prev_last).ratio() > 0.6:
                    if attempt < max_attempts - 1:
                        continue
                    raise Exception("Generated description too similar to previous after max attempts")

            # Save for context
            previous_descriptions.append(description)

            return structured

        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_attempts - 1:
                raise Exception(f"Error in description completion after {max_attempts} attempts: {str(e)}")

# FastAPI endpoint for listing description
@app.post("/listing-description")
async def generate_listing_description(request: ListingDescriptionRequest):
    try:
        result = create_listing_description(request.listing_data)
        return result
    except Exception as e:
        logging.error(f"Endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating listing description: {str(e)}")