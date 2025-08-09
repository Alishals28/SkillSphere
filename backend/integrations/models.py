from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
import json


class IntegrationProvider(models.Model):
    """Available integration providers"""
    PROVIDER_TYPES = [
        ('calendar', 'Calendar'),
        ('payment', 'Payment'),
        ('video', 'Video Conferencing'),
        ('storage', 'Cloud Storage'),
        ('email', 'Email Service'),
        ('analytics', 'Analytics'),
        ('social', 'Social Media'),
        ('communication', 'Communication'),
        ('crm', 'CRM'),
        ('lms', 'Learning Management System'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    provider_type = models.CharField(max_length=20, choices=PROVIDER_TYPES)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    logo_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    
    # API Configuration
    api_base_url = models.URLField()
    auth_type = models.CharField(max_length=20, choices=[
        ('oauth2', 'OAuth 2.0'),
        ('api_key', 'API Key'),
        ('basic', 'Basic Auth'),
        ('bearer', 'Bearer Token'),
    ])
    
    # OAuth Configuration
    client_id = models.CharField(max_length=255, blank=True)
    client_secret = models.CharField(max_length=255, blank=True)
    authorization_url = models.URLField(blank=True)
    token_url = models.URLField(blank=True)
    scope = models.CharField(max_length=500, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['provider_type', 'is_active']),
        ]
    
    def __str__(self):
        return self.display_name


class UserIntegration(models.Model):
    """User's connected integrations"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
        ('error', 'Error'),
        ('pending', 'Pending'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='integrations'
    )
    provider = models.ForeignKey(
        IntegrationProvider,
        on_delete=models.CASCADE,
        related_name='user_integrations'
    )
    
    # Authentication
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    api_key = models.CharField(max_length=500, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_enabled = models.BooleanField(default=True)
    
    # Configuration
    settings = models.JSONField(default=dict, blank=True)
    permissions = models.JSONField(default=list, blank=True)
    
    # Metadata
    external_user_id = models.CharField(max_length=255, blank=True)
    external_username = models.CharField(max_length=255, blank=True)
    external_email = models.EmailField(blank=True)
    
    # Timestamps
    connected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'provider']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['status', 'sync_enabled']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.provider.display_name}"
    
    def is_token_expired(self):
        """Check if access token is expired"""
        if not self.token_expires_at:
            return False
        return timezone.now() >= self.token_expires_at
    
    def needs_refresh(self):
        """Check if token needs refresh"""
        if not self.token_expires_at:
            return False
        # Refresh 5 minutes before expiry
        return timezone.now() >= (self.token_expires_at - timezone.timedelta(minutes=5))


class CalendarIntegration(models.Model):
    """Calendar-specific integration settings"""
    user_integration = models.OneToOneField(
        UserIntegration,
        on_delete=models.CASCADE,
        related_name='calendar_settings'
    )
    
    # Calendar Configuration
    default_calendar_id = models.CharField(max_length=255, blank=True)
    calendar_name = models.CharField(max_length=255, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    
    # Sync Settings
    sync_upcoming_sessions = models.BooleanField(default=True)
    sync_availability = models.BooleanField(default=True)
    create_booking_events = models.BooleanField(default=True)
    update_booking_events = models.BooleanField(default=True)
    delete_cancelled_events = models.BooleanField(default=True)
    
    # Event Configuration
    event_title_template = models.CharField(
        max_length=255,
        default="Mentoring Session with {participant}",
        help_text="Available variables: {participant}, {subject}, {duration}"
    )
    event_description_template = models.TextField(
        default="Subject: {subject}\nDuration: {duration} minutes\nPlatform: SkillSphere",
        help_text="Available variables: {subject}, {duration}, {mentor}, {learner}"
    )
    
    # Reminders
    add_reminders = models.BooleanField(default=True)
    reminder_minutes = models.JSONField(default=list, help_text="List of minutes before event to remind")
    
    # Metadata
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_errors = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return f"Calendar settings for {self.user_integration.user.email}"


class PaymentIntegration(models.Model):
    """Payment processor integration settings"""
    user_integration = models.OneToOneField(
        UserIntegration,
        on_delete=models.CASCADE,
        related_name='payment_settings'
    )
    
    # Account Information
    merchant_id = models.CharField(max_length=255, blank=True)
    account_id = models.CharField(max_length=255, blank=True)
    account_status = models.CharField(max_length=50, blank=True)
    
    # Payment Configuration
    default_currency = models.CharField(max_length=3, default='USD')
    supported_currencies = models.JSONField(default=list)
    
    # Fee Structure
    platform_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=2.5)
    transaction_fee_flat = models.DecimalField(max_digits=8, decimal_places=2, default=0.30)
    
    # Payout Settings
    auto_payout = models.BooleanField(default=True)
    payout_schedule = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], default='weekly')
    minimum_payout = models.DecimalField(max_digits=8, decimal_places=2, default=25.00)
    
    # Metadata
    last_payout = models.DateTimeField(null=True, blank=True)
    total_processed = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Payment settings for {self.user_integration.user.email}"


class VideoConferencingIntegration(models.Model):
    """Video conferencing integration settings"""
    user_integration = models.OneToOneField(
        UserIntegration,
        on_delete=models.CASCADE,
        related_name='video_settings'
    )
    
    # Account Information
    user_id = models.CharField(max_length=255, blank=True)
    display_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    
    # Meeting Configuration
    auto_create_meetings = models.BooleanField(default=True)
    default_meeting_type = models.CharField(max_length=20, choices=[
        ('instant', 'Instant Meeting'),
        ('scheduled', 'Scheduled Meeting'),
        ('recurring', 'Recurring Meeting'),
    ], default='scheduled')
    
    # Meeting Settings
    enable_waiting_room = models.BooleanField(default=True)
    enable_recording = models.BooleanField(default=False)
    auto_record = models.BooleanField(default=False)
    mute_participants_on_entry = models.BooleanField(default=True)
    
    # Security Settings
    require_password = models.BooleanField(default=True)
    allow_join_before_host = models.BooleanField(default=False)
    
    # Notifications
    send_meeting_invites = models.BooleanField(default=True)
    send_reminders = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Video settings for {self.user_integration.user.email}"


class IntegrationLog(models.Model):
    """Log of integration actions and events"""
    LOG_LEVELS = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    ACTION_TYPES = [
        ('auth', 'Authentication'),
        ('sync', 'Synchronization'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('webhook', 'Webhook'),
        ('api_call', 'API Call'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_integration = models.ForeignKey(
        UserIntegration,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    
    # Log Details
    level = models.CharField(max_length=10, choices=LOG_LEVELS)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    message = models.TextField()
    
    # Technical Details
    request_data = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)
    error_details = models.JSONField(null=True, blank=True)
    
    # Context
    booking_id = models.UUIDField(null=True, blank=True)
    external_id = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user_integration', 'created_at']),
            models.Index(fields=['level', 'created_at']),
            models.Index(fields=['action_type', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.level.upper()}: {self.action_type} - {self.message[:50]}"


class WebhookEndpoint(models.Model):
    """Webhook endpoints for receiving events from integrated services"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(
        IntegrationProvider,
        on_delete=models.CASCADE,
        related_name='webhook_endpoints'
    )
    
    # Endpoint Configuration
    url_path = models.CharField(max_length=255, unique=True)
    secret_key = models.CharField(max_length=255)
    
    # Event Configuration
    supported_events = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    
    # Security
    verify_signature = models.BooleanField(default=True)
    allowed_ips = models.JSONField(default=list, blank=True)
    
    # Statistics
    total_received = models.PositiveIntegerField(default=0)
    last_received = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.provider.display_name} webhook - {self.url_path}"


class WebhookEvent(models.Model):
    """Received webhook events"""
    EVENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
        ('ignored', 'Ignored'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    endpoint = models.ForeignKey(
        WebhookEndpoint,
        on_delete=models.CASCADE,
        related_name='events'
    )
    
    # Event Details
    event_type = models.CharField(max_length=100)
    event_id = models.CharField(max_length=255, blank=True)
    payload = models.JSONField()
    headers = models.JSONField(default=dict)
    
    # Processing
    status = models.CharField(max_length=20, choices=EVENT_STATUS, default='pending')
    processed_at = models.DateTimeField(null=True, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    # Metadata
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    signature_valid = models.BooleanField(null=True, blank=True)
    
    # Timestamps
    received_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['endpoint', 'received_at']),
            models.Index(fields=['status', 'received_at']),
            models.Index(fields=['event_type', 'received_at']),
        ]
        ordering = ['-received_at']
    
    def __str__(self):
        return f"{self.event_type} - {self.status} ({self.received_at})"
