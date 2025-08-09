from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'reviews'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    # ViewSet routes (includes /api/reviews/reviews/)
    path('', include(router.urls)),
    
    # Mentor-specific reviews
    path('mentor/<int:mentor_id>/', views.MentorReviewsView.as_view(), name='mentor-reviews'),
    path('mentor/<int:mentor_id>/rating/', views.MentorRatingView.as_view(), name='mentor-rating'),
    
    # User reviews
    path('my-reviews/', views.UserReviewsView.as_view(), name='user-reviews'),
    path('reviewable-bookings/', views.ReviewableBookingsView.as_view(), name='reviewable-bookings'),
    
    # Review utilities
    path('tags/', views.ReviewTagsView.as_view(), name='review-tags'),
    path('templates/', views.ReviewTemplatesView.as_view(), name='review-templates'),
    path('stats/', views.ReviewStatsView.as_view(), name='review-stats'),
    
    # Admin endpoints
    path('admin/reviews/', views.AdminReviewListView.as_view(), name='admin-reviews'),
    path('admin/bulk-action/', views.bulk_review_action, name='bulk-review-action'),
    path('admin/reports/', views.ReviewReportsView.as_view(), name='review-reports'),
    path('admin/reports/<int:report_id>/resolve/', views.resolve_review_report, name='resolve-report'),
]
