# import requests
# import math
# from datetime import datetime, timedelta
# from django.utils import timezone
# from typing import List, Dict, Any

# class RouteCalculatorService():
#     """Handles route calculation, distance, and estimated travel time using a map API."""
#     def __init__(self):
#         self.max_drive_time = 11 # 11 hrs limit
#         self.max_cycle_hours = 70 #70hrs/8days
#         self.max_on_duty_hours = 14 #14 hrs on-duty hrs
#         self.required_rest_minutes = 30  # 30 minute break
#         self.required_rest_after_hours = 8 # 8 hours driving
#         self.max_distance_without_fuel = 1000  # mile

#     def calculate_routes_with_stops(self,current_location:str,  dropoff_location:str, pickup_location:str,current_cycle_used: float):
#         # get coodinates
#         current_coords = self._coord_location(current_location)
#         pickup_coords = self._coord_location(pickup_location)
#         dropoff_coords = self._coord_location(dropoff_location)

#         section1 = self._calculate_route_section(current_coords, pickup_coords)
#         section2 = self._calculate_route_section(pickup_coords, dropoff_coords)

#         total_distance = section1['distance'] + section2['distance']
#         total_duration = section1['duration'] + section2['duration'] + 120  # plus 2 hrs

#         def _geocode_location(self, location: str) -> Dict[str, float]:
#             """Geocode a location using OpenStreetMap Nominatim"""
#         try:
#             url = 'https://nominatim.openstreetmap.org/search'
#             params = {
#                 'q': location,
#                 'format': 'json',
#                 'limit': 1,
#                 'countrycodes': 'us'
#             }
            
#             response = requests.get(url, params=params, timeout=10)
#             response.raise_for_status()
            
#             results = response.json()
#             if results:
#                 return {
#                     'lat': float(results[0]['lat']),
#                     'lng': float(results[0]['lon']),
#                     'name': results[0]['display_name']
#                 }
#             else:
#                 raise ValueError(f"Location not found: {location}")
                
#         except Exception as e:
#             # Fallback to some default coordinates if geocoding fails
#             # In production, you'd want better error handling
#             raise ValueError(f"Geocoding failed for {location}: {str(e)}")
    

    
