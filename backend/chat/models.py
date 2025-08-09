from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class Message(models.Model):
    session = models.ForeignKey('sessions.Session', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['session', 'created_at']),
        ]
