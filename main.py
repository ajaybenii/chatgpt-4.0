#!/usr/bin/python
from dotenv import load_dotenv
import logging
import os
import openai
import re
import ast
import requests
import json



from typing import List, Optional
from groq import Groq
from fastapi import FastAPI
from pydantic import BaseModel, validator
from fastapi import FastAPI, HTTPException


from urllib.parse import urlparse
from fastapi.responses import PlainTextResponse,HTMLResponse,JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from prompts import Lifestyle_index_prompt, Liveability_index_prompt, Connectivity_index_prompt, Education_and_health_prompt
from models.property_types import (
    CommercialListingDataupdated,
    LandListingDataupdated,
    OfficeSpaceListingDataupdated,
    ResidentialListingDataupdated,
    LandListingData,
    OfficeSpaceListingData,
    CommercialListingData,
    PayingGuestListingData,
    request_body
)

app = FastAPI(
    title="Minite GPT3",
    description="Generates description for real estate listings from the listing parameters",
    version="2.0.0"
)

origins = [
    "https://ai.propvr.tech",
    "http://ai.propvr.tech",
    "https://ai.propvr.tech/classify",
    "http://ai.propvr.tech/classify",
    "https://uatapp.smartagent.ae",
    "https://app.smartagent.ae",
    "http://localhost:8080",
    "http://localhost:8081"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item2(BaseModel):

    ProjectName : str
    PrimarySubLocation : str
    PrimaryLocation : str
    CountryName : str
    CityName : str
    LowCost : int
    HighCost : int
    ProjectStatusDesc : str
    TowerCount : int
    WOWFactor : str
    ProjectClassName : str
    ProjectMinSize : int
    ProjectMaxSize : int
    ProjectReras : str
    UnitBHKOptions : str
    UnitCatOptions : str
    ProjectArea : str
    TotalUnits: str

class project_body(BaseModel):
    property_type: str #apartment, plot, commercial, studio_apartments, independent_floors, penthouse, villa ----------------------
    project_name: str
    location: str
    overview: str
    key_amenities: str
    key_features: str
    floor_plan: str 
    plot_detail: str
    project_detail: str
    properties_for_sale: str
    properties_for_rent: str
    project_location_and_advantages: str
    locality_snapshot: str
    launch_date: str
    possession: str
    avg_resale_price: str
    property_key_specification: str
    why_invest: str

class project_faq(BaseModel):
    
    ProjectName : str
    PrimarySubLocation : str
    PrimaryLocation : str
    CountryName : str
    CityName : str
    LowCost : int
    HighCost : int
    ProjectStatusDesc : str
    WOWFactor : str
    ProjectClassName : str
    ProjectMinSize : int
    ProjectMaxSize : int
    ProjectReras : str
    UnitBHKOptions : str
    UnitCatOptions : str
    ProjectArea : str
    TotalUnits: str
    Brochure : str

class request_body1(BaseModel):
    agency_name: str
    location: str

# loading environment variables from .env file
load_dotenv()

# OPENAI_DEPLOYMENT_NAME = 'sqy-gpt-35-turbo'
openai.api_type = "azure"
openai.api_key = os.getenv('openai.api_key')
openai.api_base = 'https://sqy-openai.openai.azure.com/'
openai.api_version = "2023-05-15"

groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key is None:
    raise ValueError("API key not found. Set the GROQ_API_KEY environment variable.")

client = Groq(api_key=groq_api_key)

def format_description(description):
    """
    Breaks descriptions into sentences and the creates format with first paragraph,
    body (bullet points array) and last paragraph
    """
    description  =str(description)
    description = description.replace("'","")
    description = description.replace("?",". ")
    description = description.replace(";"," ")
    description = description.replace("Rs.","INR")
    description = description.replace("sq.ft","sqft")
    description = description.replace("sq.","sq")
    description = description.replace("sqft.","sqft")
    description = description.replace("sq.ft.","square feet")
    
    sentences = list(map(str.strip, description.split('. ')[:-1]))
    sentences = [f'{sentence}.' for sentence in sentences]
    
    formatted_description = {
        'first_paragraph': sentences[0],
        'body': sentences[1:-1],
        'last_paragraph': sentences[-1]
    }
    
    print(formatted_description)
    return formatted_description


command = "You are a Square Yards specialised content writer and designer who focuses on providing real-estate based information. Your job is to write descriptions for listing from the pointers provided. Make sure all the details mentioned have to be appended as it is or exactly same. If price is prvided, you should write price like that 50 lakh, 3.20 crore or 25 thousand in article you genrate. The description should be SEO friendly, interactive to user and should not have name of any real estate organisation. First few words of description is unique and the article should be useful for home buyers or tenants based on the described details. You also have to make sure that all the values given are used in description atleast once."
command_dubai = "You are a Square Yards specialised content writer and designer who focuses on providing real-estate based information. Your job is to write a just 10 - 12 line of descriptions for listing from the pointers provided. Make sure all the details mentioned have to be appended as it is or exactly same. If price is prvided, you should write price like that 50 lakh, 3.20 crore or 25 thousand in article you genrate. The description should be SEO friendly, interactive to user and should not have name of any real estate organisation. First few words of description is unique and the article should be useful for home buyers or tenants based on the described details. You also have to make sure that all the values given are used in description atleast once."


@app.get("/")
async def root():
    return "Hello World!!!"


@app.post('/payingguest_descriptions')
async def generate_payingguest_description(payingguest_listing_data: PayingGuestListingData, format: bool = False):
    """
    Generates descriptions for residential property types
    """
    req_body = jsonable_encoder(payingguest_listing_data)
    # if len(payingguest_listing_data.locality) and len(payingguest_listing_data.city) >= 2 :
    
    #prepare data for input value 
    req_body1 = str(req_body).replace("'",'')
    req_body2 = str(req_body1).replace("{",'')
    req_body3 = str(req_body2).replace("}",'')

    
    completion = openai.ChatCompletion.create(
        deployment_id="sqy-gpt-35-turbo",
        model="gpt-3.5-turbo",
        temperature = 1.3,
        messages=[
            {"role": "system", "content": command},
            {"role": "user", "content": str(req_body3)}
        ]
        )

    get_content = dict(completion.choices[0].message)
    result = (str(get_content['content']))     
    final_result1= result.replace("\n",'')
    description = re.sub(r"[\([{})\]]", "", final_result1)
    
    return format_description(description)      


@app.post("/residential_descriptions")
async def generate_apartment_des_finetune1(fine_tune_apartment: request_body, format: bool = False):
    """
    Generates descriptions for Apartment property types
    """
    req_body = jsonable_encoder(fine_tune_apartment)
    if len(fine_tune_apartment.locality) and len(fine_tune_apartment.city) >= 2:
        #prepare data for input value 
        req_body1 = str(req_body).replace("'",'')
        req_body2 = str(req_body1).replace("{",'')
        req_body3 = str(req_body2).replace("}",'')

        completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt-35-turbo",
            model="gpt-3.5-turbo",
            temperature = 1.3,
            messages=[
                {"role": "system", "content": command },
                {"role": "user", "content": str(req_body3)}
            ]
            )

        get_content = dict(completion.choices[0].message)
        result = (str(get_content['content']))  

        final_result1= result.replace("\n",'')
        description = re.sub(r"[\([{})\]]", "", final_result1)
        

        return format_description(description)      
    
    else:
        return("Error please fill city and locality")

@app.post('/land_descriptions')
async def land_description(land_listing_data: LandListingData, format: bool = False):
    """
    Generates descriptions for land property types
    """
    
    req_body = jsonable_encoder(land_listing_data)
    if len(land_listing_data.locality) and len(land_listing_data.city) >= 2:
        #prepare data for input value 
        req_body1 = str(req_body).replace("'",'')
        req_body2 = str(req_body1).replace("{",'')
        req_body3 = str(req_body2).replace("}",'')

        completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt-35-turbo",
            model="gpt-3.5-turbo",
            temperature = 1.3,
            messages=[
                {"role": "system", "content": "You are a real-estate marketing creative. Your job is to write a good helpful details about localities of land or plot on pointers provided.Your main focus is on Price, If price is available then you should write price in words not in numbers. The content should be SEO-friendly should be engaging for the reader and should arouse their interest in browsing through the website. First line of every description should be unique. The article should be useful for home buyers and people looking to rent out properties in that area."},
                {"role": "user", "content": str(req_body3)}
            ]
            )

        get_content = dict(completion.choices[0].message)
        result = (str(get_content['content']))     
        final_result1= result.replace("\n",'')
        description = re.sub(r"[\([{})\]]", "", final_result1)
    
        
        return format_description(description)      
    
    else:
        return("Error please fill city and locality")


@app.post('/office_space_descriptions')
async def office_space_description(office_space_data: OfficeSpaceListingData, format: bool = False):
    """
    Generates descriptions for office space property types
    """

    req_body = jsonable_encoder(office_space_data)
    if len(office_space_data.locality) and len(office_space_data.city) >= 2:
        #prepare data for input value 
        req_body1 = str(req_body).replace("'",'')
        req_body2 = str(req_body1).replace("{",'')
        req_body3 = str(req_body2).replace("}",'')

        completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt-35-turbo",
            model="gpt-3.5-turbo",
            temperature = 1.3,
            messages=[
                {"role": "system", "content": command},
                {"role": "user", "content": str(req_body3)}
            ]
            )
        
        get_content = dict(completion.choices[0].message)
        result = (str(get_content['content']))     
        final_result1= result.replace("\n",'')

        description = re.sub(r"[\([{})\]]", "", final_result1)
       
        
        return format_description(description)      
    
    else:
        return("Error please fill city and locality")


@app.post('/commercial_descriptions')
async def generate_land_description(commercial_listing_data: CommercialListingData, format: bool = False):
    """
    Generates descriptions for commercial property types
    """   
    req_body = jsonable_encoder(commercial_listing_data)
    if len(commercial_listing_data.locality) and len(commercial_listing_data.city) >= 2:
        #prepare data for input value 
        req_body1 = str(req_body).replace("'",'')
        req_body2 = str(req_body1).replace("{",'')
        req_body3 = str(req_body2).replace("}",'')
       
        completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt-35-turbo",
            model="gpt-3.5-turbo",
            temperature = 1.3,
            messages=[
                {"role": "system", "content": command},
                {"role": "user", "content": str(req_body3)}
            ]
            )

        get_content = dict(completion.choices[0].message)
        result = (str(get_content['content']))     
        final_result1= result.replace("\n",'')

        description = re.sub(r"[\([{})\]]", "", final_result1)
        
        
        return format_description(description)    
    
    else:
        return("Error please fill city and locality")


@app.post('/residential_descriptions_dubai')
async def generate_apartment_description_dubai(residential_listing_data: ResidentialListingDataupdated, format: bool = False):
    """
    Generates descriptions for residential property types
    """ 
    
    req_body = jsonable_encoder(residential_listing_data)
    if len(residential_listing_data.locality) and len(residential_listing_data.city) >= 2 and residential_listing_data.price != 0:
        
        #prepare data for input value 
        req_body1 = str(req_body).replace("'",'')
        req_body2 = str(req_body1).replace("{",'')
        req_body3 = str(req_body2).replace("}",'')

        completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt-35-turbo",
            model="gpt-3.5-turbo",
            temperature = 1.3, 
            messages=[
                {"role": "system", "content": command},
                {"role": "user", "content": str(req_body3)}
            ]
            )


        get_content = dict(completion.choices[0].message)
        result = (str(get_content['content']))     
        final_result1= result.replace("\n",'')

        description = re.sub(r"[\([{})\]]", "", final_result1)
     
        
        return format_description(description)

    else:
        return("Error please fill city and locality and price")


@app.post('/land_descriptions_dubai')
async def land_description_dubai(land_listing_data: LandListingDataupdated, format: bool = False):
    """
    Generates descriptions for land property types
    """
    req_body = jsonable_encoder(land_listing_data)
    if len(land_listing_data.locality) and len(land_listing_data.city) >= 2 and land_listing_data.price != 0:
        #prepare data for input value 
        req_body1 = str(req_body).replace("'",'')
        req_body2 = str(req_body1).replace("{",'')
        req_body3 = str(req_body2).replace("}",'')
       
        completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt-35-turbo",
            model="gpt-3.5-turbo",
            temperature = 1.3,
            messages=[
                {"role": "system", "content": command},
                {"role": "user", "content": str(req_body3)}
            ]
            )


        get_content = dict(completion.choices[0].message)
        result = (str(get_content['content']))     
        final_result1= result.replace("\n",'')

        description = re.sub(r"[\([{})\]]", "", final_result1)

        
        return format_description(description)      
        
    else:
        return("Error please fill city and locality")

    
@app.post('/office_space_descriptions_dubai')
async def office_space_description_dubai(office_space_data: OfficeSpaceListingDataupdated, format: bool = False):
    """
    Generates descriptions for office space property types
    """
    req_body = jsonable_encoder(office_space_data)
    if len(office_space_data.locality) and len(office_space_data.city) >=2 and office_space_data.price != 0:
        #prepare data for input value 
        req_body1 = str(req_body).replace("'",'')
        req_body2 = str(req_body1).replace("{",'')
        req_body3 = str(req_body2).replace("}",'')

        completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt-35-turbo",
            model="gpt-3.5-turbo",
            temperature = 1.3,
            messages=[
                {"role": "system", "content": command},
                {"role": "user", "content": str(req_body3)}
            ]
            )

        get_content = dict(completion.choices[0].message)
        result = (str(get_content['content']))     
        final_result1= result.replace("\n",'')

        description = re.sub(r"[\([{})\]]", "", final_result1)
        
        return format_description(description)      
        
    else:
        return("Error please fill city and locality")

    
