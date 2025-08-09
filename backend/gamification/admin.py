"""
Simple Badge Admin

Admin interface for the simple badge system.
"""

from django.contrib import admin
from .models import Badge, UserBadge


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Admin interface for Badge model"""
    list_display = ['name', 'category', 'requirement_type', 'requirement_count', 'is_active']
    list_filter = ['category', 'requirement_type', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    """Admin interface for UserBadge model"""
    list_display = ['user', 'badge', 'earned_at']
    list_filter = ['badge__category', 'earned_at']
    search_fields = ['user__username', 'user__email', 'badge__name']
    ordering = ['-earned_at']
