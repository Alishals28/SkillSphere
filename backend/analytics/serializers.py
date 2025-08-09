from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    AnalyticsEvent, MentorAnalytics, LearnerAnalytics,
    PlatformAnalytics, SkillAnalytics, UserEngagementMetrics
)
from skills.models import Skill

User = get_user_model()


class AnalyticsEventSerializer(serializers.ModelSerializer):
    """Serializer for analytics events"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = AnalyticsEvent
        fields = [
            'id', 'user', 'user_name', 'event_type', 'event_data',
            'session_id', 'ip_address', 'user_agent', 'referrer',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'user_name']


class MentorAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for mentor analytics"""
    mentor_name = serializers.CharField(source='mentor.full_name', read_only=True)
    mentor_email = serializers.EmailField(source='mentor.email', read_only=True)
    
    class Meta:
        model = MentorAnalytics
        fields = [
            'id', 'mentor', 'mentor_name', 'mentor_email',
            'total_sessions', 'completed_sessions', 'cancelled_sessions',
            'total_earnings', 'average_session_rating', 'average_rating',
            'response_time_hours', 'completion_rate', 'cancellation_rate',
            'repeat_learner_rate', 'profile_views', 'booking_requests',
            'last_updated'
        ]
        read_only_fields = ['id', 'mentor_name', 'mentor_email', 'last_updated']


class LearnerAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for learner analytics"""
    learner_name = serializers.CharField(source='learner.full_name', read_only=True)
    learner_email = serializers.EmailField(source='learner.email', read_only=True)
    
    class Meta:
        model = LearnerAnalytics
        fields = [
            'id', 'learner', 'learner_name', 'learner_email',
            'total_sessions', 'completed_sessions', 'cancelled_sessions',
            'total_spent', 'average_session_cost', 'total_learning_hours',
            'skills_learned', 'favorite_mentors', 'completion_rate',
            'average_rating_given', 'learning_streak_days',
            'last_updated'
        ]
        read_only_fields = ['id', 'learner_name', 'learner_email', 'last_updated']


class PlatformAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for platform analytics"""
    
    class Meta:
        model = PlatformAnalytics
        fields = [
            'id', 'date', 'total_users', 'active_users', 'new_registrations',
            'total_mentors', 'active_mentors', 'new_mentors',
            'total_learners', 'active_learners', 'new_learners',
            'total_sessions', 'completed_sessions', 'cancelled_sessions',
            'total_revenue', 'platform_commission', 'average_session_rating',
            'total_skills', 'active_skills', 'most_popular_skill',
            'user_retention_rate', 'mentor_utilization_rate'
        ]
        read_only_fields = ['id']


class SkillAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for skill analytics"""
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    skill_category = serializers.CharField(source='skill.category.name', read_only=True)
    
    class Meta:
        model = SkillAnalytics
        fields = [
            'id', 'skill', 'skill_name', 'skill_category',
            'total_sessions', 'unique_learners', 'unique_mentors',
            'total_revenue', 'average_session_rating', 'demand_score',
            'average_mentor_rate', 'price_trend', 'growth_rate',
            'last_updated'
        ]
        read_only_fields = ['id', 'skill_name', 'skill_category', 'last_updated']


class UserEngagementMetricsSerializer(serializers.ModelSerializer):
    """Serializer for user engagement metrics"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    
    class Meta:
        model = UserEngagementMetrics
        fields = [
            'id', 'user', 'user_name', 'user_role', 'date',
            'login_count', 'session_duration_minutes', 'pages_viewed',
            'messages_sent', 'bookings_made', 'profile_updates',
            'last_activity_time'
        ]
        read_only_fields = ['id', 'user_name', 'user_role']


class DashboardSummarySerializer(serializers.Serializer):
    """Serializer for dashboard summary data"""
    total_sessions = serializers.IntegerField()
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_rating = serializers.FloatField()
    completion_rate = serializers.FloatField()
    period = serializers.CharField()


class SessionTimelineSerializer(serializers.Serializer):
    """Serializer for session timeline data"""
    date = serializers.DateField()
    sessions = serializers.IntegerField()
    earnings = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    completed = serializers.IntegerField(required=False)
    cancelled = serializers.IntegerField(required=False)


class SkillDemandSerializer(serializers.Serializer):
    """Serializer for skill demand data"""
    skill_name = serializers.CharField()
    sessions = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    unique_learners = serializers.IntegerField()
    average_rating = serializers.FloatField()


