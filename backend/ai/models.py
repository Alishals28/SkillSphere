from django.db import models
from django.conf import settings


class AIResponse(models.Model):
    """Store AI-generated responses for various use cases"""
    TYPE_CHOICES = (
        ('session_summary', 'Session Summary'),
        ('learning_recommendation', 'Learning Recommendation'),
        ('skill_assessment', 'Skill Assessment'),
        ('mentor_match', 'Mentor Matching'),
        ('learning_path', 'Learning Path'),
        ('session_analysis', 'Session Analysis'),
        ('feedback_analysis', 'Feedback Analysis'),
        ('qa_response', 'Q&A Response'),
        ('content_generation', 'Content Generation'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    # Core fields
    type = models.CharField(max_length=32, choices=TYPE_CHOICES, default='general')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # AI model info
    model_name = models.CharField(max_length=100, default='gpt-3.5-turbo')
    model_version = models.CharField(max_length=50, blank=True)
    
    # Request/Response
    prompt = models.TextField(blank=True, default='')
    response = models.TextField(blank=True)
    tokens_used = models.PositiveIntegerField(null=True, blank=True)
    processing_time_ms = models.PositiveIntegerField(null=True, blank=True)
    
    # Context and metadata
    context_data = models.JSONField(default=dict, blank=True, help_text="Input data for AI processing")
    meta = models.JSONField(default=dict, blank=True, help_text="Additional metadata and settings")
    error_message = models.TextField(blank=True)
    
    # Relations
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ai_responses'
    )
    session = models.ForeignKey(
        'mentoring_sessions.Session', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='ai_responses'
    )
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ai_responses'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['type', 'status']),
            models.Index(fields=['user', 'type']),
            models.Index(fields=['session']),
            models.Index(fields=['booking']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.type} - {self.status} ({self.created_at})"


class LearningPath(models.Model):
    """AI-generated personalized learning paths"""
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'learner'},
        related_name='learning_paths'
    )
    
    title = models.CharField(max_length=200, blank=True, default='')
    description = models.TextField(blank=True, default='')
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    estimated_duration_weeks = models.PositiveIntegerField(default=1)
    
    # AI generation info
    ai_response = models.ForeignKey(
        AIResponse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_learning_paths'
    )
    
    # Skills covered
    target_skills = models.ManyToManyField('skills.Skill', related_name='learning_paths')
    
    # Progress tracking
    is_active = models.BooleanField(default=True)
    progress_percentage = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.learner.full_name}"


class LearningPathStep(models.Model):
    """Individual steps in a learning path"""
    learning_path = models.ForeignKey(
        LearningPath,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    
    title = models.CharField(max_length=200, blank=True, default='')
    description = models.TextField(blank=True, default='')
    order = models.PositiveIntegerField(default=1)
    
    # Step type
    step_type = models.CharField(
        max_length=30,
        choices=[
            ('mentor_session', 'Mentor Session'),
            ('self_study', 'Self Study'),
            ('practice_project', 'Practice Project'),
            ('assessment', 'Assessment'),
            ('resource_review', 'Resource Review'),
        ],
        default='self_study'
    )
    
    # Content and resources
    resources = models.JSONField(default=list, blank=True)
    estimated_duration_hours = models.PositiveIntegerField(default=1)
    
    # Progress
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Related booking if it's a mentor session
    related_booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='learning_path_steps'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['learning_path', 'order']
        unique_together = ['learning_path', 'order']

    def __str__(self):
        return f"{self.learning_path.title} - Step {self.order}: {self.title}"


class SkillAssessment(models.Model):
    """AI-driven skill assessments"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='skill_assessments'
    )
    
    skill = models.ForeignKey(
        'skills.Skill',
        on_delete=models.CASCADE,
        related_name='assessments'
    )
    
    assessment_type = models.CharField(
        max_length=20,
        choices=[
            ('initial', 'Initial Assessment'),
            ('progress', 'Progress Check'),
            ('final', 'Final Assessment'),
        ]
    )
    
    # AI assessment results
    ai_response = models.ForeignKey(
        AIResponse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='skill_assessments'
    )
    
    # Assessment data
    questions_data = models.JSONField(default=dict)
    answers_data = models.JSONField(default=dict)
    
    # Results
    proficiency_level = models.CharField(
        max_length=20,
        choices=[
            ('novice', 'Novice'),
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert'),
        ],
        null=True,
        blank=True
    )
    score_percentage = models.PositiveIntegerField(null=True, blank=True)
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    recommendations = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'skill']),
            models.Index(fields=['assessment_type']),
        ]

    def __str__(self):
        return f"{self.user.full_name} - {self.skill.name} ({self.assessment_type})"


class MentorRecommendation(models.Model):
    """AI-generated mentor recommendations"""
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'learner'},
        related_name='mentor_recommendations'
    )
    
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'mentor'},
        related_name='recommendation_received'
    )
    
    # Recommendation data
    ai_response = models.ForeignKey(
        AIResponse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentor_recommendations'
    )
    
    match_score = models.FloatField(default=0.0, help_text="AI-calculated match score (0-1)")
    reasoning = models.TextField(blank=True, default='', help_text="AI explanation for the recommendation")
    
    # Skills that make this a good match
    matching_skills = models.ManyToManyField('skills.Skill', related_name='mentor_recommendations')
    
    # User interaction
    is_viewed = models.BooleanField(default=False)
    is_contacted = models.BooleanField(default=False)
    user_rating = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5 rating
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-match_score', '-created_at']
        unique_together = ['learner', 'mentor']

    def __str__(self):
        return f"{self.learner.full_name} -> {self.mentor.full_name} (Score: {self.match_score})"
