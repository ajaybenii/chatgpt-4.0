from dotenv import load_dotenv
import os
import streamlit as st
import requests
import json
import random
import re
import openai
from google import genai
from google.genai import types
from typing import Dict, Any
from locality_data_extract import DataExtractor
from fastapi.encoders import jsonable_encoder
from http.client import HTTPException


# loading environment variables from .env file
load_dotenv()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './sqy-prod.json'

# OPENAI_DEPLOYMENT_NAME = 'sqy-gpt4o-mini'
openai.api_type = "azure"
openai.api_key = os.getenv('openai.api_key')
openai.api_base = 'https://sqy-openai.openai.azure.com/'
openai.api_version = "2023-05-15"

# Initialize Gemini client
gemini_client = genai.Client(
    http_options=types.HttpOptions(api_version="v1beta1"),
    vertexai=True,
    project='sqy-prod',
    location='us-central1'
)

gemini_tools = [types.Tool(google_search=types.GoogleSearch())]

# Centralized content creation function with combined prompt
def create_content_locality_description(prompt: str, input_data: Dict[str, Any], model: str, city: str = "", locality: str = "") -> str:
    try:
        if model == "gemini-no-template":
            # Full SEO-friendly description for gemini-no-template (unchanged)
            url = f"https://www.squareyards.com/getlocalitydatafordesc/{city.lower()}/{locality.lower().replace(' ', '-')}"
            full_query = f"""
            Provide a detailed and SEO-friendly description for {locality}, {city}. 
            Utilize data from {url} and incorporate trending "People Also Ask" (PAA) data.
            Descriptions should be in easy language and should look human-generated, not robotic.
            The description should cover:
            - Location and connectivity (metro, roads, proximity to business hubs)
            - Lifestyle and livability (amenities, green spaces, safety)
            - Entertainment and amenities (shopping, restaurants, recreation)
            - Education and healthcare (schools, hospitals)
            - Property rates and price trends
            - Real estate builders and projects (newly launched, ready to move)
            - Advantages and disadvantages
            - Future prospects
            - FAQs based on PAA(People Also Ask)
            - I want response in proper tags, dont add any special character and please direct give response dont mention any suggestion line or note.
            Use bullet points and tables where appropriate. Focus on information relevant to homebuyers and investors.
            ### **Response Format should be this:**
            The heading should be in <h2> heading </h2> for each section and paragraph should be in <p> paragraph</p> , i used your response direct on my UI, so give response according to UI.
            <h2>People Also Ask</h2>
            <div class="panel">
                <div class="panelHeader">
                    <strong>Q: [Your Question Here]</strong>
                    <em class="icon-arrow-down"></em>
                </div>
                <div class="panelBody">
                    <p>[Your Answer Here]</p>
                </div>
            </div>
            """
            response = gemini_client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=full_query,
                config=types.GenerateContentConfig(
                    tools=gemini_tools,
                    max_output_tokens=8192,
                    system_instruction="You are a helpful real-estate agent. I want response in proper tags and please direct give response dont mention any suggestion line or note. You may include additional useful details from Google search like PAA or pincode.",
                    temperature=0.7,
                )
            )
            content = response.text
        else:
            # Combined prompt for gemini and chatgpt
            full_query = f"""
            Using the provided JSON data, generate a complete and structured locality description for {locality}, {city}. 
            Descriptions should be in easy language, SEO-friendly, and human-generated (not robotic). 
            Include the following sections with their specific guidelines and formatting:

            ### 1. Overview
            - Write a concise and informative description (50-60 words) highlighting key features.
            - Include location, connectivity, housing options, and nearby prominent areas.
            - Data: basic_info, micromarket, supply_demand_data, top_five_localities
            ### **Format:**
            <h2>[Creative Heading]</h2>
            <p>[Description]</p>

            ### 2. Connectivity & Infrastructure
            - Emphasize seamless access to key areas and business hubs (70-80 words).
            - Use data: connecting_roads, indices_data.connectivity, metro_stations
            ### **Format:**
            <h2>[Creative Heading]</h2>
            <p>[Description]</p>

            ### 3. Real Estate Trends
            - Cover property types, price trends, BHK distribution, and buyer preferences.
            - Use data: supply_demand_data, nearby_localities
            ### **Format:**
            <h2>[Creative Heading]</h2>
            <ul>
                <li><strong>Property Types:</strong> [25 words]</li>
                <li><strong>Price Trends:</strong> [25 words]</li>
                <li><strong>BHK Distribution:</strong> [25 words]</li>
                <li><strong>Price Range:</strong> [25 words]</li>
            </ul>

            ### 4. Lifestyle & Amenities
            - Highlight premium lifestyle offerings.
            - Use data: indices_data.livability.facilities.Education, indices_data.livability.facilities.Healthcare, 
            indices_data.lifestyle.facilities.Shopping, indices_data.lifestyle.facilities.Entertainment, connecting_roads
            
            ### **Format:**
            <h2>[Creative Heading]</h2>
            <ul>
                <li><strong>Educational Institutions:</strong> [20 words]</li>
                <li><strong>Healthcare Facilities:</strong> [20 words]</li>
                <li><strong>Recreational & Shopping Centers:</strong> [20 words]</li>
                <li><strong>Green Spaces & Sports Facilities:</strong> [20 words]</li>
            </ul>

            ### 5. Nearby Localities & Their Impact
            - Highlight influence on property pricing, rental demand, and luxury housing (max 4-5 points).
            - Use data: nearby_localities (distances, avg_price_per_sqft)
            - Max 4-5 bullet points.
            ### **Format:**
            <h2>[Creative Heading]</h2>
            <ul>
                <li><strong>[Locality Name] ([Distance]):</strong> [Impact]</li>
                <li><strong>[Locality Name] ([Distance]):</strong> [Impact]</li>
                <li><strong>[Locality Name] ([Distance]):</strong> [Impact]</li>
                <li><strong>[Locality Name] ([Distance]):</strong> [Impact]</li>
            </ul>

            ### 6. Why Invest
            - Highlight demand, connectivity, and future growth potential.
            - Use data: supply_demand_data.sale.property_types, connecting_roads
            ### **Format:**
            <h2>[Creative Heading]</h2>
            <ul>
                <li><strong>Strong Demand:</strong> [25 words]</li>
                <li><strong>Proximity to Business Hubs:</strong> [25 words]</li>
                <li><strong>Future Growth Potential:</strong> [25 words]</li>
            </ul>

            ### 7. People Also Ask
            - Provide 4-5 FAQs based on connectivity, livability, education, and healthcare.
            - Use data: indices_data.connectivity, indices_data.livability, indices_data.education, indices_data.health
            ### **Format:**
            <h2>People Also Ask</h2>
            <div class="panel">
                <div class="panelHeader">
                    <strong>Q: [Question]</strong>
                    <em class="icon-arrow-down"></em>
                </div>
                <div class="panelBody">
                    <p>[Answer]</p>
                </div>
            </div>

            ### Guidelines:
            - I want response in proper tags, no special characters, and direct response (no notes/suggestions).
            - Use bullet points and structured format where specified.
            - Focus on homebuyers and investors.

            ### Data:
            {json.dumps(input_data)}
            """
            if model == "gemini":
                response = gemini_client.models.generate_content(
                    model="gemini-2.0-flash-001",
                    contents=full_query,
                    config=types.GenerateContentConfig(
                        tools=gemini_tools,
                        max_output_tokens=8192,
                        system_instruction="You are a helpful real-estate agent. I want response in proper tags and please direct give response dont mention any suggestion line or note .You may include additional useful details from Google search like PAA or pincode.",
                        temperature=0.9,
                    )
                )
                content = str(response.text).replace("html", "")
            else:  # ChatGPT
                completion = openai.ChatCompletion.create(
                    deployment_id="sqy-gpt4o-mini",
                    model="sqy-gpt4o-mini",
                    temperature=0.9,
                    top_p=0.9,
                    n=1,  # Single response for simplicity
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful real-estate agent. Ensure the final response feels human-written, not machine-generated. Generate the response in proper HTML tags as per the prompt."
                        },
                        {"role": "user", "content": full_query}
                    ]
                )
                content = completion.choices[0].message['content']

        cleaned_content = re.sub(r"[\([{})\]]|`|\*|#", "", content).replace("\n", "")
        return cleaned_content
    except Exception as e:
        return f"Error generating content: {str(e)}"

