from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    """Notification model for user alerts"""
    TYPE_CHOICES = (
        ('booking_request', 'Booking Request'),
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('booking_completed', 'Booking Completed'),
        ('session_starting', 'Session Starting Soon'),
        ('session_reminder', 'Session Reminder'),
        ('feedback_received', 'Feedback Received'),
        ('mentor_approved', 'Mentor Application Approved'),
        ('mentor_rejected', 'Mentor Application Rejected'),
        ('availability_conflict', 'Availability Conflict'),
        ('payment_received', 'Payment Received'),
        ('general', 'General'),
        ('system', 'System Notification'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='general')
    title = models.CharField(max_length=200, blank=True, default='Notification')
    message = models.TextField(blank=True, default='')
    payload = models.JSONField(default=dict, blank=True, help_text="Additional data related to notification")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Status fields
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Optional action button
    action_url = models.URLField(blank=True, help_text="URL for action button")
    action_text = models.CharField(max_length=50, blank=True, help_text="Text for action button")
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When notification expires")
    
    # Related objects (optional foreign keys)
    related_booking = models.ForeignKey(
        'bookings.Booking', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='notifications'
    )
    related_session = models.ForeignKey(
        'mentoring_sessions.Session', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='notifications'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['priority', 'is_read']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def is_urgent(self):
        """Check if notification is urgent"""
        return self.priority in ['high', 'urgent']


class NotificationPreference(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notification_preferences'
    )
    
    # Email preferences
    email_booking_requests = models.BooleanField(default=True)
    email_booking_confirmations = models.BooleanField(default=True)
    email_session_reminders = models.BooleanField(default=True)
    email_feedback_received = models.BooleanField(default=True)
    email_general_updates = models.BooleanField(default=True)
    
    # Push notification preferences (for future mobile app)
    push_booking_requests = models.BooleanField(default=True)
    push_booking_confirmations = models.BooleanField(default=True)
    push_session_reminders = models.BooleanField(default=True)
    push_feedback_received = models.BooleanField(default=False)
    push_general_updates = models.BooleanField(default=False)
    
    # Timing preferences
    session_reminder_minutes = models.PositiveIntegerField(
        default=30, 
        help_text="Minutes before session to send reminder"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification preferences for {self.user.email}"
