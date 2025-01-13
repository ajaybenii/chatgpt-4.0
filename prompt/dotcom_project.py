# Prompts
html_sample_overview = """<p>
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

overview_prompt = f"""
You are real-estate agent. I will give you details of a real-estate project. Your task is generate the project description that should be SEO-Friendly. The content should include the following sections:
- Using all provided details generate project description and description should be divided into 3 large paragraph's only and not more than 1-2 line about amenties and specifications in description.
- Generate a available unit option table. Ensure the prices are clearly labeled with 'Lac' or 'Cr' for clarity.")

Note :- Begin direct with description, don't write any line in starting of final response

this is the sample format, i want response in this format without any syntax error:-
{html_sample_overview}

-Above sample is just format , dont use its value.
"""

overview_prompt_less_data = """
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