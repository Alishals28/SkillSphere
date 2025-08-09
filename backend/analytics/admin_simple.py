from django.contrib import admin
from .models import (
    AnalyticsEvent, MentorAnalytics, LearnerAnalytics,
    PlatformAnalytics, SkillAnalytics, UserEngagementMetrics
)


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    """Admin interface for AnalyticsEvent model"""
    list_display = ['id', 'user', 'event_type', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['user__email', 'event_type']
    readonly_fields = ['created_at']


@admin.register(MentorAnalytics)
class MentorAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for MentorAnalytics model"""
    list_display = ['mentor', 'total_sessions', 'total_earnings', 'average_rating']
    search_fields = ['mentor__email', 'mentor__first_name', 'mentor__last_name']
    readonly_fields = ['last_updated']


@admin.register(LearnerAnalytics)
class LearnerAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for LearnerAnalytics model"""
    list_display = ['learner', 'total_sessions', 'total_spent', 'total_learning_hours']
    search_fields = ['learner__email', 'learner__first_name', 'learner__last_name']
    readonly_fields = ['last_updated']


@admin.register(PlatformAnalytics)
class PlatformAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for PlatformAnalytics model"""
    list_display = ['date', 'total_users', 'active_users', 'total_sessions']
    list_filter = ['date']
    date_hierarchy = 'date'


@admin.register(SkillAnalytics)
class SkillAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for SkillAnalytics model"""
    list_display = ['skill', 'total_sessions', 'unique_learners']
    search_fields = ['skill__name']
    readonly_fields = ['last_updated']


@admin.register(UserEngagementMetrics)
class UserEngagementMetricsAdmin(admin.ModelAdmin):
    """Admin interface for UserEngagementMetrics model"""
    list_display = ['user', 'date', 'pages_viewed', 'messages_sent']
    list_filter = ['date', 'user__role']
    search_fields = ['user__email']
    date_hierarchy = 'date'


# Admin site customization
admin.site.site_header = "SkillSphere Admin Panel"
admin.site.site_title = "SkillSphere Admin"
admin.site.index_title = "Welcome to SkillSphere Administration"
