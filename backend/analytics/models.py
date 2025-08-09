from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class AnalyticsEvent(models.Model):
    """Track user events for analytics"""
    EVENT_TYPES = (
        ('page_view', 'Page View'),
        ('search', 'Search'),
        ('profile_view', 'Profile View'),
        ('booking_created', 'Booking Created'),
        ('booking_completed', 'Booking Completed'),
        ('message_sent', 'Message Sent'),
        ('rating_given', 'Rating Given'),
        ('skill_learned', 'Skill Learned'),
        ('goal_achieved', 'Goal Achieved'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics_events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    event_data = models.JSONField(default=dict, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'event_type']),
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.full_name} - {self.event_type} at {self.created_at}"


class MentorAnalytics(models.Model):
    """Aggregated analytics for mentors"""
    mentor = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='mentor_analytics',
        limit_choices_to={'role': 'mentor'}
    )
    
    # Session Statistics
    total_sessions = models.PositiveIntegerField(default=0)
    completed_sessions = models.PositiveIntegerField(default=0)
    cancelled_sessions = models.PositiveIntegerField(default=0)
    no_show_sessions = models.PositiveIntegerField(default=0)
    
    # Rating and Reviews
    average_rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    total_reviews = models.PositiveIntegerField(default=0)
    five_star_reviews = models.PositiveIntegerField(default=0)
    four_star_reviews = models.PositiveIntegerField(default=0)
    three_star_reviews = models.PositiveIntegerField(default=0)
    two_star_reviews = models.PositiveIntegerField(default=0)
    one_star_reviews = models.PositiveIntegerField(default=0)
    
    # Earnings
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    this_month_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_month_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Response Times
    avg_response_time_hours = models.FloatField(default=0.0)
    response_rate_percentage = models.FloatField(
        default=100.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    
    # Engagement
    profile_views_this_month = models.PositiveIntegerField(default=0)
    profile_views_total = models.PositiveIntegerField(default=0)
    repeat_learners = models.PositiveIntegerField(default=0)
    
    # Time tracking
    total_teaching_hours = models.FloatField(default=0.0)
    this_month_hours = models.FloatField(default=0.0)
    average_session_duration = models.FloatField(default=0.0)
    
    # Updated timestamps
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analytics for {self.mentor.full_name}"


class LearnerAnalytics(models.Model):
    """Aggregated analytics for learners"""
    learner = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='learner_analytics',
        limit_choices_to={'role': 'learner'}
    )
    
    # Session Statistics
    total_sessions = models.PositiveIntegerField(default=0)
    completed_sessions = models.PositiveIntegerField(default=0)
    cancelled_sessions = models.PositiveIntegerField(default=0)
    no_show_sessions = models.PositiveIntegerField(default=0)
    
    # Learning Progress
    skills_learned = models.PositiveIntegerField(default=0)
    goals_achieved = models.PositiveIntegerField(default=0)
    total_learning_hours = models.FloatField(default=0.0)
    this_month_hours = models.FloatField(default=0.0)
    
    # Spending
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    this_month_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    average_session_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Engagement
    mentors_worked_with = models.PositiveIntegerField(default=0)
    favorite_mentors = models.PositiveIntegerField(default=0)
    reviews_given = models.PositiveIntegerField(default=0)
    
    # Preferences
    preferred_session_duration = models.PositiveIntegerField(default=60)  # minutes
    most_booked_skill = models.ForeignKey(
        'skills.Skill', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Updated timestamps
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analytics for {self.learner.full_name}"


class PlatformAnalytics(models.Model):
    """Platform-wide analytics (admin only)"""
    date = models.DateField(unique=True)
    
    # User Statistics
    total_users = models.PositiveIntegerField(default=0)
    new_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    total_mentors = models.PositiveIntegerField(default=0)
    active_mentors = models.PositiveIntegerField(default=0)
    new_mentors = models.PositiveIntegerField(default=0)
    
    # Session Statistics
    total_sessions = models.PositiveIntegerField(default=0)
    completed_sessions = models.PositiveIntegerField(default=0)
    cancelled_sessions = models.PositiveIntegerField(default=0)
    
    # Revenue
    gross_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    mentor_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Engagement
    average_session_rating = models.FloatField(default=0.0)
    total_messages_sent = models.PositiveIntegerField(default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Updated timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Platform Analytics for {self.date}"


class SkillAnalytics(models.Model):
    """Analytics for individual skills"""
    skill = models.OneToOneField(
        'skills.Skill', 
        on_delete=models.CASCADE, 
        related_name='analytics'
    )
    
    # Demand Statistics
    total_sessions = models.PositiveIntegerField(default=0)
    unique_learners = models.PositiveIntegerField(default=0)
    total_mentors = models.PositiveIntegerField(default=0)
    active_mentors = models.PositiveIntegerField(default=0)
    
    # Pricing
    average_hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    min_hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    max_hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Quality
    average_rating = models.FloatField(default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Trends
    growth_rate = models.FloatField(default=0.0)  # Percentage growth in demand
    popularity_rank = models.PositiveIntegerField(default=0)
    
    # Updated timestamps
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['popularity_rank', '-total_sessions']

    def __str__(self):
        return f"Analytics for {self.skill.name}"


class UserEngagementMetrics(models.Model):
    """Daily engagement metrics per user"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='engagement_metrics')
    date = models.DateField()
    
    # Session activity
    time_spent_minutes = models.PositiveIntegerField(default=0)
    pages_viewed = models.PositiveIntegerField(default=0)
    searches_performed = models.PositiveIntegerField(default=0)
    profiles_viewed = models.PositiveIntegerField(default=0)
    
    # Interaction activity
    messages_sent = models.PositiveIntegerField(default=0)
    bookings_made = models.PositiveIntegerField(default=0)
    reviews_given = models.PositiveIntegerField(default=0)
    
    # Learning activity (for learners)
    sessions_attended = models.PositiveIntegerField(default=0)
    learning_hours = models.FloatField(default=0.0)
    
    # Teaching activity (for mentors)
    sessions_taught = models.PositiveIntegerField(default=0)
    teaching_hours = models.FloatField(default=0.0)
    
    # Device info
    device_type = models.CharField(max_length=20, blank=True)  # mobile, desktop, tablet
    browser = models.CharField(max_length=50, blank=True)
    
    class Meta:
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.user.full_name} engagement on {self.date}"
