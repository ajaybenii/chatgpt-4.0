sample_response_format= """
<div class='main chatGPT'> <div class='heading'><strong>Welcome to 140 Widdicombe Hill Blvd</strong></div> <div class='para'> <p>Located in the Willowridge-Martingrove-Richview neighbourhood in Toronto, this property offers a great opportunity for those looking to purchase a home in this area.</p> </div> <div class='info'> <strong>Here are some key details about this property:</strong> <ul> <li>There are currently 2 listings available for sale in 140 Widdicombe Hill Blvd, with a price of $730,000 each.</li> <li>The exterior finish of this building is concrete, providing a modern and durable look.</li> <li>Each unit in property comes with an owned locker, offering additional storage space for your belongings.</li> <li>The laundry facilities in 140 Widdicombe Hill Blvd are ensuite and located on the main level, providing convenience and privacy.</li> <li>Enjoy the terrace in 140 Widdicombe Hill Blvd, perfect for relaxing and enjoying the outdoor space.</li> <li>High-speed internet is available in this building, ensuring you stay connected at all times.</li> <li>140 Widdicombe Hill Blvd also features an underground garage, providing secure parking for residents.</li> <li>Building insurance is included in 140 Widdicombe Hill Blvd, giving you peace of mind.</li> </ul> </div> </div>"""

canada_prompt = f"""
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


Like this format example :- {sample_response_format}

Above is just sample format, only generate that bullet points which data is given to you , don't add additionl points details in description response and don't write or mention any Note in the end of response.
"""

Canada_description_prompt2 = """
You are a real-estate agent. Generate a concise project description in two paragraphs based on the provided input data:
Instructions:

1.Ensure the descriptions are SEO-friendly, utilizing relevant keywords naturally.
2.Write the description in easy English.
3.To generate description only use provide key value data, don't add additionl details in description response.

Ensure the response is formatted as:
<p>First paragraph content.</p>
<p>Second paragraph content.</p>
"""