from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    time_ago = serializers.SerializerMethodField()
    is_expired = serializers.ReadOnlyField()
    is_urgent = serializers.ReadOnlyField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title', 'message', 'payload', 'priority',
            'is_read', 'is_archived', 'read_at', 'action_url', 'action_text',
            'created_at', 'expires_at', 'time_ago', 'is_expired', 'is_urgent',
            'related_booking', 'related_session'
        ]
        read_only_fields = ['created_at', 'read_at']
    
    def get_time_ago(self, obj):
        """Get human-readable time ago"""
        from django.utils.timesince import timesince
        return timesince(obj.created_at)


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications"""
    
    class Meta:
        model = Notification
        fields = [
            'type', 'title', 'message', 'payload', 'priority',
            'action_url', 'action_text', 'expires_at',
            'related_booking', 'related_session'
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences"""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'email_booking_requests', 'email_booking_confirmations',
            'email_session_reminders', 'email_feedback_received', 'email_general_updates',
            'push_booking_requests', 'push_booking_confirmations',
            'push_session_reminders', 'push_feedback_received', 'push_general_updates',
            'session_reminder_minutes'
        ]


class NotificationBulkActionSerializer(serializers.Serializer):
    """Serializer for bulk notification actions"""
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    action = serializers.ChoiceField(choices=['mark_read', 'mark_unread', 'archive', 'delete'])
    
    def validate_action(self, value):
        if value not in ['mark_read', 'mark_unread', 'archive', 'delete']:
            raise serializers.ValidationError("Invalid action")
        return value