@app.post('/commercial_descriptions_dubai')
async def generate_land_description_dubai(commercial_listing_data: CommercialListingDataupdated, format: bool = False):
    """
    Generates descriptions for commercial property types
    """
    #prepare data for input value 
    req_body = jsonable_encoder(commercial_listing_data)
    if len(commercial_listing_data.locality) and len(commercial_listing_data.city) >=2 and commercial_listing_data.price != 0:
        
        req_body1 = str(req_body).replace("'",'')
        req_body2 = str(req_body1).replace("{",'')
        req_body3 = str(req_body2).replace("}",'')

        completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt-35-turbo",
            model="gpt-3.5-turbo",
            temperature = 1.3,
            messages=[
                {"role": "system", "content": command},
                {"role": "user", "content": str(req_body3)}
            ]
            )

        get_content = dict(completion.choices[0].message)
        result = (str(get_content['content']))     
        final_result1= result.replace("\n",'')

        description = re.sub(r"[\([{})\]]", "", final_result1)
        
        return format_description(description)
    
    else:
        return("Error please fill city and locality")


#dubai agency description api on live
@app.post("/dubai_agency_description")
async def dubai_agency_description(data: request_body1):
    """
    Api to generate Dubai-agency description

    Request body format

        {
        "agency_name": "Dacha Real Estate ",
        "location": "Downtown, Dubai"
        }

    """

    req_body = jsonable_encoder(data)

    #prepare data for input value 
    req_body1 = str(req_body).replace("'",'')
    req_body2 = str(req_body1).replace("{",'')
    req_body3 = str(req_body2).replace("}",'')

    
    completion = openai.ChatCompletion.create(
        deployment_id="sqy-gpt-35-turbo",
        model="gpt-3.5-turbo",
        temperature = 1.3,
        messages=[
            {"role": "system", "content": "You are dubai agent,i will gave you two things agency name and location on the basis of these two things you will genrate ae description like this (Providential Properties Management is a full-service real estate company that specializes in the management and sale of residential and commercial properties in the UAE. We offer our clients a wide range of services, including property management, marketing, and leasing. We also have a team of experienced professionals who are dedicated to providing the best possible service to our clients. We take pride in our reputation for providing quality real estate services at a fair price.)"},
            {"role": "user", "content": str(req_body3)}
        ]
        )

    get_content = dict(completion.choices[0].message)
    result = (str(get_content['content']))     
    final_result1= result.replace("\n",'')
    description = re.sub(r"[\([{})\]]", "", final_result1)
    
    return {"description":description}


# Data provided
sample_data = {
    "overview": "Godrej Horizon Wadala offers a perfect blend of comfort and luxury in apartment living. Situated in the vibrant neighborhood of Wadala, Mumbai, this project features 470 units with spacious 1 BHK, 2 BHK, and 3 BHK apartments ranging from 435 sq. ft. to 1000 sq. ft. The project was launched in May 2020 and spans across 5 acres of lush green landscape. With best-in-class resorts, proposed IT park, and the International Airport in close proximity, Godrej Horizon Wadala ensures you have everything you need right at your doorstep.",
    "key_amenities": "Experience a host of essential amenities at Godrej Horizon Wadala, including Rain Water Harvesting, Sewage Treatment Plant, and a serene Central Green area, creating a harmonious and eco-friendly environment for the residents.",
    "key_features": "The project incorporates state-of-the-art technology with features like Intelligent Master Command for all Smart Appliances, Intelligent Biometric Security, Smart Lighting & Cooling, 24X7 Remote Connectivity, and Fibre Optic Infrastructure, providing you with the convenience and safety you deserve.",
    "floor_plan": "The thoughtfully designed floor plan includes 470 units of 1 BHK, 2 BHK, and 3 BHK apartments sprawled across 5 acres, ensuring ample space and comfortable living for all residents. The apartments range from 435 sq. ft. to 1000 sq. ft., catering to various family sizes and preferences.",
    "properties_for_sale": "For those seeking to own their dream home, Godrej Horizon Wadala offers exquisite properties for sale. Choose from a variety of options, including 1 BHK, 2 BHK, and 3 BHK apartments ranging from 435 sq. ft. to 1000 sq. ft., and make the perfect investment for your future.",
    "properties_for_rent": "If you prefer a more flexible living arrangement, the property also has apartments available for rent. Experience the comforts of home with the flexibility of renting, as the project offers 1 BHK, 2 BHK, and 3 BHK apartments ranging from 435 sq. ft. to 1000 sq. ft.",
    "project_location_and_advantages": "Strategically located in Vikhroli West, Mumbai, Godrej Horizon Wadala is easily accessible from the Western Express Highway and Eastern Express Highway, connected via a 10.6 km six-lane road. The project's advantageous location provides quick access to major business hubs like BKC, Godrej Business District, and Hiranandani Business Park. With close proximity to JVLR, residents can enjoy seamless connectivity to the rest of the city.",
    "locality_snapshot": "Situated in the bustling locality of Wadala, Mumbai, Godrej Horizon Wadala offers a snapshot of a vibrant and thriving community. The area boasts excellent social infrastructure, including schools, hospitals, shopping centers, and various entertainment options, making it an ideal place to call home.",
    "launch_date": "Anticipated to be launched in April 2024, Godrej Horizon Wadala is all set to redefine urban living with its modern amenities and premium lifestyle.",
    "avg_resale_price": "With an average resale price ranging from 1 crore to 15 crores, investing in Godrej Horizon Wadala offers a promising return on investment and an opportunity to be a part of a thriving community.",
    "property_key_specification": "Lakeview apartments include a power backup, 24*7 CCTV security system, power backup, 24*7 water supply, normal park, central park,Oil bound distemper on the master bedroom walls and flooring with vitrified tiles.The frame structure that is used to construct the project is RCC.The amenities that are included in this project are a 24*7 security system, power backup, 24*7 water supply, normal park, central park, indoor games, kid’s play area, and lift.",
    "why_invest": "Invest in premium office spaces tailored to meet your business needs on a 1 lac sq. ft. property."
}

command_page_conntent = f'i want long descriptions like i will give you as a sample and i want response in this format same as it is{sample_data},so using my data which i provide to you please genrate description in details like this {sample_data} without any syntax error Please provide a JSON response with the enclosed in double quotes:'

