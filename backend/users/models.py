from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone as django_timezone
from django_countries.fields import CountryField
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
import uuid


class User(AbstractUser):
    ROLE_CHOICES = (
        ('learner', 'Learner'),
        ('mentor', 'Mentor'),
        ('admin', 'Admin'),
    )
    
    # Core fields (keep default Django ID)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default='learner', db_index=True)
    
    # Profile fields
    bio = models.TextField(blank=True, max_length=1000)
    timezone = models.CharField(max_length=64, default='UTC')
    phone_number = models.CharField(
        max_length=17,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    country = CountryField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    
    # Status fields
    is_email_verified = models.BooleanField(default=False)
    is_mentor_approved = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    password_reset_token = models.UUIDField(null=True, blank=True)
    password_reset_expires = models.DateTimeField(null=True, blank=True)
    
    # Learner-specific fields
    learning_goals = models.TextField(blank=True, help_text="What do you want to achieve?")
    experience_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        blank=True
    )
    preferred_session_duration = models.IntegerField(
        default=60,
        help_text="Preferred session duration in minutes"
    )
    
    # Mentor-specific fields (will be null for non-mentors)
    mentor_bio = models.TextField(blank=True, max_length=2000, help_text="Detailed mentor biography")
    teaching_experience = models.TextField(blank=True, help_text="Teaching experience and background")
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    portfolio_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    is_available = models.BooleanField(default=True, help_text="Currently accepting new sessions")
    
    # Search functionality
    search_vector = SearchVectorField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(default=django_timezone.now)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['role', 'is_mentor_approved']),
            models.Index(fields=['email', 'is_email_verified']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_available', 'hourly_rate']),
            GinIndex(fields=['search_vector']),  # Full-text search index
        ]

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_mentor(self):
        return self.role == 'mentor'

    @property
    def is_learner(self):
        return self.role == 'learner'

    @property
    def is_admin_user(self):
        return self.role == 'admin'

    def can_mentor(self):
        """Check if user can act as a mentor"""
        return self.is_mentor and self.is_mentor_approved and self.is_email_verified

    def update_last_active(self):
        """Update last active timestamp"""
        self.last_active = django_timezone.now()
        self.save(update_fields=['last_active'])

    def update_search_vector(self):
        """Update search vector for full-text search"""
        from django.contrib.postgres.search import SearchVector
        
        # Build search vector from various fields
        search_fields = []
        
        # Basic info
        if self.first_name:
            search_fields.append(SearchVector('first_name', weight='A'))
        if self.last_name:
            search_fields.append(SearchVector('last_name', weight='A'))
        if self.mentor_bio:
            search_fields.append(SearchVector('mentor_bio', weight='B'))
        if self.bio:
            search_fields.append(SearchVector('bio', weight='C'))
        if self.teaching_experience:
            search_fields.append(SearchVector('teaching_experience', weight='C'))
        
        # Skills (we'll add this in the manager)
        if search_fields:
            User.objects.filter(pk=self.pk).update(
                search_vector=search_fields[0] if len(search_fields) == 1 
                else search_fields[0] + sum(search_fields[1:], SearchVector('id'))
            )


class UserInterest(models.Model):
    """Learner interests/topics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interests')
    interest = models.CharField(max_length=100, default='learning')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'interest')
        db_table = 'user_interests'

    def __str__(self):
        return f"{self.user.email} - {self.interest}"


class SocialProfile(models.Model):
    """Store social auth profile data"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='social_profile')
    provider = models.CharField(max_length=50, default='local')
    social_id = models.CharField(max_length=100, default='')
    avatar_url = models.URLField(blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('provider', 'social_id')
        db_table = 'social_profiles'

    def __str__(self):
        return f"{self.user.email} - {self.provider}"
