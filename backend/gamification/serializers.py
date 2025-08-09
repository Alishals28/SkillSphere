"""
Simple Badge Serializers

Serializers for the simple badge system.
"""

from rest_framework import serializers
from .models import Badge, UserBadge


class BadgeSerializer(serializers.ModelSerializer):
    """Serializer for Badge model"""
    
    class Meta:
        model = Badge
        fields = [
            'id', 'name', 'description', 'category', 'icon',
            'requirement_type', 'requirement_count', 'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']


class UserBadgeSerializer(serializers.ModelSerializer):
    """Serializer for UserBadge model"""
    badge = BadgeSerializer(read_only=True)
    
    class Meta:
        model = UserBadge
        fields = ['id', 'badge', 'earned_at']
        read_only_fields = ['earned_at']