@app.post("/page-content")
async def create_page_content1(data: project_body):
    """
    Get the listing content for a particular configuration
    
    Request body example

        {
        "property_type": "apartment",
        "project_name": "Godrej Horizon Wadala",
        "location": "Wadala,Mumbai",
        "overview": "launched on May 2020, 470 units, 5 Acres, 1 BHK-2 BHK-3 BHK, 435 Sq. Ft. to 1000 Sq. Ft., best-in-class resorts, proposed IT park International Airport,you stay close to everything you need",
        "key_amenities": "Rain Water Harvesting, Sewage Treatment Plant, Normal Park / Central Green",
        "key_features": "Intelligent Master Command for all Smart Appliances, Intelligent Biometric Security, Smart Lighting & Cooling, 24X7 Remote Connectivity, Fibre Optic Infrastructure and much more",
        "floor_plan": "470 units, 5 Acres, 1 BHK-2 BHK-3 BHK, 435 Sq. Ft. to 1000 Sq. Ft.",
        "plot_detail": "1200 sq. ft. , 1500 sq. ft. and 2400 sq. ft",
        "project_detail": "1600 sqft to 1700 sqft",
        "properties_for_sale": "1 BHK-2 BHK-3 BHK, 435 Sq. Ft. to 1000 Sq. Ft.",
        "properties_for_rent": "1 BHK-2 BHK-3 BHK, 435 Sq. Ft. to 1000 Sq. Ft.",
        "project_location_and_advantages": "stands elegantly at Mumbai Central suburbs in Vikroli West, linked to Western Express Highway & Easter Express Highway by a 10.6 km six-lane road, close proximity to JVLR while the BKC is 30 mins away, Godrej Business district & Hiranandani Business Park",
        "locality_snapshot": "Wadala,Mumbai",
        "launch_date": "april 2024",
        "possession": "may 2026",
        "avg_resale_price": "1cr to 15cr",
        "property_key_specification": "Glazed Vitrified tile flooring in all rooms and kitchen, Anti-skid vitrified tiles in toilet flooring, Silent chimney, Granite kitchen platform, stainless steel sink",
        "why_invest": "Spread over approximately 1 lac sq.ft. this multi-storey structure of premium offices ranging in sizes based on your business needs"
        }

    """
    req_body = jsonable_encoder(data)
    req_body1 = str(req_body).replace("'",'')
    req_body2 = str(req_body1).replace("{",'')
    req_body3 = str(req_body2).replace("}",'')

    try:
        completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt-35-turbo",
            model="gpt-3.5-turbo",
            temperature=1.3,
            messages=[
                {"role": "system", "content": command_page_conntent},
                {"role": "user", "content": str(req_body3)}
            ]
        )
        get_content = dict(completion.choices[0].message)
        result = get_content['content']

    except Exception as e:    
        return {"error": f"Error in OpenAI API call: {str(e)}"}
   
    data = eval(result)
    print(data)
    if data["overview"]:

        overview = str(data["overview"]).replace("'","")
        print("if working of overview")

    else:
        try:
            print("else working of overview")
            completion = openai.ChatCompletion.create(
                deployment_id="sqy-gpt-35-turbo",
                model="gpt-3.5-turbo",
                temperature = 1.3,
                messages=[
                    {"role": "system", "content": "i will gave you data, on the basis of data, genrate 7 to 8 line of description about only overview of given data of project"},
                    {"role": "user", "content": str(req_body3)}
                ]
                )
            get_content = dict(completion.choices[0].message)
            # (get_content)
            result = str(get_content['content'])

            overview = str(result).replace("'","")
        except:
            overview = ""

    if data["key_amenities"]:
         key_amenities = str(data["key_amenities"]).replace("'","")
        #  key_amenities = key_amenities.replace(";","")
        #  key_amenities = key_amenities.replace("?","")
        #  key_amenities = re.sub(r"[\([{})\]]","", key_amenities)
         print("if working of key_amenities")
    
    else:
        try:
            print("else working of key amenities")
            completion = openai.ChatCompletion.create(
                deployment_id="sqy-gpt-35-turbo",
                model="gpt-3.5-turbo",
                temperature = 1.3,
                messages=[
                    {"role": "system", "content": "i will gave you data, on the basis of data, genrate a 5 to 6 line of description about only key amenities of given data of project"},
                    {"role": "user", "content": str(req_body3)}
                ]
                )
            get_content = dict(completion.choices[0].message)
            # (get_content)
            result = str(get_content['content'])
            key_amenities = str(result).replace("'","")

        except:
            key_amenities =""
    

    if data["key_features"]:

        key_features = str(data["key_features"]).replace("'","")
        # key_features = key_features.replace(";","")
        # key_features = key_features.replace("?","")
        # key_features = re.sub(r"[\([{})\]]","", key_features)
        
        print("if working of key features")
    else:
        try:
            print("else working of key features")
            completion = openai.ChatCompletion.create(
                deployment_id="sqy-gpt-35-turbo",
                model="gpt-3.5-turbo",
                temperature = 1.3,
                messages=[
                    {"role": "system", "content": "i will gave you data, on the basis of data, genrate 6 to 7 line of description about only key features of given data of project"},
                    {"role": "user", "content": str(req_body3)}
                ]
                )
            get_content = dict(completion.choices[0].message)
            # (get_content)
            result = str(get_content['content'])
            key_features = str(result).replace("'","")

        except:
            key_features = ""


    if data["floor_plan"]:     
        floor_plan = str(data["floor_plan"]).replace("'","")
        # floor_plan = floor_plan.replace(";","")
        # floor_plan = floor_plan.replace("?","")
        # floor_plan = re.sub(r"[\([{})\]]","", floor_plan)
        print("if working of floor plan")
    else:
        try:
            completion = openai.ChatCompletion.create(
                deployment_id="sqy-gpt-35-turbo",
                model="gpt-3.5-turbo",
                temperature = 1.3,
                messages=[
                    {"role": "system", "content": "i will gave you data, on the basis of data, genrate a 6 to 7 line description about only floor plan of given data of project"},
                    {"role": "user", "content": str(req_body3)}
                ]
                )
            get_content = dict(completion.choices[0].message)
            # (get_content)
            result = str(get_content['content'])
            floor_plan = str(result).replace("'","")

        except:
            floor_plan = ""

    if data["properties_for_sale"]:
        properties_for_sale = str(data["properties_for_sale"]).replace("'","")
        # properties_for_sale = properties_for_sale.replace(";","")
        # properties_for_sale = properties_for_sale.replace("?","")
        # properties_for_sale = re.sub(r"[\([{})\]]","", properties_for_sale)
        print("if working of properties for sale")
    else:
        try:
            # else:
            completion = openai.ChatCompletion.create(
                deployment_id="sqy-gpt-35-turbo",
                model="gpt-3.5-turbo",
                temperature = 1.3,
                messages=[
                    {"role": "system", "content": "i will gave you data, on the basis of data, genrate 6 to 7 line description about only properties for sale of given data of project"},
                    {"role": "user", "content": str(req_body3)}
                ]
                )
            get_content = dict(completion.choices[0].message)
            # (get_content)
            result = str(get_content['content'])
            properties_for_sale = str(result).replace("'","")

        except :
            properties_for_sale = ""

    if data["properties_for_rent"]:
        properties_for_rent = str(data["properties_for_rent"]).replace("'","")
        # properties_for_rent = properties_for_rent.replace(";","")
        # properties_for_rent = properties_for_rent.replace("?","")
        # properties_for_rent = re.sub(r"[\([{})\]]","", properties_for_rent)
        print("if working of properites for rent")
    else:
        try:
            print("else working of properites for rent")
            completion = openai.ChatCompletion.create(
                deployment_id="sqy-gpt-35-turbo",
                model="gpt-3.5-turbo",
                temperature = 1.3,
                messages=[
                    {"role": "system", "content": "i will gave you data, on the basis of data, genrate 6 to 7 line description about only properties for rent of given data of project"},
                    {"role": "user", "content": str(req_body3)}
                ]
                )
            get_content = dict(completion.choices[0].message)
            # (get_content)
            result = str(get_content['content'])
            properties_for_rent = str(result).replace("'","")  
        except:
            properties_for_rent = ""


    if data["project_location_and_advantages"]:         
        project_location_and_advantages = str(data["project_location_and_advantages"]).replace("'","")
        # project_location_and_advantages = project_location_and_advantages.replace(";","")
        # project_location_and_advantages = project_location_and_advantages.replace("?","")
        # project_location_and_advantages = re.sub(r"[\([{})\]]","", project_location_and_advantages)
        print("if working of project location and advantages")
    else:
        try:          
            print("else working of project location and advantages")
            completion = openai.ChatCompletion.create(
                deployment_id="sqy-gpt-35-turbo",
                model="gpt-3.5-turbo",
                temperature = 1.3,
                messages=[
                    {"role": "system", "content": "i will gave you data, on the basis of data, genrate 6 to 7 line description about only project location and advantages of given data of project"},
                    {"role": "user", "content": str(req_body3)}
                ]
                )
            get_content = dict(completion.choices[0].message)
            # (get_content)
            result = str(get_content['content'])
            project_location_and_advantages = str(result).replace("'","")

        except:
            project_location_and_advantages = ""


    if data["locality_snapshot"]:
        locality_snapshot = str(data["locality_snapshot"]).replace("'","")
        # locality_snapshot = locality_snapshot.replace(";","")
        # locality_snapshot = locality_snapshot.replace("?","")
        # locality_snapshot = re.sub(r"[\([{})\]]","", locality_snapshot)
        print("if working of locality snapshot")
    else:
            completion = openai.ChatCompletion.create(
                deployment_id="sqy-gpt-35-turbo",
                model="gpt-3.5-turbo",
                temperature = 1.3,
                messages=[
                    {"role": "system", "content": "i will gave you data, on the basis of data, genrate 6 to 7 line description about only project locality snapshot of given data of project"},
                    {"role": "user", "content": str(req_body3)}
                ]
                )
            get_content = dict(completion.choices[0].message)
            # (get_content)
            result = str(get_content['content'])
            locality_snapshot = str(result).replace("'","")


    if data["launch_date"]:
                   
        launch_date = str(data["launch_date"]).replace("'","")
        # launch_date = launch_date.replace(";","")
        # launch_date = launch_date.replace("?","")
        # launch_date = re.sub(r"[\([{})\]]","", launch_date)
        
        print("if working of launch date")
    else:
        try:
            print("else working of launch date")
            completion = openai.ChatCompletion.create(
                deployment_id="sqy-gpt-35-turbo",
                model="gpt-3.5-turbo",
                temperature = 1.3,
                messages=[
                    {"role": "system", "content": "if launch date is available then genrate 4 to 5 line description about launch date otherwise give blank response."},
                    {"role": "user", "content": str(req_body3)}
                ]
                )
            get_content = dict(completion.choices[0].message)
            # (get_content)
            result = str(get_content['content'])
            launch_date = str(result).replace("'","")

        except:
            launch_date = ""


    if data["avg_resale_price"]:             
        avg_resale_price = str(data["avg_resale_price"]).replace("'","")
        # avg_resale_price = avg_resale_price.replace(";","")
        # avg_resale_price = avg_resale_price.replace("?","")
        # avg_resale_price = re.sub(r"[\([{})\]]","", avg_resale_price)
        print("if working of avg resale price")
    else:
        try:
            print("else working of avg resale price")
            completion = openai.ChatCompletion.create(
                deployment_id="sqy-gpt-35-turbo",
                model="gpt-3.5-turbo",
                temperature = 1.3,
                messages=[
                    {"role": "system", "content": "i will gave you data, on the basis of data, genrate 5 to 6 line description about only average resale price of given data of project"},
                    {"role": "user", "content": str(req_body3)}
                ]
                )
            get_content = dict(completion.choices[0].message)
            # (get_content)
            result = str(get_content['content'])
            avg_resale_price = str(result).replace("'","")

        except :
            avg_resale_price = " "


    if data["property_key_specification"]:                 
        property_key_specification = str(data["property_key_specification"]).replace("'","")
        # property_key_specification = property_key_specification.replace(";","")
        # property_key_specification = property_key_specification.replace("?","")
        # property_key_specification = re.sub(r"[\([{})\]]","", property_key_specification)
        print("if working of property key specification")

    else:
        try:
            print("else working of property key specification")
            completion = openai.ChatCompletion.create(
                deployment_id="sqy-gpt-35-turbo",
                model="gpt-3.5-turbo",
                temperature = 1.3,
                messages=[
                    {"role": "system", "content": "i will gave you data, on the basis of data, genrate 6 to 7 line description about only property key specification of given data of project"},
                    {"role": "user", "content": str(req_body3)}
                ]
                )
            get_content = dict(completion.choices[0].message)
            # (get_content)
            result = str(get_content['content'])
            property_key_specification = str(result).replace("'","")

        except:
            property_key_specification = " "


    if data["why_invest"]:     
        why_invest= str(data["why_invest"]).replace("'","")
        # why_invest = why_invest.replace(";","")
        # why_invest = why_invest.replace("?","")
        # why_invest = re.sub(r"[\([{})\]]","", why_invest)

        print("if working of why_invest")
    else:
        try:
            print("else working of why_invest")
            completion = openai.ChatCompletion.create(
                deployment_id="sqy-gpt-35-turbo",
                model="gpt-3.5-turbo",
                temperature = 1.3,
                messages=[
                    {"role": "system", "content": "i will gave you data, on the basis of data, genrate 6 to 7 line description about only Why invest in this project"},
                    {"role": "user", "content": str(req_body3)}
                ]
                )
            get_content = dict(completion.choices[0].message)
            # (get_content)
            result = str(get_content['content'])
            why_invest = str(result).replace("'","")

        except:
            why_invest = ""

    return {"overview":overview,
            "key_amenities":key_amenities,
            "key_features":key_features,
            "floor_plan":floor_plan,
            "properties_for_sale":properties_for_sale,
            "properties_for_rent":properties_for_rent,
            "project_location_and_advantages":project_location_and_advantages,
            "locality_snapshot":locality_snapshot,
            "launch_date":launch_date,
            "avg_resale_price":avg_resale_price,
            "property_key_specification":property_key_specification,
            "why_invest":why_invest
            }

# Data provided
sample_data = {

    "Question_1": "Okay, I want to buy a home here. What are the documents I need to provide to complete the sale?",
    "Answer_1": "The list of documents required to confirm your booking is below; 1. Residence / Address proof (Aadhar Card Copy) 2. Identity proof 3. PAN card copy 4. Passport size photographs 5. Bank Attested Signature 6. Copy of Passport for NRI customers 7. Further details are available in the Application Form",
    "Question_2": "What kind of dwelling units does Emaar Palm Heights offer?",
    "Answer_2": "This project offers well designed residential units of type(s) Apartments. Feel free to explore options.",
    "Question_3": "What are the other projects & their construction status been undertaken by this developer?",
    "Answer_3": "To ensure your peace of mind, we only list projects from reputed and top rated developers here. In this case, Emaar is established since 2009. A list of their project(s) follows; 1. Emaar Commerce Park - delivered2. Emaar Capital Tower - delivered3. Emaar Marbella Phase 2 - delivered4. Emaar Emerald Nuevo - delivered",
    "Question_4": "Is there more to it? Special features perhaps?",
    "Answer_4": "Oh Yes. Here are some special features that will make you go WOW! 1. Dream lifestyle, exclusive space and immense luxury2. Every apartment is crammed with sun filled rooms, full ventilation, complete privacy and more3. Strategically located on the intersection of NH-8 and Dwarka Expressway4. Proposed metro station in vicinity5. Easy connectivity to IMT Manesar and IGI Airport6. The local area is filled with school, hospital, clinics, local market, restaurants and banks7. Convenient shopping centre for daily needs.",
    "Question_5": "So, where is Emaar Palm Heights exactly located?",
    "Answer_5": "Emaar Palm Heights is very conveniently located in New Gurgaon, Sector 77, in Gurgaon The major road(s) connecting this project are here; 1. NH 8 - 0.518 Km2. Dwarka Expressway - 1.5 Km"

}

Sample_question = {
"1. Is <Project Name> Rera approved?",
"2. Where to Get / Download <Project Name>'s Brochure?",
"3. What are the Key Features of <Project Name> <City>?",
"4. What is Good & Bad about <Project Name>?",
"5. Why Should I Invest in <Project Name> <City>?",
"6. Where is <Project Name> Located in <City>?",
"7. What are the Unit Sizes Available for Sale in <<Project Name>",
"8. Is <Project name> Ready for Possession or Delivered?",
"9. Are there any sports facility available in <Project Name>?",
"10. What is the Stamp Duty Changes / Registration Charges for this Project?",
"11. What is the name of the Real Estate Builder constructing this project?",
"12. What is price of 2/3 bhk in <Project Name>?"
    
}

# command = f'i want long descriptions like i will give you as a sample and i want response in this format same as it is{sample_data},so using  my data which i provide to you please genrate description in details like this {sample_data} without any syntax error and use double quotes insteaded of single.'
command_faq = f"i will gave you data, using that data you will genrate only 7 to 10 FAQs. I want FAQs in this format same as it is in this sample data ({sample_data}) and these type of questions is include in the FAQs ({Sample_question}) but i want response format like this ({sample_data}). I want reponse without any syntax error.Please provide a JSON response with the enclosed in double quotes"

@app.post("/project-FAQs")
async def create_project_FAQs(data: project_faq):

    req_body = jsonable_encoder(data)

    #prepare data for input value 
    req_body1 = str(req_body).replace("'",'')
    req_body2 = str(req_body1).replace("{",'')
    req_body3 = str(req_body2).replace("}",'')

    try:
        completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt-35-turbo",
            model="gpt-3.5-turbo",
            temperature = 1.3,
            messages=[
                {"role": "system", "content": command_faq},
                {"role": "user", "content": str(req_body3)}
            ]
            )

        get_content = dict(completion.choices[0].message)
        # (get_content)
        result = (get_content['content']) 
        # print(result)
    
    except Exception as e:    
        return {"error": f"Error in OpenAI API call: {str(e)}"}
         

    try:
        data = eval(result)
        print("try work")
    except:
        # return {"data":result}
    
        # result = "{'key1': 'value1', 'key2': 'value2'}"
        print("except work")
        data = ast.literal_eval(result)
        return data


    return data


ca_sample2 = """
<div class='main chatGPT'> <div class='heading'><strong>Welcome to 140 Widdicombe Hill Blvd</strong></div> <div class='para'> <p>Located in the Willowridge-Martingrove-Richview neighbourhood in Toronto, this property offers a great opportunity for those looking to purchase a home in this area.</p> </div> <div class='info'> <strong>Here are some key details about this property:</strong> <ul> <li>There are currently 2 listings available for sale in 140 Widdicombe Hill Blvd, with a price of $730,000 each.</li> <li>The exterior finish of this building is concrete, providing a modern and durable look.</li> <li>Each unit in property comes with an owned locker, offering additional storage space for your belongings.</li> <li>The laundry facilities in 140 Widdicombe Hill Blvd are ensuite and located on the main level, providing convenience and privacy.</li> <li>Enjoy the terrace in 140 Widdicombe Hill Blvd, perfect for relaxing and enjoying the outdoor space.</li> <li>High-speed internet is available in this building, ensuring you stay connected at all times.</li> <li>140 Widdicombe Hill Blvd also features an underground garage, providing secure parking for residents.</li> <li>Building insurance is included in 140 Widdicombe Hill Blvd, giving you peace of mind.</li> </ul> </div> </div>"""

ca_prompt2 = f"""
#Output response should be in HTML-format.
Generate real estate property descriptions for Canada without including any outside information. Follow strict instructions.

Instructions:

1.Do not include any information beyond the property description.
2.Ensure the descriptions are SEO-friendly, utilizing relevant keywords naturally.
3.Write the description in easy English.
4.Present the description in a clear and engaging format, similar to the example provided with bullet points for key details.
5.Avoid any reference to external sources or additional details beyond the property itself.
6.To generate description only use provide key value data, don't add additionl details in description response.
7.Do not include any concluding or call-to-action statements.


Like this format example :- {ca_sample2}

Above is just sample format, only generate that bullet points which data is given to you , don't add additionl points details in description response and don't write or mention any Note in the end of response.
"""

