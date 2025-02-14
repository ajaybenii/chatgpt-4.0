from dotenv import load_dotenv

import os
import re
import json
import time
import openai
import random
import datetime
import requests
import replicate

from groq import Groq
from io import BytesIO
from fastapi import FastAPI
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

from google.cloud import storage
from fastapi.param_functions import Query


app = FastAPI(
    title="Minite GPT3",
    description="Generates description for real estate listings from the listing parameters",
    version="2.0.0"
)

# loading environment variables from .env file
load_dotenv()

#Openai setup
openai.api_type = "azure"
openai.api_key = "f379f0f5e9e042289297765f32320268"
openai.api_base = 'https://sqy-openai.openai.azure.com/'
openai.api_version = "2023-05-15"

# #Groq setup
# groq_api_key = os.getenv("GROQ_API_KEY")
# if groq_api_key is None:
#     raise ValueError("API key not found. Set the GROQ_API_KEY environment variable.")
# GROQ_API_KEY="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"
client_groq = Groq(api_key="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")

# Add your WordPress API URL
wordpress_api_url = 'https://www.squareyards.com/blog/wp-json/square/news-post-content'

def extract_names_from_text(text):
    completion = openai.ChatCompletion.create(
        deployment_id="sqy-gpt-35-turbo-16k",
        model="sqy-text-embedding-ada-002",
        temperature=1.3,
        messages=[
            {"role": "system", "content": str(f"Extract the name of the real estate developer if mentioned in the following mixed text data otherwise gave NA response,i just need exact name mention in mix data like this : ('tag':'Godrej') and also i want city and locality name like this:('New Delhi') and provide the response with each part on a new line like this :- Name: Macrotech Developers \nCity: Mumbai \nLocality: Mumbai Metropolitan Region and Pune")},

            {"role": "user", "content": (str(text))}
        ]
    )

    response_dev_name = completion.choices[0].message['content']

    name_start = response_dev_name.find("Name:")
    name_end = response_dev_name.find("City:")
    name_prefix_length = len("Name:")
    dev_name = response_dev_name[name_start + name_prefix_length:name_end].strip()

    city_start = response_dev_name.find("City:")
    city_end = response_dev_name.find("Locality:")
    city_prefix_length = len("City:")
    city_name = response_dev_name[city_start + city_prefix_length:city_end].strip()

    locality_start = response_dev_name.find("Locality:")
    locality_prefix_length = len("Locality:")
    locality_name = response_dev_name[locality_start + locality_prefix_length:].strip()
    return {"name": dev_name,
            "City": city_name,
            "locality_name": locality_name
            }

def upload_image(local_image_path):
        credentials_path = "sqy-prod-e00ffd95e2ce.json"

        # Initialize a GCS client
        cloud_client = storage.Client.from_service_account_json(credentials_path)

        # Define your GCS bucket name
        bucket_name = "sqydocs"


        gcs_image_path = f"rcheck/projectvideos/{local_image_path}"
        bucket = cloud_client.get_bucket(bucket_name)
        blob = bucket.blob(gcs_image_path)
        blob.upload_from_filename(local_image_path)

        gcs_base_url = f"https://img.squareyards.com/{bucket_name}/"
        image_url = gcs_base_url + gcs_image_path
        image_url = str(image_url).replace("/sqydocs", "")

        return image_url

