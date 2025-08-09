from django.db import models

# Create your models here.
from django.db import models

class AvailabilitySlot(models.Model):
    mentor = models.ForeignKey('mentors.MentorProfile', on_delete=models.CASCADE)
    start_utc = models.DateTimeField()
    end_utc = models.DateTimeField()
    is_booked = models.BooleanField(default=False)
    recurring_rule = models.TextField(blank=True, null=True)  # Optional RRULE format
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['mentor', 'start_utc']),
        ]

class AvailabilityException(models.Model):
    mentor = models.ForeignKey('mentors.MentorProfile', on_delete=models.CASCADE)
    start_utc = models.DateTimeField()
    end_utc = models.DateTimeField()
    reason = models.TextField(blank=True)
    is_full_day = models.BooleanField(default=False)