# response_class=PlainTextResponse
#dubai agency description api on live
@app.post("/ca_description")
async def project_description(data: str):
    """
    Api to generate Dubai-agency description

    Request body format

        {
        "building_Name": "str",
        "neighbourhood": "str",
        "municipality": "str"
        "area": "str",
        "PType": "str",
        "date": "str",
        "count_of_PType_Sale": "str",
        "count_of_PType_Rental": "str",
        "min_price_of_Sale_Listings": "str",
        "max_price_of_sale_Listings": "str",
        "bhk": "str",
        "min_price_of_Rent_Listings": "str",
        "min_price_of_rent_Listings": "str",
        "amenities": "str"
        }

    """
    req_body = jsonable_encoder(data)

    try:
        completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt-35-turbo-16k",
            model="sqy-text-embedding-ada-002",
            temperature=0.7,
            messages=[
                {"role": "system", "content": ca_prompt2},
                {"role": "user", "content": req_body}
            ]
        )

        get_content = completion.choices[0].message
        result = get_content['content']
        description = re.sub(r"[\([{})\]]", "", result)
        description = description.replace("\n","")
        description = description.replace("\n","")
        return {"description":description}
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    w

Canada_description_prompt2 = """
Generate a concise project description in two paragraphs based on the provided input data:

1. The first paragraph should introduce the project, mentioning its name, location, developer, architect, and key highlights like the number of buildings, total residential gross floor area, and total units.
2. The second paragraph should describe the neighborhood and nearby amenities, including schools and hospitals, specifying their names and types, in a professional and informative tone.

Ensure the response is formatted as:
<p>First paragraph content.</p>
<p>Second paragraph content.</p>
"""

@app.post("/ca_description2")
async def project_description(data: str):
    """
    Api to generate Dubai-project description
    """
    req_body = jsonable_encoder(data)

    try:
        completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt-35-turbo-16k",
            model="sqy-text-embedding-ada-002",
            temperature=0.7,
            messages=[
                {"role": "system", "content": Canada_description_prompt2},
                {"role": "user", "content": req_body}
            ]
        )

        get_content = completion.choices[0].message
        result = get_content['content']
        description = re.sub(r"[\([{})\]]", "", result)
        description = description.replace("\n","")
        description = description.replace("\n","")
        return {"description":description}
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
# Prompts
html_sample = """<p>
paragrapgh
</p>

<p>
paragrapgh
</p>

<p>
paragrapgh
</p>

<strong>Available Unit Options</strong>
<p>The following table outlines the available unit options at (Project name):</p>
<div class='tablesResponsive'>
  <table width='100%' border='1' cellspacing='0' cellpadding='5'>
    <tbody>
      <tr>
        <td>Unit Type</td>
        <td>Area (Sq. Ft.)</td>
        <td>Price (Rs.)</td>
      </tr>
      <tr>
        <td>Retail Shop</td>
        <td>183</td>
        <td>56.64 Lac</td>
      </tr>
      <tr>
        <td>Retail Shop</td>
        <td>728</td>
        <td>2.25 Cr</td>
      </tr>
    </tbody>
  </table>
</div>
"""

prompt = f"""
You are real-estate agent. I will give you details of a real-estate project. Your task is generate the project description that should be SEO-Friendly. The content should include the following sections:
- Using all provided details generate project description and description should be divided into 3 large paragraph's only and not more than 1-2 line about amenties and specifications in description.
- Generate a available unit option table. Ensure the prices are clearly labeled with 'Lac' or 'Cr' for clarity.")

Note :- Begin direct with description, don't write any line in starting of final response

this is the sample format, i want response in this format without any syntax error:-
{html_sample}

-Above sample is just format , dont use its value.
"""

prompt2 = """
I will give you details of a real-estate project. Your task is generate the project description that should be SEO-Friendly. The content should include the following sections:
-Using all provided details generate project description and description should be divided into 2-3 large paragraph's only.

Please ensure that:
- Dont Mention paragrapgh numbers.
- If some details are not available, omit those sections in the final response.
- Dont write any additional line in response.
- Ensure the format is error-free.

sample response format:- 
<p>
paragrapgh
</p>

<p>
paragrapgh
</p>

<p>
paragrapgh
</p>

-Above sample is just format , dont use its value.
"""

listing_table_prompt = """
I will provide you details of a real estate project listings information. Your task is to create section for listing table , first write something about listing table then make a table.
Ensure the table has a clean and structured layout.
- Dont write any additional line.
- If details not available dont mention about this.
- Table structured should be in well format without any syntax error

sample Format response:
<strong>Listing Information</strong> <p>We have total 44 options available in {project name} for resale and rental, In resale we have 17 properties available ranging from 2 BHK - 3 BHK having sizes from  1.47 CR - ₹ 3.10 CR </p> <p>For rent you can check 27 properties having options for 2 BHK - 3 BHK with price ranging from ₹ 40000 - ₹ 50000.</p> <div class="tablesResponsive"> <table width="100%" border="1" cellspacing="0" cellpadding="5"> <tbody> <tr> <td>Listing Type</td> <td>Total Listings</td> <td>Unit Type Range</td> <td>Price Range</td> </tr> <tr> <td>Resale</td> <td>17</td> <td>2 BHK - 2.5 BHK</td> <td>1.55 CR - ₹ 3.10 CR</td> </tr> <tr> <td>Rental</td> <td>17</td> <td>2 BHK - 2.5 BHK</td> <td>1.55 CR - ₹ 3.10 CR</td> </tr> </tbody> </table> </div>

-Above sample is just for format, dont use its value.
"""

listing_table_prompt_2 = """
I will provide you details of a real estate project listings information. Your task is to create section for listing table , first write something about listing table then make a table.
Ensure the table has a clean and structured layout.
- Dont write any additional line.
- If details not available dont mention about this.
- Table structured should be in well format without any syntax error

Sample Table Format response:-
<strong>Listing Information</strong> <p>In resale we have 31 properties available ranging from (unit type) having price from {Price}</p> <div class="tablesResponsive"> <table width="100%" border="1" cellspacing="0" cellpadding="5"> <tbody> <tr> <td>Listing Type</td> <td>Total Listings</td> <td>Unit Type Range</td> <td>Price Range</td> </tr> <tr> <td>Resale</td> <td>17</td> <td>2 BHK - 2.5 BHK</td> <td>1.55 CR - ₹ 3.10 CR</td> </tr> </tbody> </table> </div>

Above sample is just for format, dont use its value.
"""

listing_table_prompt_plot = """
I will provide you details of a real estate project listings information. Your task is to create section for listing table , first write something about listing table then make a table.
Ensure the table has a clean and structured layout.
- Dont write any additional line
- If details not available dont mention about this
- Table structured should be in well format without any syntax error
- If price is same, just give one price value in table.

sample Format response:-
<strong>Listing Information</strong> <p> In this (Project name) for resale we have total (count) properties available having price from {Price} </p> <div class="tablesResponsive"> <table width="100%" border="1" cellspacing="0" cellpadding="5"> <tbody> <tr> <td>Listing Type</td> <td>Total Listings</td> <td>Unit Type Range</td> <td>Price Range</td> </tr> <tr> <td>Resale</td> <td>17</td> <td>2 BHK - 2.5 BHK</td> <td>1.55 CR - ₹ 3.10 CR</td> </tr> <tr> <td>Rental</td> <td>17</td> <td>2 BHK - 2.5 BHK</td> <td>1.55 CR - ₹ 3.10 CR</td> </tr> </tbody> </table> </div>

-Above sample is just for format, dont use its value.
"""

listing_table_prompt_commercial = """
I will provide you details of a real estate project listings information. Your task is to create section for listing table , first generate summary about listing table then make table.

Ensure the table has a clean and structured layout. If in provided data some key is null or no value, remove those column from table.
-Remove that coloum, which has no value available.
-if rental details not available dont write about this.
-Dont write any additional line.

sample Format response:
<strong>Listing Information</strong> <p>We have (total count) options available in (project name) for resale and rental, In resale we have (count) properties available ranging from (unit type) having sizes from (price) </p> <p>For rent you can check (count) properties having options for (unit type) with price ranging from (price).</p> <div class="tablesResponsive"> <table width="100%" border="1" cellspacing="0" cellpadding="5"> <tbody> <tr> <td>Listing Type</td> <td>Total Listings</td> <td>Unit Type Range</td> <td>Price Range</td> </tr> <tr> <td>Resale</td> <td>17</td> <td>2 BHK - 2.5 BHK</td> <td>1.55 CR - ₹ 3.10 CR</td> </tr> <tr> <td>Rental</td> <td>17</td> <td>2 BHK - 2.5 BHK</td> <td>1.55 CR - ₹ 3.10 CR</td> </tr> </tbody> </table> </div>

Note:- This is just for format, use only provided data to make this type of response , dont add additional lines .
"""

nearby_landmarks_prompt = """
I will provide details of the landmarks for a real estate project. 
- Begin with a brief 2-3 sentence summary highlighting the significance of these landmarks.
- After first step, Follow this with bullet points listing the landmarks in a sentence format, specifying distances where applicable.
- Dont write any additional line.

I want response format like this :-
<strong>Nearby Landmarks</strong> <p>The residential property is strategically located near several notable landmarks, providing residents with easy access to essential amenities and services. These landmarks not only enhance the quality of life for residents but also offer a unique blend of convenience and comfort.</p> <ul> <li>St Angels Global School is just 0.2 km away, making it an ideal choice for families with children.</li> <li>Southern Peripheral Road is 5.3 km away, providing a convenient connection to the city.</li> <li>Intellion Edge is 4.1 km away, offering a hub for business and entrepreneurship.</li> <li>Hotel Sapphire is 3.3 km away, perfect for guests and visitors.</li> <li>Ananta Hospital is 1.6 km away, ensuring timely medical attention in case of an emergency.</li> <li>Spaze Forum is 2.5 km away, offering a range of shopping and dining options.</li> </ul>

-Above sample is just for format , dont use its value.
"""

transaction_prompt = """
I will give you details of real estate project for :- Govt. Registered Recent Transactions. Your task is generate a paragraph an SEO-optimized summary for the recent government-registered transactions in the real estate market Begin with direct pargarpgh dont wrtie any heading line.

Example Response:-
<strong>Govt. Registered Recent Transactions</strong><p>Over the past three months, the rental rate for properties in the residential area has remained consistently high at ₹ 23.885, with the current rate sitting at ₹ 9,264. This pattern has been observed over the past six months, with no significant fluctuations in the rental rate. However, a more dramatic shift is seen when examining the current state of the market over the past year, which has witnessed a total of 7 government-registered sales transactions with a combined gross sales value of ₹ 9 Cr, providing insight into the significant activity in the area.</p>

-Above sample is just for format , dont use its value.
"""

why_invest = """
I will provide you with details of a real estate project. Your task is to generate a why invest in this project bullet points.
-The bullet points should be seo-friendly for buyers.
-Bullet point contain only 6-7 words.
-Not more than 5 bullet points.
-Dont write any additional line in response .
sample format of Response:-
<ul>
  <li>Seamless connectivity to NH 8, Sohna Road, and Southern Peripheral Road, ideal for commuters.</li>
  <li>Posh neighbourhood and rich landscaping</li>
  <li>Prime location in Sector 70A, Gurgaon, close to industrial and commercial hubs.</li>
  <li>Spacious apartments ranging from 1475 to 3500 sq. ft., catering to various needs.</li>
  <li>2 BHK and 3 BHK apartments at competitive prices, offering an attractive investment opportunity.</li>
</ul>



-Above sample is just for format, dont use its value.
"""

example_question = """
  . What are the key features of {'Project Name'}?
  . How many units are available in {'Project Name'}?
  . What types of configurations are available in {'Project Name'}?
  . Who is the developer of {'Project Name'}?
  . What are the nearby infrastructure developments and future growth potential of {'Project Name'}?
  . What is the location of {'Project Name'}?
  . Is {'Project Name'} RERA-registered?
  . What is the expected possession date of {'Project Name'}?
  . What is the status of construction at {'Project Name'}?
  . What is the price range for units in {'Project Name'}?
  . Does {'Project Name'} have legal approvals and clearances?
  . What is the expected appreciation potential in the area of {'Project Name'}?
  . What is the location of {'Project Name'} and its proximity to key landmarks?
  . What is the total area of {'Project Name'}?
  . What are the available unit sizes and configurations in {'Project Name'} (e.g., 1 BHK, 2 BHK, etc.)?
  . What are the starting prices for units in {'Project Name'}?
  . Is {'Project Name'} part of a gated community, and what are the security features?
  . What is the distance to schools, hospitals, malls, and public transport from {'Project Name'}?
  . What kind of flooring and fittings are provided in the homes at {'Project Name'}?
"""

example_question_1 = """
  . What are the key features of {'Project Name'}?
  . How many units are available in {'Project Name'}?
  . What types of configurations are available in {'Project Name'}?
  . Who is the developer of this {'Project Name'}?
  . What are the nearby infrastructure developments and future growth potential of {'Project Name'}?
  . What is the location of the {'Project Name'}?
  . What is the expected possession date of {'Project Name'}?
  . What is the status of construction in {'Project Name'}?
  . What is the price range for units in {'Project Name'}?
  . Does {'Project Name'} have legal approvals and clearances?
  . What is the expected appreciation potential in this area of {'Project Name'}?
  . What is the location of {'Project Name'} and its proximity to key landmarks?
  . What is the total area of {'Project Name'}?
  . What are the available unit sizes and configurations (e.g., 1 BHK, 2 BHK, etc.) in {'Project Name'}?
  . What are the starting prices for units in {'Project Name'}?
  . Is {'Project Name'} part of a gated community, and what are the security features?
  . What is the distance to schools, hospitals, malls, and public transport from {'Project Name'}?
  . What kind of flooring and fittings are provided in the homes of {'Project Name'}?
"""