def Etrealty_news_generated(url):

    current_datetime = datetime.datetime.now()
    current_date_str = current_datetime.date().strftime("%Y%m%d")
    current_time_str = current_datetime.time().strftime("%H%M%S")

    local_time = current_date_str + current_time_str

    
    try:
        response = requests.get(url)
    except:
        return {"Realty ecnomictimes website server slow, Hit again"}

    if response.status_code == 200:
        raw_headline = str(url).split("/")[-2]
        formatted_headline = raw_headline.replace("-", " ").capitalize()
        guid_response = requests.get(url)
        soup = BeautifulSoup(guid_response.text, 'html.parser')
        text_data = soup.get_text()
        final_result1 = text_data.replace("\n", '')
        description = re.sub(r"[\([{})\]]", "", final_result1)
        data = (description + '\n')

        extracted_devep = extract_names_from_text(data)

        possible_sample = {
            "second" : """<h2>Sample Subheadline 1</h2>
                <p>Write the content here and should be contain 200-300 words.</p>
                    """,
        "first" : """<h2>Sample conclusion </h2>
                        <p>Write conclusion paragraph here and should be contain 200-300 words, offering additional context or insights.</p>
                """,
            "third" : """<h2>Sample Conclusion</h2>
                    <p>Write conclusion paragraph and should be contain 50-80 words, offering additional context or insights.</p>
                    <p>
                    <ul>
                        <li>First bullet point</li>
                        <li>Second bullet point</li>
                        <li>Third bullet point</li>
                        <li>fourth bullet point</li>
                        <li>fifth bullet point</li>
                        <li>sixth bullet point</li>
                    </ul>
                    </p>
                    """
        }
        
        # Select a random position
        random_sample_selection = random.choice(list(possible_sample.keys()))
        final_sample = possible_sample[random_sample_selection]
        
        prompt = f"""You are a journalist of Square Times Bureau for a renowned news outlet, tasked with creating SEO-friendly, compelling, and well-structured news articles based on the data provided to you.

            Your goal is to craft an in-depth news article with bold and concise subheadlines that break down the content into digestible sections. The content may include updates on recent developments, announcements, or events across various sectors, such as real estate, technology, industry, or infrastructure.
            The sentance line not more than 20 words.
            The article should adhere to the following guidelines:

            1. SEO-Friendly: Ensure the use of relevant keywords naturally throughout the article to improve search engine visibility.
            2. Informative: Accurate and well-researched information relevant to the topic.
            3. Engaging: Write captivating content that grabs the reader's attention while maintaining a professional tone.


            Start with direct news paragrapgh below is sample.
            Note- I want All paragrapghs length should be more than 250 words.

            ### final Response Format should be this:
            <p>First paragraph: Provide an overview of the news, covering the key points and background in 200-300 words.</p>

            <h2>Sample Subheadline 1</h2>
            <p>Write the first section’s content here, elaborating on the details with 200-350 words.</p>

            <h2>Sample Subheadline 2</h2>
            <p>Write the second section’s content here, including 200-350 words.</p>
            <p>Write additional paragraph text here, ensuring it is between 200-300 words for further elaboration.</p>
            
            {final_sample}
            """

        
        chat_completion = openai.ChatCompletion.create(
                    deployment_id="sqy-gpt4o-mini",
                    model="sqy-gpt4o-mini",
                    temperature=0.7,
                    messages=[
                        {
                            "role": "system", 
                            "content": prompt
                        },

                        {
                            "role": "user", 
                            "content": f"This is a raw text : {data}"
                            }
                    ]
                )
        news_content=  chat_completion.choices[0].message['content']

                # Extract the HTML part of FAQ response
        start_index = news_content.find('<p>')  # Find the starting index of '<p>'
        end_index = news_content.rfind('</p>')  # Find the last occurrence of '</p>'

        if start_index != -1 and end_index != -1:
            news_content = news_content[start_index:end_index + len('</p>')]
        else:
            news_content = news_content 

        # print("news_content: ",news_content)


        headline_prompt = "Here is a news headline. Re-write it concisely with minor changes, maintaining the same meaning and agenda, in 8 to 9 words."

        chat_completion_headline = client_groq.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": headline_prompt
                },
                {
                    "role": "user",
                    "content": f"This is the line: \n\n {formatted_headline}"
                }
            ],
            model="llama-3.1-8b-instant"
        )
        headline = chat_completion_headline.choices[0].message.content
        headline = headline.replace('"', '')
        headline = re.sub(r'\.$', '', headline)
        # print("headline - ",headline)
        here_text_line = headline

        # print("text_line: ",here_text_line)
        local_image_path = f"image-{local_time}.png"

        # Initialize the client
        client = replicate.Client(api_token="3cc9aad598a3d99182e29f8a09bbcbdc01851719")
        
        # Define the input parameters
        
        inputs = {
            "prompt": f"Create Clear and clean Image. Ensure the theme of the image aligns with this line: {headline}.",
            "aspect_ratio": "1:1",
            "output_format": "webp",
            "output_quality": 100,
            "safety_tolerance": 2,
            "prompt_upsampling": True
        }
        
        try:
        # Create and start the prediction
            prediction = client.predictions.create(
                # model="black-forest-labs/flux-1.1-pro",
                model= "black-forest-labs/flux-schnell",
                input=inputs
            )
            
            # Get the prediction
            while prediction.status != "succeeded":
                prediction.reload()
                # print(f"Status: {prediction.status}")
                if prediction.status == "failed":
                    
                    raise Exception("Image generation failed")
                    
                time.sleep(1)
                
            
            # Get the output URL - handle both list and dictionary output formats
            get_image_url =  prediction.output

        except Exception as e:
            print(f"Error generating image: {str(e)}")
            raise Exception("Image generation failed")
        
        response_data = get_image_url[0]
        # print("image url =",response_data)

        image_response = requests.get(response_data)
        img = Image.open(BytesIO(image_response.content))
        
        # Add logo
        try:
            logo_path = "new-logo.png"
            logo = Image.open(logo_path)
            logo_aspect_ratio = logo.width / logo.height
            logo = logo.resize((128, int(128 / logo_aspect_ratio)))  # Maintain aspect ratio
            img.paste(logo, (img.width - logo.width - 10, 10), mask=logo)
        except FileNotFoundError:
            print("Logo file not found. Skipping logo overlay.")
        
        # Add text overlay (headline)
        draw = ImageDraw.Draw(img)
        text_line = here_text_line  # Replace with your generated text
        
        font_list = [
                        #Bold and Modern Fonts
                        "impact.ttf",
                        "Impacted.ttf", 
                    ]

        try:
            selected_font = random.choice(font_list)
            # print(("font= ",selected_font))
            font = ImageFont.truetype(selected_font, 48)  # Fixed size 36
        except IOError:
            print("Font not found or invalid. Using default font.")
            font = ImageFont.load_default()
        
        # Break text into multiple lines after every 2 words
        words = text_line.split()
        lines = [' '.join(words[i:i + 3]) for i in range(0, len(words), 3)]
        text_block = '\n'.join(lines)
        
        # Calculate text dimensions
        bbox = draw.multiline_textbbox((0, 0), text_block, font=font, spacing=10)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]+10
        
        # Define possible text positions with padding
        img_width, img_height = img.size
        padding = 80  # Space from boundaries
        possible_positions = {
            # "top_center": ((img_width - text_width) // 2, padding),
            "left_center": (padding, (img_height - text_height) // 2),
            # "right_center": (img_width - text_width - padding, (img_height - text_height) // 2),
            # "bottom_center": ((img_width - text_width) // 2, img_height - text_height - padding),
            "bottom_left": (padding, img_height - text_height - padding),  # New bottom-left position
        }
        
        # Select a random position
        random_position_name = random.choice(list(possible_positions.keys()))
        text_position = possible_positions[random_position_name]
        
        # Draw semi-transparent rectangle behind text
        background_position = (
            text_position[0] - 20,
            text_position[1] - 20,
            text_position[0] + text_width + 20,
            text_position[1] + text_height + 30
        )
        text_background_color = (0, 0, 0, 128)  # Semi-transparent black background (RGBA)
        img = img.convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(background_position, fill=text_background_color)
        img = Image.alpha_composite(img, overlay)
        
        # Draw the text on the image
        draw = ImageDraw.Draw(img)
        draw.multiline_text(text_position, text_block, fill=(255, 255, 255), font=font, spacing=10)
        
        # Convert back to RGB for saving
        img = img.convert("RGB")
        
        # Save and display the image
        ##  local_image_path = "/app/web/chatgpt-newsblog/output_image.png"
        img.save(local_image_path)
        # img.show()

        image_url = upload_image(local_image_path)
        os.remove(local_image_path)

        wordpress_data = {
            'post_title': headline,
            'post_content': news_content,
            'post_image': image_url,
            "builder": extracted_devep["name"],
            "city": extracted_devep["City"],
            "locality": extracted_devep["locality_name"],
            "news_type": "ET-Realty",
            "news_url": f"{url}"
        }

        # print(wordpress_data)
        wordpress_response = requests.post(wordpress_api_url, json=wordpress_data)

        if wordpress_response.status_code == 200:
            return {"Response":"News article of ET-Realty is generated successfully."}
        else:
            return json.dumps({"message": f"Failed to post to WordPress API. Status code: {wordpress_response.status_code}"})
        
    else:
        return {"message": f"Failed to retrieve the page. Status code: {response.status_code}"}

# # # Example usage in a loop
# url = "https://realty.economictimes.indiatimes.com/rss/recentstories"
# try:
#     response = requests.get(url)
# except:
#     response = requests.get(url)

# if response.status_code == 200:
#         soup = BeautifulSoup(response.text, 'xml')
#         guid_elements = soup.find_all("guid")
#         guid_list = [guid.text for guid in guid_elements]
#         # print("total url = ",len(guid_list))
#         n=1
#         for news_number in range(len(guid_list)+1):
#         # for news_number in range(1):   
#             start_time = time.time()  # Record the start time
#             result = generate_news(news_number)
#             print(f"{n}. news article generaterd successfully.",result)
#             n+=1

#             end_time = time.time()  # Record the end time
#             time_taken = end_time - start_time  # Calculate the time taken
            
#             print(f"Time taken for this iteration: {time_taken:.2f} seconds")    
