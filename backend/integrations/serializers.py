from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    IntegrationProvider, UserIntegration, CalendarIntegration,
    PaymentIntegration, VideoConferencingIntegration, IntegrationLog,
    WebhookEndpoint, WebhookEvent
)

User = get_user_model()


class IntegrationProviderSerializer(serializers.ModelSerializer):
    """Serializer for IntegrationProvider model"""
    
    class Meta:
        model = IntegrationProvider
        fields = [
            'id', 'name', 'provider_type', 'display_name', 'description',
            'logo_url', 'website_url', 'auth_type', 'scope', 'is_active',
            'requires_approval'
        ]
        read_only_fields = ['id']


class UserIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for UserIntegration model"""
    provider_name = serializers.CharField(source='provider.display_name', read_only=True)
    provider_type = serializers.CharField(source='provider.provider_type', read_only=True)
    provider_logo = serializers.URLField(source='provider.logo_url', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = UserIntegration
        fields = [
            'id', 'provider', 'provider_name', 'provider_type', 'provider_logo',
            'user', 'user_name', 'status', 'last_sync', 'sync_enabled',
            'settings', 'permissions', 'external_user_id', 'external_username',
            'external_email', 'connected_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'provider_name', 'provider_type', 'provider_logo', 'user',
            'user_name', 'external_user_id', 'external_username', 'external_email',
            'connected_at', 'updated_at'
        ]
        extra_kwargs = {
            'access_token': {'write_only': True},
            'refresh_token': {'write_only': True},
            'api_key': {'write_only': True},
        }


class CalendarIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for CalendarIntegration model"""
    user_email = serializers.EmailField(source='user_integration.user.email', read_only=True)
    provider_name = serializers.CharField(source='user_integration.provider.display_name', read_only=True)
    
    class Meta:
        model = CalendarIntegration
        fields = [
            'id', 'user_integration', 'user_email', 'provider_name',
            'default_calendar_id', 'calendar_name', 'timezone',
            'sync_upcoming_sessions', 'sync_availability', 'create_booking_events',
            'update_booking_events', 'delete_cancelled_events',
            'event_title_template', 'event_description_template',
            'add_reminders', 'reminder_minutes', 'last_sync', 'sync_errors'
        ]
        read_only_fields = ['id', 'user_email', 'provider_name', 'last_sync', 'sync_errors']


class PaymentIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for PaymentIntegration model"""
    user_email = serializers.EmailField(source='user_integration.user.email', read_only=True)
    provider_name = serializers.CharField(source='user_integration.provider.display_name', read_only=True)
    
    class Meta:
        model = PaymentIntegration
        fields = [
            'id', 'user_integration', 'user_email', 'provider_name',
            'merchant_id', 'account_id', 'account_status',
            'default_currency', 'supported_currencies',
            'platform_fee_percentage', 'transaction_fee_flat',
            'auto_payout', 'payout_schedule', 'minimum_payout',
            'last_payout', 'total_processed'
        ]
        read_only_fields = [
            'id', 'user_email', 'provider_name', 'merchant_id', 'account_id',
            'account_status', 'supported_currencies', 'last_payout', 'total_processed'
        ]


class VideoConferencingIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for VideoConferencingIntegration model"""
    user_email = serializers.EmailField(source='user_integration.user.email', read_only=True)
    provider_name = serializers.CharField(source='user_integration.provider.display_name', read_only=True)
    
    class Meta:
        model = VideoConferencingIntegration
        fields = [
            'id', 'user_integration', 'user_email', 'provider_name',
            'user_id', 'display_name', 'email',
            'auto_create_meetings', 'default_meeting_type',
            'enable_waiting_room', 'enable_recording', 'auto_record',
            'mute_participants_on_entry', 'require_password',
            'allow_join_before_host', 'send_meeting_invites', 'send_reminders'
        ]
        read_only_fields = [
            'id', 'user_email', 'provider_name', 'user_id', 'display_name', 'email'
        ]


class IntegrationLogSerializer(serializers.ModelSerializer):
    """Serializer for IntegrationLog model"""
    user_email = serializers.EmailField(source='user_integration.user.email', read_only=True)
    provider_name = serializers.CharField(source='user_integration.provider.display_name', read_only=True)
    
    class Meta:
        model = IntegrationLog
        fields = [
            'id', 'user_integration', 'user_email', 'provider_name',
            'level', 'action_type', 'message', 'booking_id', 'external_id',
            'created_at'
        ]
        read_only_fields = ['id', 'user_email', 'provider_name', 'created_at']


class WebhookEndpointSerializer(serializers.ModelSerializer):
    """Serializer for WebhookEndpoint model"""
    provider_name = serializers.CharField(source='provider.display_name', read_only=True)
    
    class Meta:
        model = WebhookEndpoint
        fields = [
            'id', 'provider', 'provider_name', 'url_path', 'supported_events',
            'is_active', 'verify_signature', 'allowed_ips', 'total_received',
            'last_received', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'provider_name', 'total_received', 'last_received',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'secret_key': {'write_only': True}
        }