faq_prompt1 = f"""
You are a real-estate content writer. I will provide you detailed information about a real estate project.
Your task is to generate only 5-7 unique Frequently Asked Questions (FAQs) with answers based on the provided details.
Use this list of question for generate Question:- {example_question}.
Begin FAQ generation directly, without any heading.

Instructions:
- Each FAQ should be unique in type.
- Avoid generating questions about the project name.
- Total FAQ not more than 5-7.
- The answer should be in a meaningful sentence without any grammatical errors.
- The way of asking question should be different from the sample questions.
- Response should be without any syntax error.
- Do not include additional lines or text beyond the FAQs.

Note: Strictly follow this, generate only that questions whose answers are available.

Sample response format:
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

faq_prompt2 = f"""
You are a real-estate content writer. I will provide you detailed information about a real estate project.
Your task is to generate only 5-7 unique Frequently Asked Questions (FAQs) with answers based on the provided details.
Use this list of question for generate Question:- {example_question_1}.
Begin FAQ generation directly, without any heading.

Instructions:
- Each FAQ should be unique in type.
- Avoid generating questions about the project name.
- Total FAQ not more than 5-7.
- The answer should be in a meaningful sentence without any grammatical errors.
- The way of asking question should be different from the sample questions.
- Response should be without any syntax error.
- Do not include additional lines or text beyond the FAQs.

Note: Strictly follow this, generate only that questions whose answers are available.

Sample response format:
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
                                                                                                                                                              
class ProjectDetails(BaseModel):
    project_id: str

#Function's of fetch data from API
def get_project_data(project_id):
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        excluded_keys = ["Project Id","LaunchedDate","expectedCompletionDate","status", "About developer", "Floor plan and pricing", "Project USP", "otherProjectsByDeveloper", "Listings", "transactions", "Landmarks", "LandMarks"]

        # Filter out excluded keys
        filtered_data = {key.strip(): value for key, value in data.items() if key not in excluded_keys}

        # Handle the Rera field
        rera_info = filtered_data.get("Rera", {})
        if "Square Yards RERA" in rera_info:
            del rera_info["Square Yards RERA"]

        if rera_info:
            filtered_data["Rera"] = rera_info
            if filtered_data["Rera"] == {'Project RERA': ''}:
                filtered_data["Rera"] = "We don't have the RERA details available at the moment."
        else:
            filtered_data.pop("Rera", None)

        # Process Amenities - Include only the first two categories and limit to the first item in each list
        amenities = filtered_data.get("Amenities", {})
        if amenities:
            # Get only the first two categories and limit their values to the first item
            filtered_amenities = {category: values[:1] for category, values in list(amenities.items())[:2]}
            filtered_data["Amenities"] = filtered_amenities
        else:
            filtered_data.pop("Amenities", None)

        # Process Specification
        specification = filtered_data.get("Specification", [])
        if specification:
            filtered_specification = specification[:1]
            filtered_data["Specification"] = filtered_specification
        else:
            filtered_data.pop("Specification", None)

        # Remove any key with empty or null values
        filtered_data = {key.strip(): value for key, value in filtered_data.items() if value not in [None, '', [''], {''}]}

        
        # Format the filtered data without extra spaces
        formatted_data = "\n".join([f"{key.strip()}: {str(value).strip()}" for key, value in filtered_data.items()])
        # print(formatted_data)
        return formatted_data
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"
    
def get_project_data_usp(project_id):
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        excluded_keys = ["Project Id","LaunchedDate","expectedCompletionDate","status", "About developer", "Floor plan and pricing", "otherProjectsByDeveloper", "Listings", "transactions", "Landmarks", "LandMarks"]

        # Filter out excluded keys
        filtered_data = {key.strip(): value for key, value in data.items() if key not in excluded_keys}

        # Handle the Rera field
        rera_info = filtered_data.get("Rera", {})
        if "Square Yards RERA" in rera_info:
            del rera_info["Square Yards RERA"]

        if rera_info:
            filtered_data["Rera"] = rera_info
            if filtered_data["Rera"] == {'Project RERA': ''}:
                filtered_data["Rera"] = "We don't have the RERA details available at the moment."
        else:
            filtered_data.pop("Rera", None)

        # Process Amenities - Include only the first two categories and limit to the first item in each list
        amenities = filtered_data.get("Amenities", {})
        if amenities:
            # Get only the first two categories and limit their values to the first item
            filtered_amenities = {category: values[:1] for category, values in list(amenities.items())[:2]}
            filtered_data["Amenities"] = filtered_amenities
        else:
            filtered_data.pop("Amenities", None)

        # Process Specification
        specification = filtered_data.get("Specification", [])
        if specification:
            filtered_specification = specification[:2]
            filtered_data["Specification"] = filtered_specification
        else:
            filtered_data.pop("Specification", None)

        # Remove any key with empty or null values
        filtered_data = {key.strip(): value for key, value in filtered_data.items() if value not in [None, '', [''], {''}]}

        
        # Format the filtered data without extra spaces
        formatted_data = "\n".join([f"{key.strip()}: {str(value).strip()}" for key, value in filtered_data.items()])
        # print(formatted_data)
        return formatted_data
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"

def get_project_data_listing(project_id):
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        excluded_keys = ["Project Id","LaunchedDate","expectedCompletionDate","status", "Sublocation Name", "LandMarks","Specification", "About developer", "Floor plan and pricing", "Project USP", "otherProjectsByDeveloper", "Listings", "transactions", "Landmarks", "Rera", "Connecting Roads", "Amenities","LandMarks"]

        # Filter out excluded keys
        filtered_data = {key: value for key, value in data.items() if key not in excluded_keys}
        
        # Handle the Rera field
        rera_info = filtered_data.get("Rera", {})
        if "Square Yards RERA" in rera_info:
            del rera_info["Square Yards RERA"]
        
        # Update the Rera field in the filtered data
        if rera_info:
            filtered_data["Rera"] = rera_info
        else:
            # Remove Rera key if empty
            filtered_data.pop("Rera", None)
        
        # Format the filtered data
        formatted_data = "\n".join([f"{key}: {value}" for key, value in filtered_data.items()])
        # print(formatted_data)
        return formatted_data
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"

def fetch_filtered_floor_plan_and_pricing(project_id):
    # Define the API endpoint
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"

    # Make the API request
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract Floor Plan and Pricing
        floor_plan_and_pricing = data.get("Floor plan and pricing", [])
        # print(floor_plan_and_pricing)
        if floor_plan_and_pricing:
            result = "Available Unit Options:\n"
            for item in floor_plan_and_pricing:
                unit_type = item.get("unitType", "N/A")
                area = item.get("area", "N/A")
                price = item.get("price", "N/A")

                # Update price to "on request" if it is ₹ 0
                if price == "₹ 0":
                    price = "On request"

                # Filter out rows where unit type starts with "0"
                if not unit_type.startswith("0"):
                    result += f"Unit Type: {unit_type}, Area: {area}, Price: {price}\n"
                elif price != "on request":
                    result += f"Area: {area}, Price: {price}\n"

            # print("result value : -", result.strip())

            return result.strip()  # Remove trailing newline
        else:
            return "Available Unit Options:"
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"
    
def fetch_filtered_floor_plan_and_pricing_faq(project_id):
    # Define the API endpoint
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"

    # Make the API request
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract Floor Plan and Pricing
        floor_plan_and_pricing = data.get("Floor plan and pricing", [])

        if floor_plan_and_pricing:
            result = "Available Unit Options:\n"
            for item in floor_plan_and_pricing:
                unit_type = item.get("unitType", "N/A")
                area = item.get("area", "N/A")
                price = item.get("price", "N/A")

                # Remove "0 BHK " prefix if present
                if unit_type.startswith("0 BHK "):
                    unit_type = unit_type[5:]

                # Update price to "on request" if it is ₹ 0
                if price == "₹ 0":
                    price = "on request"

                # Filter out rows where price is "₹ 0"
                if price != "₹ 0":
                    result += f"Unit Type: {unit_type}, Area: {area}, Price: {price}\n"

            
        
            if result == "Available Unit Options:\n":

                result = ""
                # print("ressult:-",result)
                return result.strip()  # Remove trailing newline
            
            else:
                # print(result.strip())
                return result.strip()
        else:
            return " "
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"

def fetch_filtered_floor_plan_and_pricing_mixed(project_id):
    # Define the API endpoint
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"

    # Make the API request
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract Floor Plan and Pricing
        floor_plan_and_pricing = data.get("Floor plan and pricing", [])

        if floor_plan_and_pricing:
            result = "Available Unit Options:\n"
            for item in floor_plan_and_pricing:
                unit_type = item.get("unitType", "N/A")
                area = item.get("area", "N/A")
                price = item.get("price", "N/A")

                # Remove "0 BHK " prefix if present
                if unit_type.startswith("0 BHK "):
                    unit_type = unit_type[5:]

                # Update price to "on request" if it is ₹ 0
                if price == "₹ 0":
                    price = "on request"

                # Filter out rows where price is "₹ 0"
                if price != "₹ 0":
                    result += f"Unit Type: {unit_type}, Area: {area}, Price: {price}\n"

            return result.strip()
        else:
            return "Available Unit Options:"
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"

def fetch_filtered_floor_plan_and_pricing_commerical(project_id):
    # Define the API endpoint
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"

    # Make the API request
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract Floor Plan and Pricing
        floor_plan_and_pricing = data.get("Floor plan and pricing", [])

        if floor_plan_and_pricing:
            result = "Available Unit Options:\n"
            for item in floor_plan_and_pricing:
                unit_type = item.get("unitType", "N/A")
                area = item.get("area", "N/A")
                price = item.get("price", "N/A")

                # Remove "0 BHK " prefix if present
                if unit_type.startswith("0 BHK "):
                    unit_type = unit_type[5:]
                
                # Update price to "on request" if it is ₹ 0
                if price == "₹ 0":
                    price = "on request"
                
                # Filter out rows where price is "₹ 0"
                if price != "₹ 0":
                    result += f"Unit Type: {unit_type}, Area: {area}, Price: {price}\n"

            # print(result.strip())
            return result.strip()  # Remove trailing newline
        else:
            return "Available Unit Options:"
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"

def fetch_filtered_landmarks(project_id):
    # Define the API endpoint
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"

    # Make the API request
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract LandMarks
        landmarks = data.get("LandMarks", [])

        # Format landmarks for display
        formatted_landmarks = [f"{landmark['categoryName']}: {landmark['landmarkName']} is {landmark['distance']} away." for landmark in landmarks ]
        # print(formatted_landmarks)
        return formatted_landmarks
    else:
        return f"Failed to fetch data: {response.status_code}"
    
def fetch_filtered_landmarks_faq(project_id):
    # Define the API endpoint
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"

    # Make the API request
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract LandMarks
        landmarks = data.get("LandMarks", [])

        # Format landmarks for display and get the first 2
        formatted_landmarks = [
            f"{landmark['categoryName']}: {landmark['landmarkName']} is {landmark['distance']} away."
            for landmark in landmarks[:2]
        ]
        return formatted_landmarks
    else:
        return f"Failed to fetch data: {response.status_code}"

def fetch_filtered_landmarks_faq(project_id):
    # Define the API endpoint
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"

    # Make the API request
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract LandMarks
        landmarks = data.get("LandMarks", [])

        # Format landmarks for display
        formatted_landmarks = [f"{landmark['categoryName']}: {landmark['landmarkName']} is {landmark['distance']} away." for landmark in landmarks]
        
        return formatted_landmarks
    else:
        return f"Failed to fetch data: {response.status_code}"

def get_resale_and_rental_data(project_id):
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()

        # Handling Resale Data
        resale_data = data.get("Listings", {}).get("Resale", {})
        
        resale_details = ""
        if resale_data:
            resale_total_listing = resale_data.get("TotalListing", "N/A")
            resale_unit_type_range = resale_data.get("unitTypeRange", "N/A")
            resale_price_range = resale_data.get("priceRange", "").strip()  # Get and strip whitespace

            # Set default "on request" if priceRange is empty
            resale_unit_type_range = resale_unit_type_range if resale_unit_type_range else "Update soon"
            resale_price_range = resale_price_range if resale_price_range else "on request"

            resale_details = (
                f"Resale Data details is :- "
                f"Total Listings: {resale_total_listing}, "
                f"Unit Type Range: {resale_unit_type_range}, "
                f"Price: {resale_price_range}, "
            )

        # Handling Rental Data
        rental_data = data.get("Listings", {}).get("Rental", {})
        rental_details = ""
        if rental_data:
            rental_total_listing = rental_data.get("TotalListing", "N/A")
            rental_unit_type_range = rental_data.get("unitTypeRange", "N/A")
            rental_price_range = rental_data.get("priceRange", "").strip()  # Get and strip whitespace

            # Set default "on request" if priceRange is empty
            rental_unit_type_range = rental_unit_type_range if rental_unit_type_range else "Update soon"
            rental_price_range = rental_price_range if rental_price_range else "On Request"

            rental_details = (
                f"Rental Data details is :- "
                f"Total Listings: {rental_total_listing}, "
                f"Unit Type Range: {rental_unit_type_range}, "
                f"Price: {rental_price_range}, "
            )

        # Combine the details
        combined_details = f"{rental_details}\n{resale_details}"
        # print(combined_details)
        return combined_details
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"

