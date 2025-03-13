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

# Centralized content creation function with updated gemini-template
def create_content_locality_description(prompt: str, input_data: Dict[str, Any], model: str, city: str = "", locality: str = "") -> str:
    try:
        if model == "gemini(Undefined Template)":
            # Full SEO-friendly description for gemini-template
            full_query = f"""
            Provide a detailed and SEO-friendly description for {locality}, {city}. 
            Utilize data from "https://stage-www.squareyards.com/getlocalitydatafordesc/{city.lower()}/{locality.lower().replace(' ', '-')}" and incorporate trending "People Also Ask" (PAA) and "People Also Search For" data.
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
            - i want response in proper tags,dont add any special character and please direct give response dont mention any suggestion line or note.
            Use bullet points and tables where appropriate. Focus on information relevant to homebuyers and investors.
            ### **Response Format should be this:**
            The heading should be in <h2> heading </h2> for each section and paragrapgh should be in <p> paragrapgh</p> , i used your response direct on my UI, so give response according to UI.
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
            # Original behavior for gemini and chatgpt
            full_query = f"{prompt}\n\nData: {json.dumps(input_data)}"
            if model == "gemini(Fixed Template)":
                response = gemini_client.models.generate_content(
                    model="gemini-2.0-flash-001",
                    contents=full_query,
                    config=types.GenerateContentConfig(
                        tools=gemini_tools,
                        max_output_tokens=8192,
                        system_instruction="You are a helpful real-estate agent. I want response in proper tags and please direct give response dont mention any suggestion line or note. You may include additional useful details from Google search like PAA or pincode.",
                        temperature=0.9,
                    )
                )
                content = str(response.text).replace("html","")
            else:  # ChatGPT
                completion = openai.ChatCompletion.create(
                    deployment_id="sqy-gpt4o-mini",
                    model="sqy-gpt4o-mini",
                    temperature=0.9,
                    top_p=0.9,
                    n=3,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful real-estate agent. Ensure the final response feels human-written, not machine-generated. Here are the main details: " + prompt
                        },
                        {"role": "user", "content": json.dumps(input_data)}
                    ]
                )
                content = random.choice(completion.choices).message['content']

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
        model = st.selectbox("Select Model", ["gemini(Undefined Template)","gemini(Fixed Template)", "chatgpt"], index=0)
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

            response_sections = []

            if model == "gemini(Undefined Template)":
                # For gemini-template, generate the full description in one go
                full_description = create_content_locality_description("", {}, model, city, locality)
                response_sections.append(full_description)
            else:
                # Original section-by-section generation for gemini and chatgpt
                # 1. Overview
                overview_prompt = f"""
                Using the provided data, generate a description for the "summary" section about {locality}, {city}. 
                Write a concise and informative description of a residential locality, highlighting its key features.
                Include details about its location, connectivity, housing options, and nearby prominent areas.
                Keep the tone professional and engaging, making it user easy readable.
                - i want Easiest Language and Most Human-Written response.
                - I just want response, dont write anything beyond the response.
                ### **Response Format should be this:**
                <h2>[Creative Heading]</h2>  
                <p>[Striking opener and Location and nearby key areas (50-60 words)]</p>
                """
                overview_data = {
                    "basic_info": basic_info,
                    "micromarket": micromarket,
                    "supply_demand_data": supply_demand_data,
                    "top_five_localities": top_five_localities
                }
                overview = create_content_locality_description(overview_prompt, overview_data, model)
                response_sections.append(overview)

                # 2. Connectivity & Infrastructure
                connectivity_prompt = f"""
                Using the provided JSON data, generate a description for the "Connectivity & Infrastructure" section about {locality}, {city}.
                Use the following data: connecting_roads, indices_data.connectivity and metro_stations.
                Emphasize seamless access to key areas and business hubs.
                - i want Easiest Language and Most Human-Written response.
                - I just want response, dont write anything beyond the response.
                ### **Response Format should be this:**
                <h2>[Creative Heading]</h2>  
                <p>[Striking opener and Location, property options and nearby key areas using 80-100 words]</p>
                """
                connectivity_data = {
                    "indices_data": indices_data,
                    "connecting_roads": connecting_roads,
                    "metro_stations": metro_stations
                }
                connectivity = create_content_locality_description(connectivity_prompt, connectivity_data, model)
                response_sections.append(connectivity)

                # 3. Real Estate Trends
                real_estate_prompt = f"""
                Write a structured and insightful overview of real estate trends for {locality}, {city}.
                ### **Guidelines:**
                - Use a clear and engaging heading.
                - Cover key trends, including property types, price trends, BHK distribution, and buyer preferences.
                - Present data in a structured and easy-to-read format.
                - Ensure the tone is informative and relevant to homebuyers and investors.
                - i want Easiest Language and Most Human-Written response.
                - I just want response, dont write anything beyond the response.
                ### **Response Format should be this:**
                <h2>[Creative Heading]</h2>
                <ul>
                    <li><strong>Property Types:</strong> [Breakdown of property supply and key offerings (25 words paragraph)]</li>
                    <li><strong>Price Trends:</strong> [Insights into price per sq. ft. in nearby localities (25 words paragraph)]</li>
                    <li><strong>BHK Distribution:</strong> [Popular configurations and their market share (25 words paragraph)]</li>
                    <li><strong>Price Range:</strong> [Buyer preferences across different budget segments (25 words paragraph)]</li>
                </ul> 
                """
                real_estate_data = {
                    "supply_demand_data": supply_demand_data,
                    "nearby_localities": nearby_localities
                }
                real_estate = create_content_locality_description(real_estate_prompt, real_estate_data, model)
                response_sections.append(real_estate)

                # 4. Lifestyle & Amenities
                lifestyle_prompt = f"""
                Using the provided JSON data, generate a detailed and engaging "Lifestyle & Amenities" section for {locality}, {city}. 
                ### **Guidelines:**
                - Highlight premium lifestyle offerings, including top residential and commercial developments.
                - Use `indices_data.livability.facilities.Education` for schools.
                - Use `indices_data.livability.facilities.Healthcare` for hospitals.
                - Use `indices_data.lifestyle.facilities.Shopping` for shopping centers.
                - Use `indices_data.lifestyle.facilities.Entertainment` for recreational and fitness options.
                - Use `connecting_roads` for road-related amenities and accessibility.
                - i want Easiest Language and Most Human-Written response.
                - I just want response, dont write anything beyond the response.
                
                ### **Response Format should be this:**
                <h2>[Creative Heading]</h2>
                <ul>
                    <li><strong>Educational Institutions:</strong> [20 words]</li>
                    <li><strong>Healthcare Facilities:</strong> [20 words]</li>
                    <li><strong>Recreational & Shopping Centers:</strong> [20 words]</li>
                    <li><strong>Green Spaces & Sports Facilities:</strong> [20 words]</li>
                </ul>
                """
                lifestyle_data = {
                    "indices_data": indices_data,
                    "connecting_roads": connecting_roads
                }
                lifestyle = create_content_locality_description(lifestyle_prompt, lifestyle_data, model)
                response_sections.append(lifestyle)

                # 5. Nearby Localities & Their Impact
                nearby_prompt = f"""
                Using the provided JSON data, generate a detailed and structured "Nearby Localities & Their Impact" section for {locality}, {city}. 
                ### **Guidelines:**
                - Use `nearby_localities` to extract details such as distances and `avg_price_per_sqft`.
                - Highlight how each locality influences {locality}, focusing on property pricing, rental demand, and luxury housing.
                - Present data in an easy-to-read format with clear impact points.
                - Max 4-5 bullet points.
                - i want Easiest Language and Most Human-Written response.
                - I just want response, dont write anything beyond the response.
                ### **Response Format should be this:**
                <h2>[Creative Heading]</h2>
                <ul>
                    <li><strong>[Nearby Locality Name] ([Distance]):</strong> [Impact on {locality}, including price trends, rental demand, and market position]</li>
                    <li><strong>[Nearby Locality Name] ([Distance]):</strong> [Impact on {locality}, including price trends, rental demand, and market position]</li>
                    <li><strong>[Nearby Locality Name] ([Distance]):</strong> [Impact on {locality}, including price trends, rental demand, and market position]</li>
                </ul>
                """
                nearby_data = {"nearby_localities": nearby_localities}
                nearby = create_content_locality_description(nearby_prompt, nearby_data, model)
                response_sections.append(nearby)

                # 6. Why Invest
                investment_prompt = f"""
                Using the provided JSON data, generate a compelling "Why Invest in {locality}?" section for {locality}, {city}. 
                ### **Guidelines:**
                - Use `supply_demand_data.sale.property_types` to highlight the demand for builder floors and apartments.
                - Leverage `connecting_roads` to emphasize proximity to business hubs and its impact on rental yields.
                - Make logical assumptions about upcoming developments based on infrastructure growth trends.
                - i want Easiest Language and Most Human-Written response.
                - I just want response, dont write anything beyond the response.
                 ### **Response Format should be this:**
                <h2>[Creative Heading]</h2>
                <ul>
                    <li><strong>Strong Demand:</strong> [Highlight high demand for specific property types and its impact on investment potential (25 words)]</li>
                    <li><strong>Proximity to Business Hubs:</strong> [Explain connectivity advantages and their role in rental appreciation (25 words)]</li>
                    <li><strong>Future Growth Potential:</strong> [Discuss ongoing/upcoming developments and their expected impact on property values (25 words)]</li>
                </ul>
                """
                investment_data = {
                    "supply_demand_data": supply_demand_data,
                    "connecting_roads": connecting_roads
                }
                investment = create_content_locality_description(investment_prompt, investment_data, model)
                response_sections.append(investment)

                # 7. People Also Ask
                paa_prompt = f"""
                Using the provided data, generate a structured "People Also Ask (PAA)" section for {locality}, {city}. 
                ### **Guidelines:**
                - Use `indices_data.connectivity` to describe connectivity and transport options.
                - Utilize `indices_data.livability` for insights on schools, hospitals, and amenities.
                - Leverage `indices_data.education` and `indices_data.health` for detailed educational and healthcare information.
                - i want Easiest Language and Most Human-Written response.
                - I just want response, dont write anything beyond the response.
                
                ### **Response Format should be this**
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
                paa_data = {"indices_data": indices_data}
                paa = create_content_locality_description(paa_prompt, paa_data, model)
                response_sections.append(paa)

            # Combine and display
            final_response = "\n\n".join(response_sections).replace("\n", "")
            st.markdown(final_response, unsafe_allow_html=True)

if __name__ == "__main__":
    main()