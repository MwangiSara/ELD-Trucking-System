from rest_framework import serializers
from .models import DailyLog, Stop, Trip, Driver,DutyEvents
from datetime import time


class DailyLogSerializer(serializers.ModelSerializer):
    """Serializes DailyLog data including driver name and duty hour totals."""
    driver_name = serializers.SerializerMethodField()

    class Meta:
        model = DailyLog
        fields = ['id','date','driver_name','total_off_duty_time','total_sleeper_berth_time','total_driving_time','total_on_duty_time','total_driving_miles','vehicle_number','trailer_number','shipper_name','shipper_commodity','load_number']

    def get_total_hours_spent(self,obj):
        """Returns the total duty time (all statuses combined) in hours."""
        total_minutes = (obj.total_off_duty_time + obj.total_sleeper_berth_time + obj.total_driving_time + obj.total_on_duty_time)
        return round(total_minutes / 60 , 2) 
    
    def get_driving_hours(self,obj):
        """Returns the total driving time in hours for the day."""
        return round(obj.total_driving_time / 60, 1) 
    
    def get_duty_hours(self, obj):
        """Returns the combined on-duty and driving time in hours for the day."""
        return round((obj.total_driving_time + obj.total_on_duty_time) / 60, 1) #driving + on-duty hrs
    
    def get_driver_name(self, obj):
        """Returns the drivers full name (first + last)."""
        return f"{obj.driver.user.first_name} {obj.driver.user.last_name}"

class StopsSerializer(serializers.ModelSerializer):
    """Serializes Stop objects for trip detail views."""
    class Meta:
        model = Stop
        fields = ['location', 'stop_type', 'arrival_time', 'depature_time', 'duration']

class DriverSerializer(serializers.ModelSerializer):
    """Serializes Driver data including name, driver number, initials, and home base."""
    driver_name = serializers.SerializerMethodField()
    class Meta:
        model = Driver
        fields = ['driver_name', 'driver_number', 'initials', 'home_operation_center']

    def get_driver_name(self, obj):
            return f"{obj.user.first_name} {obj.user.last_name}"


class TripsSerializer(serializers.ModelSerializer):
    """Serializes Trip data with driver name, related logs, and stops."""
    driver_name = serializers.SerializerMethodField()
    daily_logs = serializers.SerializerMethodField()
    stops = StopsSerializer(many=True, read_only=True)
    class Meta:
        model = Trip
        fields = [
            'id', 'current_location', 'pickup_location', 'dropoff_location',
            'current_cycle_used', 'drive_time', 'daily_logs', 'stops', 'driver_name'
        ]


    read_only_fields = ['id', 'created_at', 'drive_time']

    def get_daily_logs(self, obj):
        """Fetches and serializes all DailyLogs linked to a given Trip."""
        logs = DailyLog.objects.filter(trip=obj).order_by('date')
        return DailyLogSerializer(logs, many=True).data
    
    def get_driver_name(self, obj):
        """Returns the drivers full name (first + last)."""
        return f"{obj.driver.user.first_name} {obj.driver.user.last_name}"

class CreateTripSerializer(serializers.ModelSerializer):
    """Serializer for creating a new Trip with essential trip details."""
    class Meta:
        model = Trip
        fields = ['current_location','pickup_location','dropoff_location','current_cycle_used']

class DutyEventSerializer(serializers.ModelSerializer):
    """Serializes DutyEvents with status, times, location, remarks, and movement flag."""
    class Meta:
        model = DutyEvents
        fields = ['duty_event_status', 'start_time', 'end_time','truck_moved', 'location',  'remarks']

    def get_duration(self,obj):
        """Calculates the duration of a duty event in minutes based on start and end times."""
        if obj.start_time and obj.end_time:
            diff = obj.end_time - obj.start_time
            return int(diff.total_seconds() / 60)
        return 0