def get_resale_and_rental_data_plot(project_id):
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()

        # Handling Resale Data
        resale_data = data.get("Listings", {}).get("Resale", {})
        
        resale_details = ""
        if resale_data:
            resale_total_listing = resale_data.get("TotalListing", "N/A")
            resale_unit_type_range = resale_data.get("unitTypeRange", "N/A")
            resale_price_range = resale_data.get("priceRange", "").strip()  # Get and strip whitespace

            # Set default "on request" if priceRange is empty
            resale_unit_type_range = resale_unit_type_range if resale_unit_type_range else "Update soon"
            resale_price_range = resale_price_range if resale_price_range else "on request"

            resale_details = (
                f"Resale Data details is :- "
                f"Total Listings: {resale_total_listing}, "
                f"Price: {resale_price_range}, "
            )

        # Handling Rental Data
        rental_data = data.get("Listings", {}).get("Rental", {})
        rental_details = ""
        if rental_data:
            rental_total_listing = rental_data.get("TotalListing", "N/A")
            rental_unit_type_range = rental_data.get("unitTypeRange", "N/A")
            rental_price_range = rental_data.get("priceRange", "").strip()  # Get and strip whitespace

            # Set default "on request" if priceRange is empty
            rental_unit_type_range = rental_unit_type_range if rental_unit_type_range else "Update soon"
            rental_price_range = rental_price_range if rental_price_range else "On Request"

            rental_details = (
                f"Rental Data details is :- "
                f"Total Listings: {rental_total_listing}, "
                f"Price: {rental_price_range}, "
            )

        # Combine the details
        combined_details = f"{rental_details}\n{resale_details}"
        # print(combined_details)
        return combined_details
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"

def get_rental(project_id):
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()

        # Handling Rental Data
        rental_data = data.get("Listings", {}).get("Rental", {})
        rental_details = ""
        if rental_data:
            rental_total_listing = rental_data.get("TotalListing", "N/A")
            rental_unit_type_range = rental_data.get("unitTypeRange", "N/A")
            rental_price_range = rental_data.get("priceRange", "").strip()  # Get and strip whitespace

            # Set default "on request" if priceRange is empty
            rental_price_range = rental_price_range if rental_price_range else "On Request"

            rental_details = (
                f"Rental Data details is :- "
                f"Total Listings: {rental_total_listing}, "
                f"Unit Type Range: {rental_unit_type_range}, "
                f"Rental Price Range: {rental_price_range}, "
            )

        # Combine the details
        combined_details = f"{rental_details}"
        # print("rental data=",combined_details,"okay")
        return combined_details
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"
    
def get_transaction_data(project_id):
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        transactions = data.get("transactions", {}).get("aggregations", [])
        transaction_details = []

        if transactions:
            for transaction in transactions:
                details = transaction.get("detail", {})
                aggregation = transaction.get("aggregation", "N/A")
                sales_transactions = details.get("salesTransactions", "N/A")
                gross_sales_value = details.get("grossSalesValue", "N/A")
                current_rate = details.get("currentRate", "N/A")
                rental_rate = details.get("rentalRate", "N/A")
                price_movement = details.get("priceMovement", "N/A")

                # Collect transaction details, omitting zero values for specific fields
                transaction_info = {
                    "Aggregation": aggregation,
                    "Rental Rate": rental_rate,
                    "Current Rate": current_rate
                }

                if sales_transactions != "0":
                    transaction_info["Sales Transactions"] = sales_transactions
                
                if gross_sales_value != "₹ 0":
                    transaction_info["Gross Sales Value"] = gross_sales_value

                if price_movement != "N/A":
                    transaction_info["Price Movement"] = price_movement

                transaction_details.append(transaction_info)

        if transaction_details:
            response_string = "Govt. Registered Recent Transactions:\n"
            for transaction in transaction_details:
                response_string += (f"\n**Aggregation**: {transaction['Aggregation']}\n"
                                    f"**Rental Rate**: {transaction['Rental Rate']}\n"
                                    f"**Current Rate**: {transaction['Current Rate']}\n")
                if "Sales Transactions" in transaction:
                    response_string += f"**Sales Transactions**: {transaction['Sales Transactions']}\n"
                if "Gross Sales Value" in transaction:
                    response_string += f"**Gross Sales Value**: {transaction['Gross Sales Value']}\n"
                if "Price Movement" in transaction:
                    response_string += f"**Price Movement**: {transaction['Price Movement']}\n"
            # print(response_string)
            return response_string.strip()
        else:
            return "NA"
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"

def get_transaction_data_commercial(project_id):
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        transactions = data.get("transactions", {}).get("aggregations", [])
        transaction_details = []

        if transactions:
            for transaction in transactions:
                details = transaction.get("detail", {})
                aggregation = transaction.get("aggregation", "N/A")
                sales_transactions = details.get("salesTransactions", "N/A")
                gross_sales_value = details.get("grossSalesValue", "N/A")
                current_rate = details.get("currentRate", "N/A")
                # rental_rate = details.get("rentalRate", "N/A")
                price_movement = details.get("priceMovement", "N/A")

                # Collect transaction details, omitting zero values for specific fields
                transaction_info = {
                    "Aggregation": aggregation,
                    # "Rental Rate": rental_rate,
                    "Current Rate": current_rate
                }

                if sales_transactions != "0":
                    transaction_info["Sales Transactions"] = sales_transactions
                
                if gross_sales_value != "₹ 0":
                    transaction_info["Gross Sales Value"] = gross_sales_value

                if price_movement != "N/A":
                    transaction_info["Price Movement"] = price_movement

                transaction_details.append(transaction_info)

        if transaction_details:
            response_string = "Recent Transactions:\n"
            for transaction in transaction_details:
                response_string += (f"\n**Aggregation**: {transaction['Aggregation']}\n"
                                    # f"**Rental Rate**: {transaction['Rental Rate']}\n"
                                    f"**Current Rate**: {transaction['Current Rate']}\n")
                if "Sales Transactions" in transaction:
                    response_string += f"**Sales Transactions**: {transaction['Sales Transactions']}\n"
                if "Gross Sales Value" in transaction:
                    response_string += f"**Gross Sales Value**: {transaction['Gross Sales Value']}\n"
                if "Price Movement" in transaction:
                    response_string += f"**Price Movement**: {transaction['Price Movement']}\n"
            # print(response_string)
            return response_string.strip()
        else:
            return "NA"
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"
        
def get_transaction_data_faq(project_id):
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        transactions = data.get("transactions", {}).get("aggregations", [])
        transaction_details = []

        if transactions:
            for transaction in transactions:
                details = transaction.get("detail", {})
                aggregation = transaction.get("aggregation", "N/A")
                sales_transactions = details.get("salesTransactions", "N/A")
                gross_sales_value = details.get("grossSalesValue", "N/A")
                current_rate = details.get("currentRate", "N/A")
                # rental_rate = details.get("rentalRate", "N/A")
                price_movement = details.get("priceMovement", "N/A")

                # Collect transaction details, omitting zero values for specific fields
                transaction_info = {
                    "Aggregation": aggregation,
                    # "Rental Rate": rental_rate,
                    "Current Rate": current_rate
                }

                if sales_transactions != "0":
                    transaction_info["Sales Transactions"] = sales_transactions
                
                if gross_sales_value != "₹ 0":
                    transaction_info["Gross Sales Value"] = gross_sales_value

                if price_movement != "N/A":
                    transaction_info["Price Movement"] = price_movement

                transaction_details.append(transaction_info)

        if transaction_details:
            response_string = "Recent Transactions:\n"
            for transaction in transaction_details:
                response_string += (f"\n**Aggregation**: {transaction['Aggregation']}\n"
                                    # f"**Rental Rate**: {transaction['Rental Rate']}\n"
                                    f"**Current Rate**: {transaction['Current Rate']}\n")
                if "Sales Transactions" in transaction:
                    response_string += f"**Sales Transactions**: {transaction['Sales Transactions']}\n"
                if "Gross Sales Value" in transaction:
                    response_string += f"**Gross Sales Value**: {transaction['Gross Sales Value']}\n"
            return response_string.strip()
        else:
            return "NA"
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"
  
def get_project_data_for_FAQ(project_id):
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        excluded_keys = ["LandMarks", "Sublocation Name", "Project Id", "otherProjectsByDeveloper", "transactions", "Floor plan and pricing"]

        # Filter out excluded keys
        filtered_data = {key: value for key, value in data.items() if key not in excluded_keys}
        
        # Handle the Rera field
        rera_info = filtered_data.get("Rera", {})
        if "Square Yards RERA" in rera_info:
            del rera_info["Square Yards RERA"]
        
        # Update the Rera field in the filtered data
        if rera_info:
            filtered_data["Rera"] = rera_info
            if filtered_data["Rera"] == {'Project RERA': ''}:
                filtered_data.pop("Rera", None)
        else:
            filtered_data.pop("Rera", None)
        
        amenities = filtered_data.get("Amenities", {})
        if amenities:
            # Get only the first two categories and limit their values to the first item
            filtered_amenities = {category: values[:1] for category, values in list(amenities.items())[:5]}
            filtered_data["Amenities"] = filtered_amenities
        else:
            filtered_data.pop("Amenities", None)

        
        # Include only specific details from "About developer"
        about_developer = data.get("About developer", {})
        about_developer_filtered = {
            "totalProjects": about_developer.get("totalProjects"),
            "name": about_developer.get("name")
        }

        # Add the filtered "About developer" section back to filtered data
        if about_developer_filtered:
            filtered_data["About developer"] = about_developer_filtered
        
        # Remove any key with empty or null values
        formatted_data = {key.strip(): value for key, value in filtered_data.items() if value not in [None, '', [''], [], {''}, {'totalProjects': None, 'name': None}]}
        # print("FAQ = ",formatted_data)
        return formatted_data
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"

def extract_overview_content(html_string):

    # Check if the input is a string and contains <p>
    if isinstance(html_string, str) and "<p>" in html_string:

        # Extract content starting from the first <p> tag
        overview_content = html_string.split("<p>", 1)[1] # Splitting from the first occurrence of <p>
        
        # Prepend the missing <p> tag
        overview_content = "<p>" + overview_content
        return overview_content
    else:
        return html_string  # Return the original string if <p> is not found or it's not a string

@app.post("/residential-project-description")
async def generate_project_details(details: ProjectDetails):
    project_id = details.project_id

    # for project_id in project_ids:
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"
    response = requests.get(api_url)

    if response.status_code == 200:

        floor_plan_and_pricing = fetch_filtered_floor_plan_and_pricing(project_id)
        raw_data = "Use these details for project overview : \n"+get_project_data(project_id)+"\n\nUse this details for Table :- "+floor_plan_and_pricing
        raw_data2 = get_project_data(project_id)

        raw_data_usp = get_project_data_usp(project_id)
        details_listings = get_resale_and_rental_data(project_id)
        response_transaction = get_transaction_data(project_id)
        faq_data = str(get_project_data_for_FAQ(project_id))+" "+str(fetch_filtered_floor_plan_and_pricing_faq(project_id))+" "+str(get_transaction_data_faq(project_id))+" Nearby landmarks are "+str(fetch_filtered_landmarks_faq(project_id))
        landmarks_data = fetch_filtered_landmarks(project_id)

        def create_chat_completion(prompt, content):
            content = jsonable_encoder(content)
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": f"This is the project details of residential property :-\n {content}"
                    }
                ],
                model="llama3-8b-8192"
                # model="mixtral-8x7b-32768",
            )
            groq_reponse = chat_completion.choices[0].message.content
            result = str(groq_reponse).replace("'s","")
            final_result = str(result).replace("'","")
            return final_result 
        
        def create_chat_completion_openai(prompt, content):
            content = jsonable_encoder(content)
            chat_completion = openai.ChatCompletion.create(
                deployment_id="sqy-gpt4o-mini",
                model="sqy-gpt4o-mini",
                temperature = 0.7,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"This is the project details :-\n\n {content}"}
                ]
                )

            completion_content = chat_completion.choices[0].message.content
            result = str(completion_content).replace("'s","")
            result = result.replace("'","")
            return result
                
        if floor_plan_and_pricing == "Available Unit Options:":
            overview_content_raw  = create_chat_completion(str(prompt2), raw_data2)
            overview_content = extract_overview_content(overview_content_raw)
        else:
            overview_content_raw2  = create_chat_completion(str(prompt), raw_data)
            overview_content = extract_overview_content(overview_content_raw2)

        if get_rental(project_id) == "":
            listing_table_response = "" if details_listings == "\n" else create_chat_completion(str(listing_table_prompt_2), get_project_data_listing(project_id)+"\n"+details_listings)

        else:
            listing_table_response = "" if details_listings == "\n" else create_chat_completion(str(listing_table_prompt), get_project_data_listing(project_id)+"\n"+details_listings)
            
        if landmarks_data == []:
            nearby_landmarks_response = " "
        else:
            nearby_landmarks_response = create_chat_completion(str(nearby_landmarks_prompt), landmarks_data)
        
        response_transaction_table = "" if response_transaction == "NA" else create_chat_completion(str(transaction_prompt), response_transaction)
        why_invest_response = create_chat_completion(str(why_invest), raw_data_usp)
        
        data = response.json()

        # Extract only the Rera field
        rera_info = data.get("Rera", {})

        # Remove "Square Yards RERA" if present
        if "Square Yards RERA" in rera_info:
            del rera_info["Square Yards RERA"]

        # Check if Rera is empty or contains only {'Project RERA': ''}
        if not rera_info or rera_info == {'Project RERA': ''}:
            faq_prompt = faq_prompt2  # If Rera is null, use prompt1

        else:
            faq_prompt = faq_prompt1  # If Rera has valid data, use prompt2

        faq_response = create_chat_completion_openai(str(faq_prompt), faq_data)

        content = [overview_content]
        content.append(nearby_landmarks_response)
        
        if listing_table_response and listing_table_response != "\n":
            content.append(listing_table_response)

        if response_transaction_table and response_transaction_table != "NA":
            content.append(response_transaction_table)
            
        # Extract the HTML part of FAQ response
        start_index = faq_response.find('<div')  # Find the starting index of '<div>'
        end_index = faq_response.rfind('</div>')  # Find the last occurrence of '</div>'

        if start_index != -1 and end_index != -1:
            sliced_response_faq = faq_response[start_index:end_index + len('</div>')]
        else:
            sliced_response_faq = faq_response 
        
        return {
            "status": 1,
            "overview_content": str("\n\n".join(content)).replace("\n",""),
            "usp_response": str(why_invest_response).replace("\n",""),
            "FAQ_response": str(sliced_response_faq).replace("\n","")
            }
    else:
        return{
                "status":0,
                "overview_content": "",
                "usp_response": "",
                "FAQ_response": ""
                }
        
