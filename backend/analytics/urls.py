from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import admin_views

app_name = 'analytics'

# URL patterns for analytics API
urlpatterns = [
    # Dashboard endpoints
    path('mentor/dashboard/', views.MentorDashboardView.as_view(), name='mentor-dashboard'),
    path('learner/dashboard/', views.LearnerDashboardView.as_view(), name='learner-dashboard'),
    path('platform/', views.platform_analytics, name='platform-analytics'),
    
    # Event tracking
    path('track/', views.track_event, name='track-event'),
    
    # Skill analytics
    path('skills/<int:skill_id>/', views.SkillAnalyticsView.as_view(), name='skill-analytics'),
    
    # Admin dashboard endpoints
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin-dashboard'),
    path('admin/api/', admin_views.admin_analytics_api, name='admin-analytics-api'),
    path('admin/users/', admin_views.admin_user_insights, name='admin-user-insights'),
    path('admin/financial/', admin_views.admin_financial_reports, name='admin-financial-reports'),
]
