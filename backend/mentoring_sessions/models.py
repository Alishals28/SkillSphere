from django.db import models

# Create your models here.
from django.db import models

class Session(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('finished', 'Finished'),
    )
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE)
    meeting_link = models.URLField(max_length=500, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='scheduled')
    recording_url = models.URLField(max_length=500, blank=True, null=True)
    ai_summary = models.OneToOneField('ai.AIResponse', on_delete=models.SET_NULL, null=True, blank=True, related_name='session_summary')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['started_at']),
        ]