@app.post("/commercial-project-description")
async def generate_project_details2(details: ProjectDetails):
    project_id = details.project_id

    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        floor_plan_and_pricing = fetch_filtered_floor_plan_and_pricing_commerical(project_id)
        details_listings = get_resale_and_rental_data_plot(project_id)
        response_transaction = get_transaction_data_commercial(project_id)
        faq_data = str(get_project_data_for_FAQ(project_id))+" "+str(fetch_filtered_floor_plan_and_pricing_faq(project_id))+" "+str(get_transaction_data_faq(project_id))+" Nearby landmarks are "+str(fetch_filtered_landmarks_faq(project_id))
        landmarks_data = fetch_filtered_landmarks(project_id)
        raw_data = "Use these details for project overview:-\n"+get_project_data(project_id)+"\n\nUse this details for Table :-\n"+floor_plan_and_pricing
        raw_data2 = "Use these details for project overview:-\n"+get_project_data(project_id)
        def create_chat_completion(prompt, content):
            content = jsonable_encoder(content)

            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": f"This is the project details of commercial property :-\n\n {str(content)}"}
                    ],
                    model="llama3-8b-8192",
                )
                completion_content = chat_completion.choices[0].message.content
                result = str(completion_content).replace("'s","")
                result = result.replace("'","")
                return result
            except Exception as e:
                return "Content generation failed. Please try again later."

        # Generate the required sections using prompts
        if floor_plan_and_pricing == "Available Unit Options:":
            overview_content_raw = create_chat_completion(prompt2, raw_data2)
            overview_content = extract_overview_content(overview_content_raw)
        else:
            overview_content_raw2 = create_chat_completion(prompt, raw_data)
            overview_content = extract_overview_content(overview_content_raw2)

        nearby_landmarks_response = create_chat_completion(nearby_landmarks_prompt, landmarks_data)

        if get_rental(project_id) == "":
            listing_table_response = "" if details_listings == "\n" else create_chat_completion(listing_table_prompt_plot, get_project_data_listing(project_id)+"\n"+details_listings)

        else:
            listing_table_response = "" if details_listings == "\n" else create_chat_completion(listing_table_prompt, get_project_data_listing(project_id)+"\n"+details_listings)
        
        if landmarks_data == []:
            nearby_landmarks_response = " "
        else:
            nearby_landmarks_response = create_chat_completion(nearby_landmarks_prompt, landmarks_data)
          
        response_transaction_table = "" if response_transaction == "NA" else create_chat_completion(transaction_prompt, response_transaction)
        why_invest_response = create_chat_completion(why_invest, str(raw_data.strip()))
        
        def create_chat_completion_faq(prompt, content):
            content = jsonable_encoder(content)
            chat_completion_openai = openai.ChatCompletion.create(
                deployment_id="sqy-gpt4o-mini",
                model="sqy-gpt4o-mini",
                temperature = 0.7,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"This is the project details :-\n\n {content}"}
                ]
                )

            completion_content = chat_completion_openai.choices[0].message.content
            result = str(completion_content).replace("'s","")
            result = result.replace("'","")
            return result
        
        data = response.json()

        # Extract only the Rera field
        rera_info = data.get("Rera", {})

        # Remove "Square Yards RERA" if present
        if "Square Yards RERA" in rera_info:
            del rera_info["Square Yards RERA"]

        # Check if Rera is empty or contains only {'Project RERA': ''}
        if not rera_info or rera_info == {'Project RERA': ''}:
            faq_prompt = faq_prompt2  # If Rera is null, use prompt1

        else:
            faq_prompt = faq_prompt1  # If Rera has valid data, use prompt2

        faq_response = create_chat_completion_faq(faq_prompt, faq_data)

        # Construct the response content
        content = [overview_content]

        # Add Nearby Landmarks
        content.append(nearby_landmarks_response)

        # Conditionally add Listing Information if it has valid data
        if listing_table_response and listing_table_response != "\n":
            content.append(listing_table_response)

        # Conditionally add Govt. Registered Recent Transactions if it has valid data
        if response_transaction_table and response_transaction_table != "NA":
            content.append(response_transaction_table)

        # Extract the HTML part of FAQ response
        start_index = faq_response.find('<div')  # Find the starting index of '<div>'
        end_index = faq_response.rfind('</div>')  # Find the last occurrence of '</div>'

        if start_index != -1 and end_index != -1:
            sliced_response_faq = faq_response[start_index:end_index + len('</div>')]
        else:
            sliced_response_faq = faq_response 

        # Join all content parts
        return {
            "status": 1,
            "overview_content": str("\n\n".join(content)).replace("\n",""),
            "usp_response": str(why_invest_response).replace("\n",""),
            "FAQ_response": str(sliced_response_faq).replace("\n","")
                }
    else:
        return{"status":0,
            "overview_content": "",
            "usp_response": "",
            "FAQ_response": ""
            }

@app.post("/plot-project-description")
def generate_project_details(details: ProjectDetails):
    project_id = details.project_id

    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
            
        floor_plan_and_pricing = fetch_filtered_floor_plan_and_pricing_commerical(project_id)
        raw_data = "Use these details for project overview:-\n"+get_project_data(project_id)+"\n\nUse this details for Table :-"+floor_plan_and_pricing
        

        raw_data2 = "Use these details for project overview:-\n"+str(get_project_data(project_id))
        details_listings = get_resale_and_rental_data_plot(project_id)
        response_transaction = get_transaction_data_commercial(project_id)

        faq_data = str(get_project_data_for_FAQ(project_id))+" "+str(fetch_filtered_floor_plan_and_pricing_faq(project_id))+" "+str(get_transaction_data_faq(project_id))+" Nearby landmarks are "+str(fetch_filtered_landmarks_faq(project_id))
        landmarks_data = fetch_filtered_landmarks(project_id)

        def create_chat_completion(prompt, content):
            content = (str(content).split())
            
            chat_completion = client.chat.completions.create(
        
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": f"This is the project details of plot property :-\n\n {str(content)}"
                    }
                ],
                model="llama3-8b-8192",
            )

            completion_content = chat_completion.choices[0].message.content
            result = str(completion_content).replace("'s","")
            result = result.replace("'","")
            return result
        
        # Generate the required sections using prompts
        if floor_plan_and_pricing == "Available Unit Options:":
            overview_content_raw = create_chat_completion(prompt2, raw_data2)
            overview_content = extract_overview_content(overview_content_raw)
        else:
            overview_content_raw2 = create_chat_completion(prompt, raw_data)
            overview_content = extract_overview_content(overview_content_raw2)

        if get_rental(project_id) == "":
            listing_table_response = "" if details_listings == "\n" else create_chat_completion(listing_table_prompt_plot, get_project_data_listing(project_id)+"\n"+details_listings)

        else:
            listing_table_response = "" if details_listings == "\n" else create_chat_completion(listing_table_prompt, get_project_data_listing(project_id)+"\n"+details_listings)
         
        if landmarks_data == []:
            nearby_landmarks_response = " "
        else:
            nearby_landmarks_response = create_chat_completion(nearby_landmarks_prompt, landmarks_data)
          
        # listing_table_response = "" if details_listings == "\n" else create_chat_completion(listing_table_prompt_commercial, details_listings)
        # nearby_landmarks_response = create_chat_completion(nearby_landmarks_prompt, landmarks_data)
        response_transaction_table = "" if response_transaction == "NA" else create_chat_completion(transaction_prompt, response_transaction)
        why_invest_response = create_chat_completion(why_invest, raw_data)
        def create_chat_completion_faq(prompt, content):
            content = jsonable_encoder(content)
            chat_completion = openai.ChatCompletion.create(
                deployment_id="sqy-gpt4o-mini",
                model="sqy-gpt4o-mini",
                temperature = 0.7,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"This is the project details :-\n\n {content}"}
                ]
                )

            completion_content = chat_completion.choices[0].message.content
            result = str(completion_content).replace("'s","")
            result = result.replace("'","")
            return result
        
        data = response.json()

        # Extract only the Rera field
        rera_info = data.get("Rera", {})

        # Remove "Square Yards RERA" if present
        if "Square Yards RERA" in rera_info:
            del rera_info["Square Yards RERA"]

        # Check if Rera is empty or contains only {'Project RERA': ''}
        if not rera_info or rera_info == {'Project RERA': ''}:
            faq_prompt = faq_prompt2  # If Rera is null, use prompt1

        else:
            faq_prompt = faq_prompt1  # If Rera has valid data, use prompt2

        faq_response = create_chat_completion_faq(faq_prompt, faq_data)

        # Construct the response content
        content = [overview_content]

        # Add Nearby Landmarks
        content.append(nearby_landmarks_response)

        # Conditionally add Listing Information if it has valid data
        if listing_table_response and listing_table_response != "\n":
            content.append(listing_table_response)

        # Conditionally add Govt. Registered Recent Transactions if it has valid data
        if response_transaction_table and response_transaction_table != "NA":
            content.append(response_transaction_table)

        # Extract the HTML part of FAQ response
        start_index = faq_response.find('<div')  # Find the starting index of '<div>'
        end_index = faq_response.rfind('</div>')  # Find the last occurrence of '</div>'

        if start_index != -1 and end_index != -1:
            sliced_response_faq = faq_response[start_index:end_index + len('</div>')]
        else:
            sliced_response_faq = faq_response 

        return{
            "status": 1,
            "overview_content": str("\n\n".join(content)).replace("\n",""),
            "usp_response": str(why_invest_response).replace("\n",""),
            "FAQ_response": str(sliced_response_faq).replace("\n","")
              }


    else:
        return{"status":0,
               "overview_content": "",
                "usp_response": "",
                "FAQ_response": ""
                }
    
@app.post("/mixed-project-description")
async def generate_project_details(details: ProjectDetails):
    project_id = details.project_id

    # for project_id in project_ids:
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"
    response = requests.get(api_url)

    if response.status_code == 200:

        floor_plan_and_pricing = fetch_filtered_floor_plan_and_pricing_mixed(project_id)
        raw_data = "Use these details for project overview :- "+get_project_data(project_id)+floor_plan_and_pricing
        raw_data2 = get_project_data(project_id)
        raw_data_usp = get_project_data_usp(project_id)
        details_listings = get_resale_and_rental_data(project_id)
        response_transaction = get_transaction_data(project_id)
        faq_data = str(get_project_data_for_FAQ(project_id))+" "+str(fetch_filtered_floor_plan_and_pricing_faq(project_id))+" "+str(get_transaction_data_faq(project_id))+" Nearby landmarks are "+str(fetch_filtered_landmarks_faq(project_id))

        landmarks_data = fetch_filtered_landmarks(project_id)

        def create_chat_completion(prompt, content):
           
            content = jsonable_encoder(content)
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": f"This is the project details :-\n\n {content}"
                    }
                ],
                model="llama-3.1-8b-instant"

                # model="llama3-8b-8192",
                # model = "llama3-70b-8192"
                
                )
            
            completion_content = chat_completion.choices[0].message.content
            result = str(completion_content).replace("'s","")
            result = result.replace("'","")
            return result
        
        if floor_plan_and_pricing == "Available Unit Options:":
            overview_content_raw  = create_chat_completion(str(prompt2), raw_data2)
            # print("overview_content_raw = ",overview_content_raw)
            overview_content = extract_overview_content(overview_content_raw)
        else:
            overview_content_raw2  = create_chat_completion(str(prompt), raw_data)
            # print("overview_content_raw2 = ",overview_content_raw2)
            overview_content = extract_overview_content(overview_content_raw2)

        if get_rental(project_id) == "":
            listing_table_response = "" if details_listings == "\n" else create_chat_completion(str(listing_table_prompt_2), get_project_data_listing(project_id)+"\n"+details_listings)

        else:
            listing_table_response = "" if details_listings == "\n" else create_chat_completion(str(listing_table_prompt), get_project_data_listing(project_id)+"\n"+details_listings)
            
        if landmarks_data == []:
            nearby_landmarks_response = " "
        else:
            nearby_landmarks_response = create_chat_completion(str(nearby_landmarks_prompt), landmarks_data)
        
        response_transaction_table = "" if response_transaction == "NA" else create_chat_completion(str(transaction_prompt), response_transaction)
        why_invest_response = create_chat_completion(str(why_invest), raw_data_usp)
        
        def create_chat_completion_faq(prompt, content):
            content = jsonable_encoder(content)
            chat_completion = openai.ChatCompletion.create(
                deployment_id="sqy-gpt4o-mini",
                model="sqy-gpt4o-mini",
                temperature = 0.7,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"This is the project details :-\n\n {content}"}
                ]
                )

            completion_content = chat_completion.choices[0].message.content
            result = str(completion_content).replace("'s","")
            result = result.replace("'","")
            return result
        
        data = response.json()

        # Extract only the Rera field
        rera_info = data.get("Rera", {})

        # Remove "Square Yards RERA" if present
        if "Square Yards RERA" in rera_info:
            del rera_info["Square Yards RERA"]

        # Check if Rera is empty or contains only {'Project RERA': ''}
        if not rera_info or rera_info == {'Project RERA': ''}:
            faq_prompt = faq_prompt2  # If Rera is null, use prompt1

        else:
            faq_prompt = faq_prompt1  # If Rera has valid data, use prompt2

        faq_response = create_chat_completion_faq(str(faq_prompt), faq_data)

        content = [overview_content]
        content.append(nearby_landmarks_response)
        
        if listing_table_response and listing_table_response != "\n":
            content.append(listing_table_response)

        if response_transaction_table and response_transaction_table != "NA":
            content.append(response_transaction_table)
            
        # Extract the HTML part of FAQ response
        start_index = faq_response.find('<div')  # Find the starting index of '<div>'
        end_index = faq_response.rfind('</div>')  # Find the last occurrence of '</div>'

        if start_index != -1 and end_index != -1:
            sliced_response_faq = faq_response[start_index:end_index + len('</div>')]
        else:
            sliced_response_faq = faq_response 

        return {
            "status": 1,
            "overview_content": str("\n\n".join(content)).replace("\n",""),
            "usp_response": str(why_invest_response).replace("\n",""),
            "FAQ_response": str(sliced_response_faq).replace("\n","")
            }
    else:
        return{
                "status":0,
                "overview_content": "",
                "usp_response": "",
                "FAQ_response": ""
                }

