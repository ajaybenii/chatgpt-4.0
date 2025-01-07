from prompts import format_description


def test_format_description():
    """
    To test the format_description function
    """
    test_description = "A luxurious builder floor is available for rent at Rs 34,000 with total area of 1730 square feet. The spacious property comes with 3 bedrooms, 3 bathrooms and 3 parking spots, making it ideal for family. The property is situated in the prime location of Sushant Lok 1 in Gurgaon. This is an east-facing property in the C Block and is on 2nd floor within a building with 4 floors in total. The age of the property is 5-7 years. It is a furnished property with all essential appliances. The property offers various amenities like medical facilities, a day care center, 24x7 security, water views and more."
    test_formatted_description = {
        "first_paragraph": "A luxurious builder floor is available for rent at Rs 34,000 with total area of 1730 square feet.",
        "body": [
            "The spacious property comes with 3 bedrooms, 3 bathrooms and 3 parking spots, making it ideal for family.",
            "The property is situated in the prime location of Sushant Lok 1 in Gurgaon.",
            "This is an east-facing property in the C Block and is on 2nd floor within a building with 4 floors in total.",
            "The age of the property is 5-7 years.",
            "It is a furnished property with all essential appliances."
        ],
        "last_paragraph": "The property offers various amenities like medical facilities, a day care center, 24x7 security, water views and more."
    }
    formatted_description = format_description(test_description)

    print(formatted_description)
    assert(test_formatted_description == formatted_description)

