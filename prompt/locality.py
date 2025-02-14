prompt_for_locality = """Your task is to generate a compelling overview of the given locality.  
Make sure the heading and the first sentence of the paragraph are **distinct and engaging** .

### **Instructions:**
1. **Check if the first few lines about the locality can be written based on trending SEO data**, but make sure the content is **unique and not copied from competitors**.
2. The **heading should be unique** and reflect something different about the locality .
3. The **paragraph must have a different starting sentence**. Avoid repetitive phrases like "stands out as" or "located in."
4. Keep it **within 90-120 words** and ensure it appeals to families and professionals.

### **Response Format:**
<h2>[Creative Heading]</h2>  
<p>[SEO-optimized and unique opening line] ... [Description of connectivity, lifestyle, amenities, etc.]</p>

"""

prompt_for_indices = """
                    Given the following raw data in JSON format, create a structured response with across connectivity, lifestyle, education & healthcare, and livability.

                    The format should include the following sections:

                    Connectivity: Summarize the Connectivity into paragrapgh.
                    Education & Healthcare: Summarize the Education & Healthcare into paragrapgh.
                    Lifestyle:  Summarize the Lifestyle into paragrapgh.
                    Livability: Summarize the overall livability into paragrapgh.
                    
                    Ensure the tone is informative, engaging, and focused on the area's strengths. Use proper formatting and bullet points for readability, and make sure to keep the sections concise yet detailed.
                    
                    ##Sample response format should be this :-

                    <h2>Living Essentials: Ratings Across Connectivity, Lifestyle, and More</h>

                    <h4>Connectivity</h4>
                    <p>Connectivity paragrapgh here</p>

                    <h4>Education & Healthcare</h4>
                    <p>Education & Healthcare here</p>

                    <h4>Lifestyle</h4>
                    <p>Lifestyle paragrapgh here</p>

                    <h4>Livability</h4>
                    <p>Livability paragrapgh here</p>"""

market_overview_prompt = """Write a detailed real estate market overview for a specific locality or sector. Ensure the response is structured with proper headings and includes the following:

                    Market Overview: Start with a paragraph introducing the area, its appeal, and its real estate mix.
                    Prominent Developers: Include a paragraph highlighting key real estate developers contributing to the area's growth and quality projects.
                    Key Projects and Developments: Use a bulleted list to categorize:
                    New Launches: Provide a short description using 30-40 words only about new projects and their significance.
                    Ready-to-Move Projects: Provide a short description using 30-40 words only about established housing societies, focusing on amenities and popularity.
                    Under-Construction Projects: Provide a short description using 30-40 words only about ongoing developments with potential for growth.
                    End with a concise summary paragraph (about 30 words) describing the overall project status.
                    

                    ##Sample response format this:
                    also give a sample like this :-
                    <h2>Real Estate Market Overview of {locality name only} </h2>
                    <p>market overview paragrapgh</p>
                    
                    <h4>Leading Real Estate Developers in {locality name only} </h4>
                    <p>Developers  paragrapgh here </p>
                    
                    <h4>Key Projects and Developments</h4>
                    <ul>
                    <li>first key paragraph about New Launches</li>
                    <li>second key paragraph about Ready-to-Move Projects</li>
                    <li>third key paragraph about Under-Construction Projects</li>
                    </ul>
                    <p>about project status paragrapgh in 30 word here</p>"""

supply_demand_prompt = """ Write a detailed analysis of property supply and demand trends for a specific real estate sector or locality. Structure the response with clear headings and include the following points:

                    Property Supply Breakdown:

                    Provide an overview of the property supply in the area, including types of properties available (e.g., apartments, builder floors, villas) with approximate percentages.
                    Highlight the most common property configurations (e.g., 2BHK, 3BHK, 4BHK) and their appeal.
                    Mention the prevalent price ranges and the types of buyers these cater to (e.g., mid-range, premium).
                    
                    Demand Highlights:

                    Discuss the factors driving demand in the area, such as location, amenities, or connectivity.
                    Outline the most in-demand property types and configurations, including percentages if possible.
                    Highlight budget trends, focusing on the most popular price brackets and their significance for homebuyers and investors.
                    Structure the response in a professional yet engaging tone, using bullet points for clarity and conciseness. Format with headings and lists for easy readability.

                    I want only 3-3 bullet points for both Supply Breakdown and Demand Highlights as you can see in sample response format.
                    
                    ##Sample response format:
                    <h2>Property Supply & Demand Trends in {locality name only}</h2>

                    <h4>Supply Breakdown</h4>
                    <p>The locality’s offers a robust mix of properties, making it appealing to a wide audience.</p>
                    <ul>
                    <li>Property Types: write here of 20-25 words</li>
                    <li>Configurations: write here of 20-25 words</li>
                    <li>Price Range: write here of 20-25 words</li>
                    </ul>

                    <h4>Demand Highlights</h4>
                    <p>The locality’s prime location and amenities have spurred consistent demand.</p>

                    <ul>
                    <li>Property Types in Demand: write  here of 20-25 words</li>
                    <li>Preferred Configurations: write here of 20-25 words</li>
                    <li>Budget Trends: write here of 20-25 words</li>
                    </ul>

                    """