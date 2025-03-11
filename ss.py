from dotenv import load_dotenv
import os
import streamlit as st
import requests
import json
import random
import re
import openai
from typing import Dict, Any
from locality_data_extract import DataExtractor
from fastapi.encoders import jsonable_encoder
from http.client import HTTPException


# loading environment variables from .env file
load_dotenv()

# OPENAI_DEPLOYMENT_NAME = 'sqy-gpt4o-mini'
openai.api_type = "azure"
openai.api_key = os.getenv('openai.api_key')
openai.api_base = 'https://sqy-openai.openai.azure.com/'
openai.api_version = "2023-05-15"

# Centralized content creation function (adapted for Streamlit)
def create_content_locality_description(prompt: str, input_data: Dict[str, Any]) -> str:
    try:
        input_data = jsonable_encoder(input_data)  # Ensure JSON compatibility
        completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt4o-mini",
            model="sqy-gpt4o-mini",
            temperature=0.9,
            top_p=0.9,
            n=3,
            messages=[
                {"role": "system", "content": "Write the response as if you’re a friendly, knowledgeable real estate agent speaking naturally to a client. Avoid robotic or overly formal language, and use vivid, relatable descriptions to make it engaging. Ensure the final response feels human-written, not machine-generated. Here are the main details: " + prompt},
                {"role": "user", "content": json.dumps(input_data)}  # Clean JSON dump
            ]
        )
        content = random.choice(completion.choices).message['content']
        # Clean up unwanted characters
        cleaned_content = re.sub(r"[\([{})\]]|`|\*|#", "", content).replace("\n", "")
        return cleaned_content
    except Exception as e:
        st.error(f"Content creation failed: {e}")
        return "Error generating content"