class WebhookEventSerializer(serializers.ModelSerializer):
    """Serializer for WebhookEvent model"""
    endpoint_path = serializers.CharField(source='endpoint.url_path', read_only=True)
    provider_name = serializers.CharField(source='endpoint.provider.display_name', read_only=True)
    
    class Meta:
        model = WebhookEvent
        fields = [
            'id', 'endpoint', 'endpoint_path', 'provider_name',
            'event_type', 'event_id', 'status', 'processed_at',
            'retry_count', 'error_message', 'signature_valid',
            'received_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'endpoint_path', 'provider_name', 'received_at', 'updated_at'
        ]


class IntegrationStatsSerializer(serializers.Serializer):
    """Serializer for integration statistics"""
    total_integrations = serializers.IntegerField()
    active_integrations = serializers.IntegerField()
    integrations_by_type = serializers.DictField()
    recent_activity = serializers.ListField()
    sync_status = serializers.DictField()


class OAuthInitiationSerializer(serializers.Serializer):
    """Serializer for OAuth initiation request"""
    provider_id = serializers.IntegerField()
    redirect_uri = serializers.URLField(required=False)
    
    def validate_provider_id(self, value):
        """Validate provider exists and supports OAuth"""
        try:
            provider = IntegrationProvider.objects.get(id=value, is_active=True)
            if provider.auth_type != 'oauth2':
                raise serializers.ValidationError('Provider does not support OAuth 2.0')
            return value
        except IntegrationProvider.DoesNotExist:
            raise serializers.ValidationError('Provider not found')


class IntegrationTestSerializer(serializers.Serializer):
    """Serializer for integration test results"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    details = serializers.DictField(required=False)
    timestamp = serializers.DateTimeField()


class IntegrationSyncSerializer(serializers.Serializer):
    """Serializer for integration sync results"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    items_synced = serializers.IntegerField(required=False)
    errors = serializers.ListField(required=False)
    timestamp = serializers.DateTimeField()


class AvailableIntegrationsSerializer(serializers.Serializer):
    """Serializer for available integrations summary"""
    calendar_providers = IntegrationProviderSerializer(many=True)
    payment_providers = IntegrationProviderSerializer(many=True)
    video_providers = IntegrationProviderSerializer(many=True)
    other_providers = IntegrationProviderSerializer(many=True)


class IntegrationSetupSerializer(serializers.Serializer):
    """Serializer for integration setup instructions"""
    provider = IntegrationProviderSerializer()
    setup_steps = serializers.ListField()
    required_permissions = serializers.ListField()
    configuration_options = serializers.DictField()
    estimated_setup_time = serializers.CharField()


class CalendarEventSerializer(serializers.Serializer):
    """Serializer for calendar event data"""
    id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(required=False)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    attendees = serializers.ListField(required=False)
    location = serializers.CharField(required=False)
    meeting_url = serializers.URLField(required=False)


class VideoMeetingSerializer(serializers.Serializer):
    """Serializer for video meeting data"""
    id = serializers.CharField()
    topic = serializers.CharField()
    start_url = serializers.URLField()
    join_url = serializers.URLField()
    password = serializers.CharField(required=False)
    start_time = serializers.DateTimeField()
    duration = serializers.IntegerField()
    timezone = serializers.CharField()


class PaymentIntentSerializer(serializers.Serializer):
    """Serializer for payment intent data"""
    id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()
    status = serializers.CharField()
    client_secret = serializers.CharField()
    metadata = serializers.DictField()


class IntegrationHealthSerializer(serializers.Serializer):
    """Serializer for integration health status"""
    integration_id = serializers.UUIDField()
    provider_name = serializers.CharField()
    status = serializers.CharField()
    last_successful_sync = serializers.DateTimeField(required=False)
    error_count = serializers.IntegerField()
    health_score = serializers.FloatField()
    recommendations = serializers.ListField()


class BulkIntegrationActionSerializer(serializers.Serializer):
    """Serializer for bulk integration actions"""
    integration_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=50
    )
    action = serializers.ChoiceField(choices=[
        ('enable_sync', 'Enable Sync'),
        ('disable_sync', 'Disable Sync'),
        ('test_connection', 'Test Connection'),
        ('refresh_tokens', 'Refresh Tokens'),
        ('disconnect', 'Disconnect')
    ])
    
    def validate_integration_ids(self, value):
        """Validate integration IDs belong to requesting user"""
        request = self.context.get('request')
        if request:
            user_integrations = UserIntegration.objects.filter(
                user=request.user,
                id__in=value
            ).values_list('id', flat=True)
            
            if len(user_integrations) != len(value):
                raise serializers.ValidationError('Some integration IDs are invalid or not accessible')
        
        return value
