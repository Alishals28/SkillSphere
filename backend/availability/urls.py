from django.urls import path
from . import views

app_name = 'availability'

urlpatterns = [
    # Weekly availability patterns
    path('weekly/', views.WeeklyAvailabilityListView.as_view(), name='weekly-availability-list'),
    path('weekly/<int:pk>/', views.WeeklyAvailabilityDetailView.as_view(), name='weekly-availability-detail'),
    
    # Availability slots
    path('slots/', views.AvailabilitySlotListView.as_view(), name='availability-slots-list'),
    path('slots/<int:pk>/', views.AvailabilitySlotDetailView.as_view(), name='availability-slot-detail'),
    path('slots/bulk/', views.bulk_create_slots, name='bulk-create-slots'),
    
    # Availability exceptions
    path('exceptions/', views.AvailabilityExceptionListView.as_view(), name='availability-exceptions-list'),
    path('exceptions/<int:pk>/', views.AvailabilityExceptionDetailView.as_view(), name='availability-exception-detail'),
    
    # Settings
    path('settings/', views.MentorAvailabilitySettingsView.as_view(), name='availability-settings'),
    
    # Utility endpoints
    path('block/', views.block_time_period, name='block-time-period'),
    path('generate-from-weekly/', views.generate_slots_from_weekly, name='generate-from-weekly'),
]

# Public endpoints for learners to view mentor availability
public_urlpatterns = [
    path('mentors/<int:mentor_id>/availability/', views.PublicMentorAvailabilityView.as_view(), name='public-mentor-availability'),
    path('mentors/<int:mentor_id>/availability/calendar/', views.mentor_availability_calendar, name='mentor-availability-calendar'),
]
