from django.urls import path
from . import views

app_name = 'trips'

urlpatterns = [
    # Trip management
    path('api/trips/', views.TripListCreateView.as_view(), name='trip-list-create'),
    path('api/trips/<uuid:pk>/', views.TripDetailView.as_view(), name='trip-detail'),
    
    # Daily logs
    path('api/trips/<uuid:trip_id>/logs/', views.DailyLogListView.as_view(), name='daily-logs'),
    
    # Duty events
    path('api/logs/<uuid:daily_log_id>/events/', views.DutyEventListView.as_view(), name='duty-events'),
    
    # Route and mapping
    path('api/trips/<uuid:trip_id>/route/', views.route_data_view, name='route-data'),
    
    # Driver statistics
    path('api/drivers/<int:driver_id>/stats/', views.driver_stats_view, name='driver-stats'),
]