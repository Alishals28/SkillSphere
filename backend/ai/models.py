from django.db import models

# Create your models here.
from django.db import models

class AIResponse(models.Model):
    TYPE_CHOICES = (
        ('summary', 'Summary'),
        ('recommendation', 'Recommendation'),
    )
    session = models.ForeignKey('sessions.Session', on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    model_name = models.CharField(max_length=100)
    prompt = models.TextField()
    response = models.TextField()
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['type']),
        ]
