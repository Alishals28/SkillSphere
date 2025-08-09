from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import ical_views

app_name = 'bookings'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'recurring-templates', views.RecurringBookingTemplateViewSet, basename='recurring-template')
router.register(r'group-bookings', views.GroupBookingViewSet, basename='group-booking')
router.register(r'packages', views.BookingPackageViewSet, basename='package')
router.register(r'package-purchases', views.BookingPackagePurchaseViewSet, basename='package-purchase')
router.register(r'templates', views.BookingTemplateViewSet, basename='template')

urlpatterns = [
    # Advanced booking ViewSets
    path('api/', include(router.urls)),
    
    # Booking CRUD
    path('', views.BookingListView.as_view(), name='booking-list'),
    path('create/', views.BookingCreateView.as_view(), name='booking-create'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='booking-detail'),
    
    # Booking actions
    path('<int:booking_id>/accept/', views.accept_booking, name='accept-booking'),
    path('<int:booking_id>/decline/', views.decline_booking, name='decline-booking'),
    path('<int:booking_id>/cancel/', views.cancel_booking, name='cancel-booking'),
    path('<int:booking_id>/complete/', views.complete_booking, name='complete-booking'),
    path('<int:booking_id>/feedback/', views.submit_feedback, name='submit-feedback'),
    
    # Advanced booking actions
    path('book-with-package/', views.book_with_package, name='book-with-package'),
    path('analytics/', views.advanced_booking_analytics, name='advanced-analytics'),
    
    # Calendar exports
    path('calendar.ics', ical_views.export_user_calendar, name='export-user-calendar'),
    path('<int:booking_id>/calendar.ics', ical_views.export_booking_ical, name='export-booking-ical'),
    
    # Dashboard and stats
    path('mentor-dashboard/', views.MentorDashboardView.as_view(), name='mentor-dashboard'),
    path('learner-dashboard/', views.LearnerDashboardView.as_view(), name='learner-dashboard'),
    path('stats/', views.booking_stats, name='booking-stats'),
]
