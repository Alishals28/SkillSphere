from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.conf import settings

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending','Pending'),
        ('confirmed','Confirmed'),
        ('declined','Declined'),
        ('cancelled','Cancelled'),
        ('completed','Completed'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mentor = models.ForeignKey('mentors.MentorProfile', on_delete=models.CASCADE)
    learner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    requested_start_utc = models.DateTimeField()
    requested_end_utc = models.DateTimeField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending', db_index=True)
    price_cents = models.IntegerField(null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
