from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class Feedback(models.Model):
    session = models.ForeignKey('sessions.Session', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # 1-5
    comment = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    anonymized = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['session']),
            models.Index(fields=['created_by']),
        ]
