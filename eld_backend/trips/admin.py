from django.contrib import admin
from django.utils.html import format_html
from .models import Driver, Trip, DailyLog, DutyEvents, Stop

# admin.py

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['user', 'driver_number', 'initials', 'home_operation_center', 'created_at']
    list_filter = ['home_operation_center', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'driver_number']
    readonly_fields = ['created_at']

class DailyLogInline(admin.TabularInline):
    model = DailyLog
    extra = 0
    readonly_fields = ['id', 'date']

class StopInline(admin.TabularInline):
    model = Stop
    extra = 0
    readonly_fields = ['arrival_time', 'depature_time', 'duration']

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['id', 'driver', 'current_location', 'pickup_location', 'dropoff_location', 'current_cycle_used', 'created_at']
    list_filter = ['created_at', 'driver']
    search_fields = ['driver__user__username', 'pickup_location', 'dropoff_location']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [StopInline, DailyLogInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('driver__user')

class DutyEventsInline(admin.TabularInline):
    model = DutyEvents
    extra = 0
    readonly_fields = ['created_at']
    ordering = ['start_time']

@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'driver', 'date', 'total_driving_time', 'total_on_duty_time', 
        'total_driving_miles', 'compliance_status'
    ]
    list_filter = ['date', 'driver']
    search_fields = ['driver__user__username', 'driver__driver_number']
    readonly_fields = ['id', 'compliance_status_display']
    inlines = [DutyEventsInline]
    
    def compliance_status(self, obj):
        """Check if the daily log is compliant with HOS regulations"""
        if obj.total_driving_time > 11:
            return format_html('<span style="color: red;">⚠ Driving Violation</span>')
        elif (obj.total_driving_time + obj.total_on_duty_time) > 14:
            return format_html('<span style="color: red;">⚠ On-Duty Violation</span>')
        else:
            return format_html('<span style="color: green;">✓ Compliant</span>')
    
    compliance_status.short_description = 'Compliance Status'
    
    def compliance_status_display(self, obj):
        return self.compliance_status(obj)
    
    compliance_status_display.short_description = 'Compliance Status'

@admin.register(DutyEvents)
class DutyEventsAdmin(admin.ModelAdmin):
    list_display = ['duty_event_status', 'daily_log', 'start_time', 'end_time', 'location', 'truck_moved']
    list_filter = ['duty_event_status', 'truck_moved', 'start_time']
    search_fields = ['daily_log__driver__user__username', 'location', 'remarks']
    readonly_fields = ['created_at', 'duration']
    
    def duration(self, obj):
        """Calculate duration of the duty event"""
        if obj.start_time and obj.end_time:
            diff = obj.end_time - obj.start_time
            hours = diff.total_seconds() / 3600
            return f"{hours:.1f} hours"
        return "Ongoing"
    
    duration.short_description = 'Duration'

@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ['trip', 'location', 'stop_type', 'arrival_time', 'depature_time', 'duration']
    list_filter = ['stop_type', 'arrival_time']
    search_fields = ['trip__driver__user__username', 'location']

admin.site.site_header = 'ELD Tracker Administration'
admin.site.site_title = 'ELD Tracker'
admin.site.index_title = 'Electronic Logging Device Management'