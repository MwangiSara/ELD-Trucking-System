from django.shortcuts import render,get_object_or_404
from django.conf import settings
from .models import DailyLog,DutyEvents,Stop,Driver, Trip
from .serializers import TripsSerializer, CreateTripSerializer, DailyLogSerializer, DutyEventSerializer, StopsSerializer, DriverSerializer
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import timedelta,datetime, time
import requests
import math
from django.utils import timezone
from decouple import config
import openrouteservice

# Create your views here.
class TripListCreateView(generics.ListCreateAPIView):
    """List all trips or create a new trip"""
    queryset = Trip.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateTripSerializer
        return TripsSerializer
    
    def perform_create(self, serializer):
        driver = Driver.objects.first()
        trip = serializer.save(driver=driver)
        
        # Generate route and ELD logs after trip creation
        self.generate_trip_route_and_logs(trip)
    
    def generate_trip_route_and_logs(self, trip):
        """Generate route information and ELD logs for the trip"""
        try:
            # Calculate route using OpenRouteService API
            route_data = self.get_route_data(trip)
            
            if route_data:
                self.create_trip_stops(trip, route_data)
                self.generate_daily_logs(trip, route_data)
                
        except Exception as e:
            print(f"Error generating trip data: {e}")
    
    def get_route_data(self, trip):
        """Get route data from OpenRouteService API"""
        api_key = config("ORS_API_KEY")
        client = openrouteservice.Client(key=api_key)

        # Get coordinates for all locations
        pickup = client.pelias_search(text=trip.pickup_location)
        dropoff = client.pelias_search(text=trip.dropoff_location)

        if not pickup['features'] or not dropoff['features']:
            raise ValueError("Could not geocode addresses")

        pickup_coords = pickup['features'][0]['geometry']['coordinates']  # [lon, lat]
        dropoff_coords = dropoff['features'][0]['geometry']['coordinates']

        # Step 2: Request driving directions
        route = client.directions(
            coordinates=[pickup_coords, dropoff_coords],
            profile='driving-hgv',   # 'driving-car' also works
            format='geojson'
        )

        # Extract distance and duration
        summary = route['features'][0]['properties']['summary']
        distance_miles = summary['distance'] / 1609.34
        duration_hours = summary['duration'] / 3600

        return {
            'distance_miles': round(distance_miles, 2),
            'duration_hours': round(duration_hours, 2),
            'waypoints': [
                {'location': trip.pickup_location, 'type': 'pickup'},
                {'location': trip.dropoff_location, 'type': 'dropoff'}
            ],
            'geometry': route['features'][0]['geometry'] 
        }
        
    def create_trip_stops(self, trip, route_data):
        """Create stops based on route data"""
        distance_miles = route_data['distance_miles']
        current_time = timezone.now()
        
        stops = []
        
        # Pre-trip inspection
        stops.append({
            'location': trip.current_location,
            'stop_type': 'pretrip',
            'arrival_time': current_time,
            'departure_time': current_time + timedelta(minutes=30),
            'duration': 0.5
        })
        
        # Fuel stops every 1000
        fuel_stops = max(1, distance_miles // 1000)
        for i in range(fuel_stops):
            fuel_time = current_time + timedelta(hours=4 * (i + 1))
            stops.append({
                'location': f'Fuel Stop {i + 1}',
                'stop_type': 'fuel',
                'arrival_time': fuel_time,
                'departure_time': fuel_time + timedelta(minutes=30),
                'duration': 0.5
            })
        
        # Pickup stop
        pickup_time = current_time + timedelta(hours=2)
        stops.append({
            'location': trip.pickup_location,
            'stop_type': 'pickup',
            'arrival_time': pickup_time,
            'departure_time': pickup_time + timedelta(hours=1),
            'duration': 1.0
        })
        
        # Dropoff stop
        dropoff_time = current_time + timedelta(hours=route_data['duration_hours'] - 1)
        stops.append({
            'location': trip.dropoff_location,
            'stop_type': 'dropoff',
            'arrival_time': dropoff_time,
            'departure_time': dropoff_time + timedelta(hours=1),
            'duration': 1.0
        })
        
        # Post-trip inspection
        stops.append({
            'location': trip.dropoff_location,
            'stop_type': 'posttrip',
            'arrival_time': dropoff_time + timedelta(hours=1),
            'departure_time': dropoff_time + timedelta(hours=1.5),
            'duration': 0.5
        })
        
        # Create stop objects
        for stop_data in stops:
            Stop.objects.create(trip=trip, **stop_data)
    
    def generate_daily_logs(self, trip, route_data):
        """Generate daily ELD logs based on trip data"""
        total_hours = route_data['duration_hours']
        total_miles = route_data['distance_miles']

        current_date = timezone.now().date()
        remaining_hours = total_hours
        remaining_miles = total_miles
        day_count = 0

        # Load constants from settings
        MAX_DRIVING_HOURS = settings.ELD_SETTINGS['MAX_DRIVING_HOURS_PER_DAY']
        REQUIRED_REST = settings.ELD_SETTINGS['REQUIRED_REST_PERIOD_HOURS']
        BREAK_DURATION = settings.ELD_SETTINGS['MANDATORY_BREAK_DURATION']
        DEFAULT_ON_DUTY = 2.0   # inspections, fueling, misc
        DEFAULT_OFF_DUTY = BREAK_DURATION

        while remaining_hours > 0:
            # Respect max driving per day
            daily_driving_hours = min(MAX_DRIVING_HOURS, remaining_hours)

            # Distribute miles proportionally
            daily_miles = (remaining_miles / remaining_hours) * daily_driving_hours if remaining_hours > 0 else 0

            # Create daily log
            daily_log = DailyLog.objects.create(
                trip=trip,
                driver=trip.driver,
                date=current_date + timedelta(days=day_count),
                total_driving_time=daily_driving_hours,
                total_on_duty_time=DEFAULT_ON_DUTY,
                total_off_duty_time=DEFAULT_OFF_DUTY,
                total_sleeper_berth_time=REQUIRED_REST,
                total_driving_miles=daily_miles,
                vehicle_number=f"T{trip.driver.driver_number}"
            )

            # Generate duty events for this day
            self.generate_duty_events(daily_log, daily_driving_hours)

            remaining_hours -= daily_driving_hours
            remaining_miles -= daily_miles
            day_count += 1
    
    def generate_duty_events(self, daily_log, driving_hours):
        """Generate duty events for a daily log"""
        start_time = timezone.make_aware(
            datetime.combine(daily_log.date, time(6, 0))  # Start at 6 AM
        )
        
        events = [
            # Pre-trip inspection
            {
                'duty_event_status': 'on_duty',
                'start_time': start_time,
                'end_time': start_time + timedelta(minutes=30),
                'location': 'Terminal',
                'remarks': 'Pre-trip inspection',
                'truck_moved': False
            },
            # Driving
            {
                'duty_event_status': 'driving',
                'start_time': start_time + timedelta(minutes=30),
                'end_time': start_time + timedelta(hours=driving_hours + 0.5),
                'location': 'On Route',
                'remarks': 'Driving',
                'truck_moved': True
            },
            # 30-minute break
            {
                'duty_event_status': 'off_duty',
                'start_time': start_time + timedelta(hours=4),
                'end_time': start_time + timedelta(hours=4.5),
                'location': 'Rest Area',
                'remarks': '30-minute break',
                'truck_moved': False
            },
            # Sleeper berth
            {
                'duty_event_status': 'sleeper_berth',
                'start_time': start_time + timedelta(hours=driving_hours + 2),
                'end_time': start_time + timedelta(hours=24),
                'location': 'Truck Stop',
                'remarks': '10-hour rest period',
                'truck_moved': False
            }
        ]
        
        for event_data in events:
            DutyEvents.objects.create(daily_log=daily_log, **event_data)


class TripDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific trip"""
    queryset = Trip.objects.all()
    serializer_class = TripsSerializer


class DailyLogListView(generics.ListAPIView):
    """List daily logs for a specific trip"""
    serializer_class = DailyLogSerializer
    
    def get_queryset(self):
        trip_id = self.kwargs.get('trip_id')
        return DailyLog.objects.filter(trip_id=trip_id).order_by('date')


class DutyEventListView(generics.ListAPIView):
    """List duty events for a specific daily log"""
    serializer_class = DutyEventSerializer
    
    def get_queryset(self):
        daily_log_id = self.kwargs.get('daily_log_id')
        return DutyEvents.objects.filter(daily_log_id=daily_log_id).order_by('start_time')


@api_view(['GET'])
def route_data_view(request, trip_id):
    """Get route data with geometry and geocoded coordinates from ORS"""
    trip = get_object_or_404(Trip, id=trip_id)
    stops = Stop.objects.filter(trip=trip).order_by('arrival_time')

    api_key = config("ORS_API_KEY")
    client = openrouteservice.Client(key=api_key)

    # Geocode pickup + dropoff addresses
    pickup = client.pelias_search(text=trip.pickup_location)
    dropoff = client.pelias_search(text=trip.dropoff_location)

    if not pickup['features'] or not dropoff['features']:
        return Response({"error": "Could not geocode addresses"}, status=400)

    pickup_coords = pickup['features'][0]['geometry']['coordinates']  # [lon, lat]
    dropoff_coords = dropoff['features'][0]['geometry']['coordinates']

    # Request driving route
    route = client.directions(
        coordinates=[pickup_coords, dropoff_coords],
        profile="driving-hgv",  # use truck routing
        format="geojson"
    )

    summary = route['features'][0]['properties']['summary']
    distance_miles = summary['distance'] / 1609.34
    duration_hours = summary['duration'] / 3600
    geometry = route['features'][0]['geometry']  # LineString coords

    # response
    route_data = {
        "trip_id": str(trip.id),
        "start_location": trip.current_location,
        "pickup_location": trip.pickup_location,
        "dropoff_location": trip.dropoff_location,
        "stops": StopsSerializer(stops, many=True).data,
        "summary": {
            "distance_miles": round(distance_miles, 2),
            "duration_hours": round(duration_hours, 2),
        },
        "coordinates": {
            "pickup": {"lat": pickup_coords[1], "lng": pickup_coords[0]},
            "dropoff": {"lat": dropoff_coords[1], "lng": dropoff_coords[0]},
        },
        "geometry": geometry  # full map drawing
    }

    return Response(route_data)


@api_view(['GET'])
def driver_stats_view(request, driver_id):
    """Get driver statistics and compliance info"""
    driver = get_object_or_404(Driver, id=driver_id)
    
    # Calculate current cycle hours (last 8 days)
    eight_days_ago = timezone.now().date() - timedelta(days=8)
    recent_logs = DailyLog.objects.filter(
        driver=driver,
        date__gte=eight_days_ago
    )
    
    total_cycle_hours = sum(
        log.total_driving_time + log.total_on_duty_time 
        for log in recent_logs
    )
    
    # Calculate available hours
    max_cycle_hours = 70  # 70-hour/8-day cycle
    available_hours = max_cycle_hours - total_cycle_hours
    
    stats = {
        'driver_name': f"{driver.user.first_name} {driver.user.last_name}",
        'driver_number': driver.driver_number,
        'current_cycle_hours': total_cycle_hours,
        'available_hours': max(0, available_hours),
        'compliance_status': 'compliant' if available_hours > 0 else 'violation',
        'recent_trips': Trip.objects.filter(driver=driver).count()
    }
    
    return Response(stats)