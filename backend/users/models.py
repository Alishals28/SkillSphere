from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('learner', 'Learner'),
        ('mentor', 'Mentor'),
        ('admin', 'Admin'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, db_index=True)
    bio = models.TextField(blank=True)
    timezone = models.CharField(max_length=64, default='UTC')

    def __str__(self):
        return f"{self.username} ({self.role})"
