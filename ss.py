from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
import random
import re

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

# # Pydantic model for request body
# class ListingDescriptionRequest(BaseModel):
#     metadata: dict

# Listing Description Format Function
def create_content_listing_description_format():
    font_list = [
        "The response format should be flexible—either a single paragraph, format:(<p>paragrapgh</p>) or a mix of one paragraph with 2–3 meaningful bullet points,format:(<ul> <li>...</li></ul>), depending on what best suits the data.",
        "The response format should be flexible—either a single or double paragraph in this format (<p>.....</p>)",
        "The response format should be a single paragraph in this format (<p>paragrapgh</p>)"
    ]
    print(random.choice(font_list))
    return random.choice(font_list)

# Listing Description Function
def create_content_listing_description(metadata: str) -> str:
    prompt = """
    You are a specialized assistant designed to generate concise and appealing property listing descriptions for real estate. Based on the provided property metadata:

    Output Requirements:
    - Format the output in clean, structured HTML that matches the specified template
    - Mention lifestyle benefits (spacious living, modern design, natural light)
    - Exclude city or locality details.
    - Exclude Null key details.
    - Output response should be like human generated so no fancy or repetitive words.
    - Base the output strictly on the provided data
    - {select_font}

    Important Notes:
    - Do not include any introductory or explanatory text in your response
    - Direct return response, do not add any suggestions, notes, or additional commentary
    - Keep the description human written like a beginner and simaple natural
    
    Generate a property listing description based on the following metadata: {metadata}
    """
    try:
        full_query = prompt.format(metadata=metadata, select_font=create_content_listing_description_format())
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=full_query,
            config=types.GenerateContentConfig(
                max_output_tokens=2048,
                system_instruction="You are a helpful real-estate agent. Please direct give response dont mention any suggestion line or note. Use simple, natural, and realistic language.",
                temperature=0.7,
            )
        )
        content = response.text
        # print(content)
        content = content.replace("```html", "").replace("```", "").replace("-", " ").replace("*", "").replace("`", "").replace("\<p>", "<p>").replace("\</p>", "</p>").replace("\<ul>", "<ul>").replace("\</ul>", "</ul>").replace("\n","").replace("  ","")
        # print(content)
        return content
    except Exception as e:
        return f"Error generating listing description: {str(e)}"

# FastAPI endpoint for listing description
@app.post("/listing-description")
async def generate_listing_description(request: str):

    description = create_content_listing_description(request)    
    return {"description": description}