class MentorPerformanceSerializer(serializers.Serializer):
    """Serializer for mentor performance data"""
    mentor_id = serializers.IntegerField()
    mentor_name = serializers.CharField()
    total_sessions = serializers.IntegerField()
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_rating = serializers.FloatField()
    completion_rate = serializers.FloatField()
    response_time_hours = serializers.FloatField()


class LearnerProgressSerializer(serializers.Serializer):
    """Serializer for learner progress data"""
    learner_id = serializers.IntegerField()
    learner_name = serializers.CharField()
    total_sessions = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2)
    learning_hours = serializers.FloatField()
    skills_count = serializers.IntegerField()
    completion_rate = serializers.FloatField()


class PlatformStatsSerializer(serializers.Serializer):
    """Serializer for platform statistics"""
    total_users = serializers.IntegerField()
    total_mentors = serializers.IntegerField()
    total_learners = serializers.IntegerField()
    active_users = serializers.IntegerField()
    new_users = serializers.IntegerField()
    total_sessions = serializers.IntegerField()
    completed_sessions = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_rating = serializers.FloatField()


class AnalyticsFilterSerializer(serializers.Serializer):
    """Serializer for analytics filters"""
    period = serializers.ChoiceField(
        choices=[
            ('7', '7 days'),
            ('30', '30 days'),
            ('90', '90 days'),
            ('365', '1 year')
        ],
        default='30'
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    skill_id = serializers.IntegerField(required=False)
    mentor_id = serializers.IntegerField(required=False)
    learner_id = serializers.IntegerField(required=False)


class EventTrackingSerializer(serializers.Serializer):
    """Serializer for event tracking requests"""
    event_type = serializers.CharField(max_length=100)
    event_data = serializers.JSONField(default=dict)
    session_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    def validate_event_type(self, value):
        """Validate event type"""
        allowed_events = [
            'page_view', 'profile_view', 'search', 'booking_request',
            'booking_confirmed', 'session_completed', 'message_sent',
            'skill_added', 'mentor_followed', 'review_submitted',
            'payment_processed', 'login', 'logout', 'signup'
        ]
        
        if value not in allowed_events:
            raise serializers.ValidationError(f"Invalid event type. Must be one of: {', '.join(allowed_events)}")
        
        return value


class RevenueAnalyticsSerializer(serializers.Serializer):
    """Serializer for revenue analytics"""
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    platform_commission = serializers.DecimalField(max_digits=12, decimal_places=2)
    mentor_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_session_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    revenue_growth_rate = serializers.FloatField()
    top_earning_mentors = MentorPerformanceSerializer(many=True)
    revenue_by_skill = SkillDemandSerializer(many=True)


class UserGrowthSerializer(serializers.Serializer):
    """Serializer for user growth analytics"""
    date = serializers.DateField()
    new_users = serializers.IntegerField()
    new_mentors = serializers.IntegerField()
    new_learners = serializers.IntegerField()
    total_users = serializers.IntegerField()
    growth_rate = serializers.FloatField()


class EngagementMetricsSerializer(serializers.Serializer):
    """Serializer for engagement metrics"""
    daily_active_users = serializers.IntegerField()
    weekly_active_users = serializers.IntegerField()
    monthly_active_users = serializers.IntegerField()
    average_session_duration = serializers.FloatField()
    average_sessions_per_user = serializers.FloatField()
    user_retention_rate = serializers.FloatField()
    bounce_rate = serializers.FloatField()


class UpcomingSessionSerializer(serializers.Serializer):
    """Serializer for upcoming sessions in dashboard"""
    id = serializers.IntegerField()
    learner_name = serializers.CharField()
    mentor_name = serializers.CharField()
    subject = serializers.CharField()
    start_time = serializers.DateTimeField()
    duration = serializers.IntegerField()
    status = serializers.CharField()


class RecentActivitySerializer(serializers.Serializer):
    """Serializer for recent activity in dashboard"""
    type = serializers.CharField()
    description = serializers.CharField()
    status = serializers.CharField(required=False)
    timestamp = serializers.DateTimeField()


class AlertSerializer(serializers.Serializer):
    """Serializer for analytics alerts"""
    type = serializers.CharField()
    message = serializers.CharField()
    severity = serializers.ChoiceField(choices=['info', 'warning', 'error'])
    created_at = serializers.DateTimeField()
    is_read = serializers.BooleanField(default=False)
