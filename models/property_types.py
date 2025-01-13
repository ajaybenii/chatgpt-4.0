#!/usr/bin/python
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class request_body(BaseModel):
    property_type: str
    listing_type: str
    keywords: str
    locality: str
    city: str
    price: str
    area: int
    area_unit: str
    facing: str
    amenities: str
    furnishing: str
    project: str
    bedrooms: str
    bathrooms: Optional[int]
    parking: Optional[int]
    property_age: Optional[str]
    floor_number: Optional[int]
    total_floor_count: Optional[int]

class PropertyType(str, Enum):
    apartment = 'apartment'
    builder_floor = 'builder_floor'
    land = 'land'
    office_space = 'office_space'
    plot = 'plot'
    penthouse = 'penthouse'
    villa = 'villa'
    independent_house = 'independent_house'
    industrial_plot = 'industrial_plot'
    office_space_in_it_sez = 'office_space_in_it_sez'
    shop = 'shop'
    showroom = 'showroom'
    warehouse = 'warehouse'
    pg = 'pg'
    duplex = 'duplex'
    townhouse = 'townhouse'
    hotel_apartment = "hotel_apartment"
    restraunt = 'restraunt'

class ListingType(str, Enum):
    sale = 'sale'
    rent = 'rent'
    dubai_sale = 'dubai_sale'
    dubai_rent = 'dubai_rent'
    
class ResidentialPropertyType(str, Enum):
    apartment = 'apartment'
    builder_floor = 'builder_floor'
    penthouse = 'penthouse'
    villa = 'villa'
    independent_house = 'independent_house'
    townhouse = 'townhouse'
    Residential_building = 'Residential_building'
    hotel_apartment = "hotel_apartment"
    duplex = 'duplex'

class PayingGuestPropertyType(str,Enum):
    pg = 'pg'

class OfficeSpacePropertyType(str, Enum):
    office_space = 'office_space'
    office_space_sez = 'office_space_sez'
    co_working_space = 'co_working_space'

class CommercialPropertyType(str, Enum):
    shop = 'shop'
    showroom = 'showroom'
    warehouse = 'warehouse'
    restraunt = 'restraunt'
    factory = 'factory'
    labour_camp = 'labour_camp'

class LandPropertyType(str, Enum):
    land = 'land'
    industrial_plot = 'industrial_plot'
    plot = 'plot'
    commercial_plot = 'commercial_plot'
    residential_plot = 'residential_plot'

class BaseListingData(BaseModel):
    property_type: PropertyType
    listing_type: ListingType
    keywords: Optional[str]
    locality: str
    city: str
    price: str
    area: int
    area_unit: str
    facing: Optional[str]
    amenities: Optional[str]

class BaseListingDataupdate(BaseModel):
    property_type: PropertyType
    listing_type: ListingType
    keywords: Optional[str]
    locality: str
    city: str
    price: str
    area: int
    area_unit: str
    amenities: Optional[str]

class ResidentialListingData(BaseListingData):
    property_type: ResidentialPropertyType
    furnishing: str
    project: Optional[str]
    bedrooms: str
    bathrooms: Optional[int]
    parking: Optional[int]
    property_age: Optional[str]
    floor_number: Optional[int]
    total_floor_count: Optional[int]

class ResidentialListingDataupdated(BaseListingDataupdate):
    property_type: ResidentialPropertyType
    furnishing: str
    project: Optional[str]
    bedrooms: str
    bathrooms: Optional[int]
    parking: Optional[int]

class PayingGuestListingData(BaseListingData):
    property_type: PayingGuestPropertyType
    project: str
    suited_for: str
    room_type: str
    food_charges_included: str
    available_for: str

class LandListingData(BaseListingData):
    property_type: LandPropertyType
    plot_number: Optional[str]

class LandListingDataupdated(BaseListingDataupdate):
    property_type: LandPropertyType
    # plot_number: Optional[str]

class OfficeSpaceListingData(BaseListingData):
    property_type: OfficeSpacePropertyType
    office_space_type: str
    pantry: str
    furnishing: str
    washroom_present: str
    parking: Optional[int]
    floor_number: Optional[int]
    total_floor_count: Optional[int]

class OfficeSpaceListingDataupdated(BaseListingDataupdate):
    property_type: OfficeSpacePropertyType
    project: Optional[str]
    furnishing: str
    washroom_present: str
    parking: Optional[int]

class CommercialListingData(BaseListingData):
    property_type: CommercialPropertyType
    furnishing: Optional[str]
    washroom_present: str
    parking: Optional[int]
    floor_number: Optional[int]

class CommercialListingDataupdated(BaseListingDataupdate):
    property_type: CommercialPropertyType
    project: Optional[str]
    furnishing: Optional[str]
    washroom_present: str
    parking: Optional[int]
    # floor_number: Optional[int]