# Function to fetch and process locality data
def generate_locality_description(city: str, locality: str):
    st.write(f"Fetching data for {city}/{locality}...")
    api_url = f"https://stage-www.squareyards.com/getlocalitydatafordesc/{city}/{locality}"
    response = requests.get(api_url)

    if response.status_code != 200:
        st.error(f"API request failed with status {response.status_code}")
        return "Failed to fetch locality data"

    st.write("Data fetched successfully!")
    data = response.json()

    # # Placeholder for DataExtractor (assuming it exists in your environment)
    # class DataExtractor:
    #     def __init__(self, data): self.data = data
    #     def get_basic_info(self): return self.data.get("basic_info", {})
    #     def get_micromarket(self): return self.data.get("micromarket", {})
    #     def get_supply_demand(self): return self.data.get("supply_demand", {})
    #     def get_indices_data(self): return self.data.get("indices_data", {})
    #     def get_developers_data(self): return self.data.get("developers_data", {})
    #     def get_connecting_roads(self): return self.data.get("connecting_roads", [])
    #     def get_metro_stations(self): return self.data.get("metro_stations", [])
    #     def get_top_five_localities(self): return self.data.get("top_five_localities", [])
    #     def get_nearby_localities(self): return self.data.get("nearby_localities", [])

    extractor = DataExtractor(data)
    basic_info = extractor.get_basic_info()
    micromarket = extractor.get_micromarket()
    supply_demand_data = extractor.get_supply_demand()
    indices_data = extractor.get_indices_data()
    connecting_roads = extractor.get_connecting_roads()
    metro_stations = extractor.get_metro_stations()
    top_five_localities = extractor.get_top_five_localities()
    nearby_localities = extractor.get_nearby_localities()

    response_sections = []

    # 1. Overview
    st.write("Generating Overview...")
    overview_prompt = f"""
    Using the provided JSON data, generate a description for the "Overview" section about {locality}, {city}. 
    Use the following data: basic_info (for locality name), micromarket (for micromarket details), 
    supply_demand_data.sale.property_types (for property types like apartments, builder floors, independent houses),
    and top_five_localities (for proximity to key areas). Highlight its appeal as a residential hub.
    Format the response as follows:
    ### **Response Format:**
    <h2>[Creative Heading]</h2>  
    <p>[Striking opener and Location and nearby key areas (50-60 words)]</p>
    """
    overview_data = {"basic_info": basic_info, "micromarket": micromarket, "supply_demand_data": supply_demand_data, "top_five_localities": top_five_localities}
    # print(overview_data)
    response_sections.append(create_content_locality_description(overview_prompt, overview_data))

    # 2. Connectivity & Infrastructure
    st.write("Generating Connectivity & Infrastructure...")
    connectivity_prompt = f"""
    Using the provided JSON data, generate a description for the "Connectivity & Infrastructure" section about {locality}, {city}.
    Use the following data: connecting_roads, indices_data.connectivity and metro_stations.
    Emphasize seamless access to key areas and business hubs.
    Format the response as follows:
    ### **Response Format:**
    <h2>[Creative Heading]</h2>  
    <p>[Striking opener and Location, property options and nearby key areas using 80-100 words]</p>
    """
    connectivity_data = {"indices_data": indices_data, "connecting_roads": connecting_roads, "metro_stations": metro_stations}
    response_sections.append(create_content_locality_description(connectivity_prompt, connectivity_data))

    # 3. Real Estate Trends
    st.write("Generating Real Estate Trends...")
    real_estate_prompt = f"""
    Write a structured and insightful overview of real estate trends for {locality}, {city}.
    ### **Guidelines:**
    - Use a clear and engaging heading.
    - Cover key trends, including property types, price trends, BHK distribution, and buyer preferences.
    - Present data in a structured and easy-to-read format.
    - Dont write any additional line beyond the response format at the end of response
    ### **Response Format:**
    <h2>[Creative Heading]</h2>
    <ul>
        <li><strong>Property Types:</strong> [Breakdown of property supply and key offerings (25 words)]</li>
        <li><strong>Price Trends:</strong> [Insights into price per sq. ft. in nearby localities (25 words)]</li>
        <li><strong>BHK Distribution:</strong> [Popular configurations and their market share (25 words)]</li>
        <li><strong>Price Range:</strong> [Buyer preferences across different budget segments (25 words)]</li>
    </ul> 
    """
    real_estate_data = {"supply_demand_data": supply_demand_data, "nearby_localities": nearby_localities}
    response_sections.append(create_content_locality_description(real_estate_prompt, real_estate_data))

    # 4. Lifestyle & Amenities
    st.write("Generating Lifestyle & Amenities...")
    lifestyle_prompt = f"""
    Using the provided JSON data, generate a detailed and engaging "Lifestyle & Amenities" section for {locality}, {city}. 
    ### **Guidelines:**
    - Highlight premium lifestyle offerings, including top residential and commercial developments.
    - Use `indices_data.livability.facilities.Education` for schools.
    - Use `indices_data.livability.facilities.Healthcare` for hospitals.
    - Use `indices_data.lifestyle.facilities.Shopping` for shopping centers.
    - Use `indices_data.lifestyle.facilities.Entertainment` for recreational and fitness options.
     - Dont write any additional line beyond the response format at the end of response
    ### **Response Format:**
    <h2>[Creative Heading]</h2>
    <ul>
        <li><strong>Educational Institutions:</strong> [20 words]</li>
        <li><strong>Healthcare Facilities:</strong> [20 words]</li>
        <li><strong>Recreational & Shopping Centers:</strong> [20 words]</li>
        <li><strong>Green Spaces & Sports Facilities:</strong> [20 words]</li>
    </ul>
    """
    lifestyle_data = {"indices_data": indices_data, "connecting_roads": connecting_roads}
    response_sections.append(create_content_locality_description(lifestyle_prompt, lifestyle_data))

    # 5. Nearby Localities & Their Impact
    st.write("Generating Nearby Localities & Their Impact...")
    nearby_prompt = f"""
    Using the provided JSON data, generate a detailed and structured "Nearby Localities & Their Impact" section for {locality}, {city}. 
    ### **Guidelines:**
    - Use `nearby_localities` to extract details such as distances and `avg_price_per_sqft`.
    - Highlight how each locality influences {locality}, focusing on property pricing, rental demand, and luxury housing.
    - i just want nearby 4-5 points
    - Dont write any additional line beyond the response format at the end of response
    ### **Response Format:**
    <h2>[Creative Heading]</h2>
    <ul>
        <li><strong>[Nearby Locality Name] ([Distance]):</strong> [Impact on {locality}, including price trends, rental demand, and market position (25 words)]</li>
        <li><strong>[Nearby Locality Name] ([Distance]):</strong> [Impact on {locality}, including price trends, rental demand, and market position (25 words)]</li>
        <li><strong>[Nearby Locality Name] ([Distance]):</strong> [Impact on {locality}, including price trends, rental demand, and market position (25 words)]</li>
    </ul>
    """
    nearby_data = {"nearby_localities": top_five_localities}
    # print(nearby_data)
    response_sections.append(create_content_locality_description(nearby_prompt, nearby_data))

    # 6. Why Invest
    st.write("Generating Why Invest section...")
    investment_prompt = f"""
    Using the provided JSON data, generate a compelling "Why Invest in {locality}?" section for {locality}, {city}. 
    ### **Guidelines:**
    - Use `supply_demand_data.sale.property_types` to highlight the demand for builder floors and apartments.
    - Leverage `connecting_roads` to emphasize proximity to business hubs and its impact on rental yields.
    - Make logical assumptions about upcoming developments based on infrastructure growth trends.
    - Focus on investment potential, rental appreciation, and future property value growth.
     - Dont write any additional line beyond the response format at the end of response
    ### **Response Format:**
    <h2>[Creative Heading]</h2>
    <ul>
        <li><strong>Strong Demand:</strong> [Highlight high demand for specific property types and its impact on investment potential (25 words)]</li>
        <li><strong>Proximity to Business Hubs:</strong> [Explain connectivity advantages and their role in rental appreciation (25 words)]</li>
        <li><strong>Future Growth Potential:</strong> [Discuss ongoing/upcoming developments and their expected impact on property values (25 words)]</li>
    </ul>
    """
    investment_data = {"supply_demand_data": supply_demand_data, "connecting_roads": connecting_roads}
    response_sections.append(create_content_locality_description(investment_prompt, investment_data))

    # 7. People Also Ask (PAA)
    st.write("Generating People Also Ask section...")
    paa_prompt = f"""
    Using the provided JSON data, generate a structured "People Also Ask (PAA)" section for {locality}, {city}. 
    ### **Guidelines:**
    - Use `indices_data.connectivity` to describe connectivity and transport options.
    - Utilize `indices_data.livability` for insights on schools, hospitals, and amenities.
    - Leverage `indices_data.education` and `indices_data.health` for detailed educational and healthcare information.
    - Ensure answers are informative, concise, and relevant to potential homebuyers.
     - Dont write any additional line beyond the response format at the end of response
    ### **Response Format:**
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
    response_sections.append(create_content_locality_description(paa_prompt, paa_data))

    # Combine sections
    final_response = "\n\n".join(response_sections).replace("\n", "")
    return final_response

# Streamlit UI
st.title("Locality Description Generator")
st.write("Enter the city and locality to generate a detailed description.")

# Input fields
city = st.text_input("City", "")
locality = st.text_input("Locality", "")

# Button to generate description
if st.button("Generate Description"):
    if city and locality:
        with st.spinner("Generating..."):
            result = generate_locality_description(city, locality)
            st.markdown(result, unsafe_allow_html=True)
    else:
        st.warning("Please enter both city and locality.")

# Footer
# st.write("Powered by  | Date: March 11, 2025")A