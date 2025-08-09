from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class Notification(models.Model):
    TYPE_CHOICES = (
        ('booking_request', 'Booking Request'),
        ('session_start', 'Session Start'),
        ('feedback_received', 'Feedback Received'),
        ('general', 'General'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    payload = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]
