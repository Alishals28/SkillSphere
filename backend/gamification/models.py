"""
Simple Badge System

A simple badge system that awards badges for various accomplishments.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Badge(models.Model):
    """
    Simple badge that users can earn
    """
    CATEGORY_CHOICES = [
        ('learning', 'Learning'),
        ('teaching', 'Teaching'),
        ('milestones', 'Milestones'),
        ('quality', 'Quality'),
        ('special', 'Special'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    icon = models.CharField(max_length=50, default='🏆', help_text="Emoji or icon identifier")
    
    # Simple criteria
    requirement_type = models.CharField(max_length=50, help_text="What needs to be accomplished")
    requirement_count = models.IntegerField(default=1, help_text="How many times")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class UserBadge(models.Model):
    """
    Badge earned by a user
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'badge']
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} earned {self.badge.name}"
