Connectivity_index_prompt = """Data Analysis Request: Location-Based Connectivity Index Description Generation

Purpose:
As a proptech company, we need to generate dynamic, concise descriptions that explain our Connectivity Index ratings for different localities on our location pages.

Output Requirements:
Generate Only 3 distinct bullet points that:

1. Mention the total count of available transportation options in the locality (bus stops, metro stations, railway stations).
2. Highlight nearby transportation options for each category, if available.
3. Explain how the available transportation options contribute to the overall connectivity of the locality.

Each bullet point should be concise, with a maximum of 8-9 words, and focus on the positive aspects of the locality’s connectivity. Avoid using negative language such as "lacks" or "no metro." Instead, emphasize the existing infrastructure and its positive impact on connectivity.

Final sample response format:

<ul>
  <li>Transportation options: 10 bus stops enhancing connectivity.</li>
  <li>Nearby metro stations boost access to major areas.</li>
  <li>Extensive bus routes ensure seamless local and regional travel.</li>
</ul>
"""


Lifestyle_index_prompt = """Data Analysis Request: Location-Based Lifestyle Index Description Generation

Purpose:
As a proptech company, we need to generate comprehensive yet concise descriptions that explain our Lifestyle Index ratings for different localities, focusing on shopping, entertainment, and dining amenities.


Output Requirements:
Generate Only 3 distinct bullet points that:
1. Highlight the shopping infrastructure, emphasizing major retail presence (supermarkets, malls) and specialty stores.
2. Describe entertainment and recreational facilities, focusing on leisure options and fitness amenities.
3. Showcase the dining and hospitality scene, including restaurants, cafes, and food establishments.

Each bullet point should:
- Be limited to 8-9 words maximum
- Focus on positive aspects of lifestyle amenities
- Avoid negative language or mentioning absences
- Emphasize convenience and quality of life benefits

Key Guidelines:
- Ensure descriptions are unique per locality
- Use natural, engaging language
- Avoid repetitive phrases
- Consider the density and diversity of amenities
- Factor in accessibility to various lifestyle facilities
- Include mix of essential and leisure amenities
- Reflect the relative importance values of different amenities


Final sample response format:

<ul>
  <li>Transportation options: 10 bus stops enhancing connectivity.</li>
  <li>Nearby metro stations boost access to major areas.</li>
  <li>Extensive bus routes ensure seamless local and regional travel.</li>
</ul>

"""

Liveability_index_prompt = """Data Analysis Request: Location-Based Liveability Index Description Generation

Purpose:
As a proptech company, we need to generate comprehensive descriptions that communicate our Liveability Index ratings for different localities, encompassing six major categories: Connectivity, Education, Healthcare, Spiritual & Religious, Shopping & Retail, and Entertainment & Dining.


Output Requirements:
Generate Only 3 distinct bullet points :
1. Highlight essential infrastructure (transportation and healthcare), emphasizing high-importance facilities (Airport: 10, Hospital: 10, Metro: 9)
2. Showcase lifestyle amenities (shopping, entertainment, dining), focusing on key facilities (Supermarket: 9, Shopping Mall: 8, Restaurant: 8)
3. Describe community facilities (education, spiritual centers), reflecting social infrastructure (Colleges: 8, Schools: 7)

Each bullet point should:
- Be limited to 8-9 words maximum
- Prioritize amenities based on their importance values
- Focus on accessibility and convenience
- Emphasize density and diversity of facilities
- Avoid negative language or missing amenities

Key Guidelines:
- Generate unique descriptions per locality
- Use natural, engaging language
- Consider all three factors: Density, Diversity, and Accessibility
- Weight descriptions based on importance values (4-10 scale)
- Balance essential services with lifestyle amenities
- Factor in both immediate and surrounding area facilities
- Include multi-modal transportation options
- Reflect the holistic nature of liveability

Category Weightage Considerations:
High Priority (8-10):
- Airport, Hospitals, Metro Stations, Supermarkets
- Railway Stations, Shopping Malls, Colleges, Parks

Medium Priority (6-7):
- Schools, Bus Stops, Cinema Halls, Restaurants
- Hotels, Clinics, Gyms, Bus Depots

Basic Priority (4-5):
- Religious Facilities, Retail Stores, Food Outlets
- Spiritual Centers, Home Decor
Final sample response format:

<ul>
  <li>Transportation options: 10 bus stops enhancing connectivity.</li>
  <li>Nearby metro stations boost access to major areas.</li>
  <li>Extensive bus routes ensure seamless local and regional travel.</li>
</ul>
"""

Education_and_health_prompt = """Data Analysis Request: Location-Based Education & Health Index Description Generation

Purpose:
As a proptech company, we need to generate precise descriptions that communicate our Education & Health Index ratings for different localities, focusing on educational institutions and healthcare facilities.


Output Requirements:
For each locality, generate Only 3 distinct bullet points that:
1. Highlight healthcare infrastructure, emphasizing hospital accessibility and clinic distribution
2. Showcase educational facilities, focusing on school and college presence
3. Describe the combined benefits of healthcare and education proximity

Each bullet point should:
- Be limited to 8-9 words maximum
- Prioritize facilities based on importance values (Hospital: 10, Colleges: 8, Schools: 7, Clinics: 6)
- Focus on all three aspects: density, diversity, and accessibility
- Emphasize positive aspects of available facilities
- Avoid negative language or highlighting absences

Key Guidelines:
- Generate unique descriptions per locality
- Use clear, professional language
- Avoid repetitive phrasing
- Consider facility hierarchy based on importance values
- Factor in both immediate and surrounding area access
- Balance primary healthcare with specialized facilities
- Consider both primary education and higher education
- Reflect the complementary nature of education and healthcare

Priority Considerations:
Critical Priority (10):
- Hospitals (primary healthcare centers)

High Priority (7-8):
- Colleges and Universities
- Schools

Supporting Priority (6):
- Clinics (specialized healthcare)

Evaluation Metrics:
- Density: Number of facilities in the area
- Diversity: Variety of facility types
- Accessibility: Ease of reaching facilities

Final sample response format:

<ul>
  <li>Transportation options: 10 bus stops enhancing connectivity.</li>
  <li>Nearby metro stations boost access to major areas.</li>
  <li>Extensive bus routes ensure seamless local and regional travel.</li>
</ul>
"""