@app.post("/project-faqs")
async def generate_project_faq(details: ProjectDetails):
    project_id = details.project_id

    # API call for fetching project data
    api_url = f"https://stage-www.squareyards.com/project-data-for-ai/{project_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        # Fetch FAQ-related data
        faq_data = str(get_project_data_for_FAQ(project_id))+" "+str(fetch_filtered_floor_plan_and_pricing_faq(project_id))+" "+str(get_transaction_data_faq(project_id))+" Nearby landmarks are "+str(fetch_filtered_landmarks_faq(project_id))

        # Function to generate chat completion using the given model
        def create_chat_completion(prompt, content):
            content = jsonable_encoder(content)

            chat_completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt4o-mini",
            model="sqy-gpt4o-mini",
            temperature = 0.7,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"This is the project details :-\n\n {content}"}
            ]
            )

            completion_content = chat_completion.choices[0].message.content
            result = str(completion_content).replace("'s","")
            result = result.replace("'","")
            return result
        
        data = response.json()

        # Extract only the Rera field
        rera_info = data.get("Rera", {})

        # Remove "Square Yards RERA" if present
        if "Square Yards RERA" in rera_info:
            del rera_info["Square Yards RERA"]

        # Check if Rera is empty or contains only {'Project RERA': ''}
        if not rera_info or rera_info == {'Project RERA': ''}:
            faq_prompt = faq_prompt2  # If Rera is null, use prompt1

        else:
            faq_prompt = faq_prompt1  # If Rera has valid data, use prompt2

        print(faq_prompt)
        # Generate FAQ response
        faq_response = create_chat_completion(str(faq_prompt), rera_info)
        # Generate FAQ response
        faq_response = create_chat_completion(str(faq_prompt), faq_data)
            
        # Extract the HTML part of FAQ response
        start_index = faq_response.find('<div')  # Find the starting index of '<div>'
        end_index = faq_response.rfind('</div>')  # Find the last occurrence of '</div>'

        if start_index != -1 and end_index != -1:
            sliced_response_faq = faq_response[start_index:end_index + len('</div>')]
        else:
            sliced_response_faq = faq_response 

        return {
            "status": 1,
            "FAQ_response": str(sliced_response_faq).replace("\n", "")
        }

    else:
        return {
            "status": 0,
            "FAQ_response": ""
        }

# Fixed prompt for FAQ generation
DSE_FAQ_PROMPT = """You are an expert real estate content writer and SEO specialist. Your task is to analyze the provided property metadata and create SEO-optimized FAQs that will help improve search rankings for key property-related queries.

Instructions for FAQ Generation:

1. Content Guidelines:
   - Focus on high-value search terms related to property prices, amenities, location benefits, and investment potential
   - Include specific location-based information from the metadata
   - Ensure answers are factual and based on the provided metadata
   - Maintain a professional yet conversational tone

2. SEO Optimization:
   - Use relevant long-tail keywords naturally in questions
   - Include location-specific terms in both questions and answers
   - Incorporate price ranges and property specifications when available
   - Target common user queries about the property type and location

3. Technical Requirements:
   - Generate exactly 12 FAQs
   - Return response in the following JSON format:
     {
       "faqs": [
         {
           "question": "Your question here?",
           "answer": "Your answer here"
         }
       ]
     }
   - Ensure all JSON keys and values are properly formatted with double quotes
   - No HTML tags or special formatting - pure text content only

4. Answer Structure:
   - Keep answers concise yet informative (40-60 words each)
   - Include specific data points from the metadata
   - Start with a direct answer and follow with supporting details
   - End each answer with a clear value proposition

5. Content Restrictions:
   - No introductory or concluding text
   - No placeholder or generic content
   - No repetitive information across answers
   - No speculative claims without data support
   - No HTML tags or formatting in the content
   - All content must be within the JSON structure

Always return the response as a valid JSON object matching the specified structure. The response should be parseable by a JSON parser without any additional processing needed."""

class URLContentInput(BaseModel):
    url: Optional[str] = None
    post_content: Optional[str] = None
    
    @validator('url')
    def validate_url(cls, v):
        # Return None if URL is None or empty string
        if v is None or v == "string" or "":
            return None
            
        # Only validate URL format if a value is provided
        if not v.startswith('https://www.squareyards.com/'):
            raise ValueError('URL must be a valid Square Yards URL')
        return v
       
class FAQ(BaseModel):
    question: str
    answer: str

class FAQContent(BaseModel):
    faqs: List[FAQ]

class StandardResponse(BaseModel):
    status: str
    message: str
    faq_content: dict = {}  # Changed to dict type to handle both success and error cases

def create_error_response(error_message: str) -> dict:
    """Creates a standardized error response"""
    return {
        "status": "0",
        "message": error_message,
        "faq_content": ""
    }

def create_success_response(faqs: List[dict]) -> dict:
    """Creates a standardized success response with structured FAQ content"""
    return {
        "status": "1",
        "message": "",
        "faq_content": {
            "faqs": faqs
        }
    }

def get_relative_path(url: str) -> str:
    """Extracts the relative path from a Square Yards URL."""
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    return path

def parse_faq_content(content: str) -> List[dict]:
    """
    Parses the OpenAI response into structured FAQ format.
    Expected format from OpenAI should be JSON string containing array of Q&A pairs.
    """
    try:
        # First try to parse if the response is already in JSON format
        try:
            faq_data = json.loads(content)
            if isinstance(faq_data, dict) and "faqs" in faq_data:
                return faq_data["faqs"]
            return faq_data
        except json.JSONDecodeError:
            # If not JSON, parse the text format and convert to structured format
            faqs = []
            # Split content into Q&A pairs (assuming format "Q: ... A: ...")
            qa_pairs = content.split('\n\n')
            
            for pair in qa_pairs:
                if 'Q:' in pair and 'A:' in pair:
                    # Split each pair into question and answer
                    parts = pair.split('A:')
                    question = parts[0].replace('Q:', '').strip()
                    answer = parts[1].strip()
                    
                    faqs.append({
                        "question": question,
                        "answer": answer
                    })
            
            return faqs
    except Exception as e:
        raise Exception(f"Error parsing FAQ content: {str(e)}")

def create_dse_faq(content):
    """Creates a chat completion using Azure OpenAI with the fixed prompt."""
    try:
        content = jsonable_encoder(content)
        # Update the system prompt to request structured output
        structured_prompt = DSE_FAQ_PROMPT + "\nPlease provide the FAQs in a structured format with clear questions and answers. Format each FAQ as 'Q: [question] A: [answer]'"
        
        completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt-35-turbo-16k",
            model="sqy-text-embedding-ada-002",
            temperature=0.7,
            messages=[
                {"role": "system", "content": structured_prompt},
                {"role": "user", "content": str(content)}
            ]
        )
        get_content = dict(completion.choices[0].message)
        return parse_faq_content(get_content['content'])
    except Exception as e:
        raise Exception(f"Error in chat completion: {str(e)}")

@app.post("/dse-page-faq/", response_model=StandardResponse)
async def generate_faq(input_data: URLContentInput):
    """
    Generates FAQs based on either the provided Square Yards URL or direct post content.
    Returns standardized response format with structured FAQ content.
    """
    try:
        # If post_content is provided and URL is empty/null, use direct content
        if not input_data.url and input_data.post_content:
            try:
                
                faq_content = create_dse_faq(input_data.post_content)
                return JSONResponse(
                    content=create_success_response(faq_content)
                )
            except Exception as e:
                return JSONResponse(
                    content=create_error_response(f"Error processing content: {str(e)}")
                )

        # Otherwise, follow the existing URL-based flow
        relative_path = get_relative_path(input_data.url)
        
        # Construct the autocomplete API URL
        autocomplete_url = f"https://rsi.squareyards.com/url-autocomplete?searchText={relative_path}"
        
        # First API call to get meta data
        response = requests.get(autocomplete_url)
        if not response.ok:
            return JSONResponse(
                content=create_error_response(f"First API call failed: {response.text}")
            )
        
        # Parse the response
        meta_data = response.json()
        
        # Extract blog post ID
        if (not meta_data.get('status') or
            not meta_data.get('data') or
            len(meta_data['data']) == 0 or
            '_source' not in meta_data['data'][0]):
            return JSONResponse(
                content=create_error_response("Invalid response structure from first API")
            )
            
        blog_post_id = meta_data['data'][0]['_source'].get('blogPostId')
        if not blog_post_id:
            return JSONResponse(
                content=create_error_response("Blog post ID not found in the response")
            )
            
        # Second API call to get blog content
        blog_api_url = f"https://www.squareyards.com/blog/wp-json/square/dsc-content?post_id={blog_post_id}"
        blog_response = requests.get(blog_api_url)
        
        if not blog_response.ok:
            return JSONResponse(
                content=create_error_response(f"Second API call failed: {blog_response.text}")
            )
            
        # Parse the blog response
        blog_data = blog_response.json()
        
        if not blog_data or len(blog_data) == 0:
            return JSONResponse(
                content=create_error_response("No content found in blog response")
            )
        
        # Get the content and generate FAQs
        original_content = blog_data[0].get('post_content', '')
        faq_content = create_dse_faq(original_content)
        
        # Return success response with structured FAQ content
        return JSONResponse(
            content=create_success_response(faq_content)
        )
            
    except Exception as e:
        return JSONResponse(
            content=create_error_response(str(e)))
    

# OpenAI Chat Completion function
def create_indices(prompt, content):
    try:
        chat_completion = openai.ChatCompletion.create(
            deployment_id="sqy-gpt4o-mini",
            model="sqy-gpt4o-mini",
            temperature=0.7,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"This is the input data for analysis:\n\n{content}"}
            ],
        )
        completion_content = chat_completion.choices[0].message.content
        response = str(completion_content).strip().replace("`", "")
        response = str(completion_content).strip().replace("\n", "")
        return response
    except Exception as e:
        return f"Error: {str(e)}"


@app.post("/generate-indices")
async def generate_all_type_indices(id: str):
    try:
        # Fetch data from the API
        api_url = f"https://rsi.squareyards.com/get-indices-data?localityId={id}"
        response = requests.get(api_url)
        if response.status_code != 200:
            return {"status": 0, "message": f"Failed to fetch data. Status code: {response.status_code}"}

        data = response.json().get("data", {})
        if not data:
            return {"status": 0, "message": "No data found for the given locality ID."}

        # Extract content for OpenAI prompts
        connectivity_content = data.get("connectivity", {})
        lifestyle_content = data.get("lifestyle", {})
        livability_content = data.get("livability", {})
        education_and_health_content = data.get("education & health", {})

        # Send data to OpenAI for processing
        Connectivity_index_response = create_indices(Connectivity_index_prompt, connectivity_content)
        Lifestyle_index_response = create_indices(Lifestyle_index_prompt, lifestyle_content)
        Liveability_index_response = create_indices(Liveability_index_prompt, livability_content)
        Education_and_health_response = create_indices(Education_and_health_prompt, education_and_health_content)

        return {
            "status": 1,
            "Connectivity_index_response": Connectivity_index_response,
            "Lifestyle_index_response": Lifestyle_index_response,
            "Liveability_index_response": Liveability_index_response,
            "Education_and_health_response": Education_and_health_response,
        }

    except Exception as e:
        return {"status": 0, "message": str(e)}