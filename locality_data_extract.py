import requests
from typing import Dict, List, Union


class DataExtractor:
    def __init__(self, json_data: Dict):
        """Initialize with JSON data."""
        self.json_data = json_data.get('data', {})

    def get_basic_info(self) -> str:
        """Get basic information about the location."""
        pincode = self.json_data.get('pincode', '')
        return f"{self.json_data.get('name', '')}, {pincode}" if pincode else self.json_data.get('name', '')
        
    def get_nearby_localities(self) -> List[Dict]:
        """Get information about nearby localities."""
        localities = self.json_data.get('nearByLocalities', [])
        processed_localities = []
        
        for locality in localities:
            processed_locality = {
                'name': locality.get('subLocalityName', ''),
                'city': locality.get('cityName', ''),
                'distance_km': round(locality.get('distance', 0), 2),
                'rental_info': {
                    'available_units': locality.get('rent', {}).get('available', 0),
                    'avg_price_per_sqft': locality.get('rent', {}).get('avgPricePerSqFt', 0)
                },
                'sale_info': {
                    'available_units': locality.get('sale', {}).get('available', 0),
                    'avg_price_per_sqft': locality.get('sale', {}).get('avgPricePerSqFt', 0)
                }
            }
            processed_localities.append(processed_locality)
        
        return processed_localities

    def get_supply_demand(self) -> Dict:
        """Get supply and demand statistics."""
        supply_demand = self.json_data.get('supplydemand', {})
        
        def process_category_data(category_data: Dict) -> Dict:
            return {
                'unit_types': category_data.get('unitType', []),
                'property_types': category_data.get('propertyType', []),
                'price_ranges': category_data.get('totalPrice_range', [])
            }
        
        return {
            'sale': process_category_data(supply_demand.get('sale', {})),
            'rent': process_category_data(supply_demand.get('rent', {}))
        }

    def get_indices_data(self) -> Dict:
        """Get indices data including connectivity, lifestyle, livability, and education."""
        indices = self.json_data.get('indicesdata', {})
        
        def process_facility(facility_data: Dict) -> Dict:
            """Process facility data, excluding nameswithlatlng."""
            return {
                'count': facility_data.get('count', 0),
                'names': facility_data.get('names', [])
            }
        
        def process_category(category_data: Dict) -> Dict:
            """Process category data, recursively cleaning facilities."""
            result = {}
            for key, value in category_data.items():
                if isinstance(value, dict):
                    if 'count' in value and 'names' in value:
                        result[key] = process_facility(value)
                    else:
                        result[key] = process_category(value)
            return result

        def process_index(index_data: Dict) -> Dict:
            """Process main index categories with text fields."""
            if not index_data:
                return {}
            
            facilities = {}
            for key, value in index_data.items():
                if isinstance(value, dict) and key not in ['Rating']:
                    facilities[key] = process_category(value)
            
            return {
                'text': index_data.get(f"{category.lower()}_text", ''),
                'facilities': facilities
            }
        
        processed_data = {}
        for category in ['connectivity', 'lifestyle', 'livability', 'education & health']:
            category_data = indices.get(category, {})
            processed_data[category] = process_index(category_data)
        
        return processed_data


    def get_developers_data(self) -> Dict:
        """Get information about developers and their projects."""
        dev_data = self.json_data.get('developerswithgrade', {})
        
        return {
            'developers': {
                grade['grade']: grade['developers']
                for grade in dev_data.get('developerData', [])
            },
            'projects': {
                grade['grade']: {
                    status['status']: status['projects']
                    for status in grade.get('statuses', [])
                }
                for grade in dev_data.get('projectData', [])
            }
        }

    def get_connecting_roads(self) -> List[Dict]:
        """Get information about connecting roads."""
        roads = self.json_data.get('connectingroads', [])
        
        return [{
            'name': road.get('name', ''),
            'distance': float(road.get('distance', 0)),
            'keyword': road.get('keyword', '')
        } for road in roads]

    def get_avg_price(self) -> Dict[str, str]:
        """Get average price information."""
        price_data = self.json_data.get('avgprice', {})
        return {
            'sale': price_data.get('sale', 'N/A'),
            'rent': price_data.get('rent', 'N/A')
        }

    def get_metro_stations(self) -> Dict[str, List[str]]:
        """Get metro station names, limited to the first three."""
        metro_stations = self.json_data.get('metrostations', [])
        if metro_stations:
            # Get the first three stations, or fewer if there are not enough
            station_names = [station['searchtext'] for station in metro_stations[:3]]
            return {'Nearby Metrostations': station_names}
        return {''}