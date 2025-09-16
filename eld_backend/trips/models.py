from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

# Create your models here.

class Driver(models.Model):
    """Represents a driver in the system, linked to a Django User. Stores driver-specific identifiers"""
    user =  models.OneToOneField(User, on_delete=models.CASCADE)
    driver_number= models.CharField(max_length=10)
    initials = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)
    home_operation_center = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username} - {self.driver_number}"


class Trip(models.Model):
    """Represents a trucking trip for a driver. Trip fields:id,driver,Current location, Pickup location, Dropoff location, Current Cycle Used (Hrs) """
    id = models.UUIDField(primary_key=True, editable=False,default=uuid.uuid4)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    current_location = models.CharField(max_length=255)
    pickup_location= models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    current_cycle_used = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    drive_time = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['updated_at']
    
    def __str__(self):
        return f"Trip {self.id}: {self.pickup_location} to {self.dropoff_location}"


class Stop(models.Model):
    """Represents a stop event during a trip. Can be fueling, rest, pickup, dropoff, loading/unloading, or inspections. Tracks location, type of stop, arrival/departure times, and duration."""
    STOPS_TYPES = [
        ('fuel','Fuel Stop'),
        ('rest', 'Rest Stop'),
        ('pretrip', 'Pre-Trip Inspection'),
        ('posttrip', 'Post-Trip Inspection'),
        ('pickup', 'Pickup Location'),
        ('dropoff', 'Dropoff Location'),
        ('loading','Loading Freight'),
        ('offloading','Offloading Freight')
    ]
    trip = models.ForeignKey(Trip,on_delete=models.CASCADE, related_name='stops')
    location = models.CharField(max_length=255)
    stop_type= models.CharField(max_length=255, choices=STOPS_TYPES)
    arrival_time = models.DateTimeField()
    depature_time = models.DateTimeField()
    duration = models.FloatField()

    class Meta:
        ordering = ['arrival_time']

class DailyLog(models.Model):
    """Represents a driver’s daily log sheet. Aggregates duty times (off-duty, sleeper, driving, on-duty) and daily mileage. Stores vehicle, trailer, shipper, and commodity information."""
    id = models.UUIDField(primary_key=True, editable=False,default=uuid.uuid4)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='daily_logs')
    driver= models.ForeignKey(Driver, on_delete=models.CASCADE)
    date= models.DateField()
    total_off_duty_time = models.FloatField(default=0)
    total_sleeper_berth_time = models.FloatField(default=0)
    total_driving_time = models.FloatField(default=0)
    total_on_duty_time = models.FloatField(default=0)
    total_driving_miles = models.FloatField()
    vehicle_number = models.CharField(max_length=50, default='P0000')
    trailer_number= models.CharField(max_length=50, default='T00000')
    shipper_name = models.CharField(max_length=255, blank=True)
    shipper_commodity = models.IntegerField(blank=True, null=True)
    load_number = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['date', 'driver']
    
    def __str__(self):
        return f"ELD log {self.date} by {self.driver.user.username}"
    
class DutyEvents(models.Model):
    """Represents a single duty event (status change) within a drivers day."""
    DUTY_EVENT_TYPE = [
        ('off_duty', 'Off Duty'),
        ('sleeper_berth', 'Sleeper Berth'),
        ('driving', 'Driving'),
        ('on_duty', 'On Duty'),
    ]
    duty_event_status= models.CharField(choices=DUTY_EVENT_TYPE,max_length=50)
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time= models.DateTimeField(blank=True,null=True)
    truck_moved = models.BooleanField(default=True)
    location = models.CharField(max_length=255)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.duty_event_status} - {self.start_time}"









