from django.db import models
from django.utils.text import slugify
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex


class SkillCategory(models.Model):
    """Categories for organizing skills"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Icon class name
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Skill Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Skill(models.Model):
    """Skills that mentors can teach"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    category = models.ForeignKey(
        SkillCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='skills'
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    popularity = models.PositiveIntegerField(default=0)  # Based on mentor count
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-popularity', 'name']
        indexes = [
            models.Index(fields=['is_active', 'popularity']),
            models.Index(fields=['category', 'popularity']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def update_popularity(self):
        """Update popularity based on number of mentors with this skill"""
        self.popularity = self.mentor_skills.filter(mentor__user__is_mentor_approved=True).count()
        self.save(update_fields=['popularity'])


class MentorSkill(models.Model):
    """Junction table for mentor skills with proficiency levels"""
    PROFICIENCY_CHOICES = [
        (1, 'Beginner'),
        (2, 'Novice'),
        (3, 'Intermediate'),
        (4, 'Advanced'),
        (5, 'Expert'),
    ]

    mentor = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='mentor_skills',
        limit_choices_to={'role': 'mentor'}
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='mentor_skills')
    proficiency = models.PositiveSmallIntegerField(
        choices=PROFICIENCY_CHOICES, 
        default=3,
        help_text="1=Beginner, 5=Expert"
    )
    years_experience = models.PositiveSmallIntegerField(null=True, blank=True)
    is_primary = models.BooleanField(default=False)  # Primary skills for mentor
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('mentor', 'skill')
        ordering = ['-is_primary', '-proficiency', 'skill__name']
        indexes = [
            models.Index(fields=['mentor', 'is_primary']),
            models.Index(fields=['skill', 'proficiency']),
        ]

    def __str__(self):
        return f"{self.mentor.full_name} - {self.skill.name} ({self.get_proficiency_display()})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update skill popularity
        self.skill.update_popularity()


class MentorTag(models.Model):
    """Tags for mentors (more flexible than skills)"""
    mentor = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='mentor_tags',
        limit_choices_to={'role': 'mentor'}
    )
    tag = models.CharField(max_length=50, default='general')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('mentor', 'tag')
        ordering = ['tag']

    def __str__(self):
        return f"{self.mentor.full_name} - {self.tag}"