# Streamlit App
def main():
    st.title("Locality Description Generator")
    st.write("Generate detailed locality descriptions using AI models")

    # Input form
    with st.form(key='locality_form'):
        city = st.text_input("City", "")
        locality = st.text_input("Locality", "")
        model = st.selectbox("Select Model", ["gemini-no-template", "gemini", "chatgpt"], index=0)
        submit_button = st.form_submit_button(label='Generate Description')

    if submit_button and city and locality:
        with st.spinner("Generating locality description..."):
            # Fetch locality data
            api_url = f"https://stage-www.squareyards.com/getlocalitydatafordesc/{city.lower()}/{locality.lower().replace(' ', '-')}"
            response = requests.get(api_url)

            if response.status_code != 200:
                st.error("Failed to fetch locality data")
                return

            data = response.json()
            extractor = DataExtractor(data)
            
            # Extract data
            basic_info = extractor.get_basic_info()
            micromarket = extractor.get_micromarket()
            supply_demand_data = extractor.get_supply_demand()
            indices_data = extractor.get_indices_data()
            developers_data = extractor.get_developers_data()
            connecting_roads = extractor.get_connecting_roads()
            metro_stations = extractor.get_metro_stations()
            top_five_localities = extractor.get_top_five_localities()
            nearby_localities = extractor.get_nearby_localities()

            # Combine all data into a single dictionary
            all_data = {
                "basic_info": basic_info,
                "micromarket": micromarket,
                "supply_demand_data": supply_demand_data,
                "indices_data": indices_data,
                "developers_data": developers_data,
                "connecting_roads": connecting_roads,
                "metro_stations": metro_stations,
                "top_five_localities": top_five_localities,
                "nearby_localities": nearby_localities
            }

            # Generate description
            full_description = create_content_locality_description("", all_data, model, city, locality)
            st.markdown(full_description, unsafe_allow_html=True)

if __name__ == "__main__":
    main()