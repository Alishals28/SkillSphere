from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Count
from bookings.models import Booking
from skills.models import Skill

User = get_user_model()


class Review(models.Model):
    """
    Main review model for mentoring sessions
    """
    REVIEW_TYPES = [
        ('mentor_review', 'Mentor Review'),
        ('learner_review', 'Learner Review'),
        ('platform_review', 'Platform Review'),
    ]
    
    # Core fields
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='reviews')
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPES)
    
    # Rating fields
    overall_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Overall rating from 1 to 5 stars"
    )
    communication_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="Communication quality rating"
    )
    knowledge_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="Knowledge/expertise rating"
    )
    punctuality_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="Punctuality rating"
    )
    professionalism_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="Professionalism rating"
    )
    
    # Content fields
    review_text = models.TextField(help_text="Detailed review text")
    pros = models.TextField(blank=True, help_text="What went well")
    cons = models.TextField(blank=True, help_text="Areas for improvement")
    
    # Recommendation
    would_recommend = models.BooleanField(
        null=True, blank=True,
        help_text="Would you recommend this mentor/learner?"
    )
    
    # Additional fields
    tags = models.ManyToManyField('ReviewTag', blank=True)
    is_verified = models.BooleanField(default=True, help_text="Review is from verified session")
    is_anonymous = models.BooleanField(default=False, help_text="Review is anonymous")
    is_featured = models.BooleanField(default=False, help_text="Featured review")
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    moderation_notes = models.TextField(blank=True)
    flagged_count = models.IntegerField(default=0)
    
    # Metadata
    helpful_count = models.IntegerField(default=0)
    reported_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['reviewer', 'reviewee', 'booking', 'review_type']
        indexes = [
            models.Index(fields=['reviewee', '-created_at']),
            models.Index(fields=['reviewer', '-created_at']),
            models.Index(fields=['overall_rating']),
            models.Index(fields=['is_approved', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.reviewer.full_name} → {self.reviewee.full_name} ({self.overall_rating}★)"
    
    @property
    def average_detailed_rating(self):
        """Calculate average of detailed ratings"""
        ratings = [
            self.communication_rating,
            self.knowledge_rating,
            self.punctuality_rating,
            self.professionalism_rating
        ]
        valid_ratings = [r for r in ratings if r is not None]
        return sum(valid_ratings) / len(valid_ratings) if valid_ratings else None


class ReviewTag(models.Model):
    """
    Predefined tags for categorizing reviews
    """
    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=30, choices=[
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ])
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name


class ReviewHelpful(models.Model):
    """
    Track users who found a review helpful
    """
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['review', 'user']
    
    def __str__(self):
        return f"{self.user.full_name} found review helpful"


class ReviewReport(models.Model):
    """
    Reports for inappropriate reviews
    """
    REPORT_REASONS = [
        ('inappropriate', 'Inappropriate Content'),
        ('spam', 'Spam'),
        ('fake', 'Fake Review'),
        ('offensive', 'Offensive Language'),
        ('irrelevant', 'Irrelevant Content'),
        ('personal_attack', 'Personal Attack'),
        ('other', 'Other'),
    ]
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='resolved_reports'
    )
    
    class Meta:
        unique_together = ['review', 'reporter']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Report for review {self.review.id} by {self.reporter.full_name}"


class ReviewResponse(models.Model):
    """
    Responses to reviews (e.g., mentor responding to learner review)
    """
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='response')
    responder = models.ForeignKey(User, on_delete=models.CASCADE)
    response_text = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Response to review {self.review.id}"


class MentorRating(models.Model):
    """
    Aggregated rating data for mentors
    """
    mentor = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='rating_profile',
        limit_choices_to={'role': 'mentor'}
    )
    
    # Overall ratings
    overall_rating = models.FloatField(default=0.0)
    total_reviews = models.IntegerField(default=0)
    
    # Detailed ratings
    communication_rating = models.FloatField(default=0.0)
    knowledge_rating = models.FloatField(default=0.0)
    punctuality_rating = models.FloatField(default=0.0)
    professionalism_rating = models.FloatField(default=0.0)
    
    # Rating distribution
    five_star_count = models.IntegerField(default=0)
    four_star_count = models.IntegerField(default=0)
    three_star_count = models.IntegerField(default=0)
    two_star_count = models.IntegerField(default=0)
    one_star_count = models.IntegerField(default=0)
    
    # Recommendation metrics
    recommendation_count = models.IntegerField(default=0)
    recommendation_percentage = models.FloatField(default=0.0)
    
    # Metadata
    last_review_date = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-overall_rating']
    
    def __str__(self):
        return f"{self.mentor.full_name} - {self.overall_rating}★ ({self.total_reviews} reviews)"
    
    def update_ratings(self):
        """Update aggregated ratings from reviews"""
        reviews = Review.objects.filter(
            reviewee=self.mentor,
            review_type='mentor_review',
            is_approved=True
        )
        
        if reviews.exists():
            # Calculate averages
            aggregates = reviews.aggregate(
                avg_overall=Avg('overall_rating'),
                avg_communication=Avg('communication_rating'),
                avg_knowledge=Avg('knowledge_rating'),
                avg_punctuality=Avg('punctuality_rating'),
                avg_professionalism=Avg('professionalism_rating'),
                total_count=Count('id'),
                five_stars=Count('id', filter=models.Q(overall_rating=5)),
                four_stars=Count('id', filter=models.Q(overall_rating=4)),
                three_stars=Count('id', filter=models.Q(overall_rating=3)),
                two_stars=Count('id', filter=models.Q(overall_rating=2)),
                one_star=Count('id', filter=models.Q(overall_rating=1)),
                recommendations=Count('id', filter=models.Q(would_recommend=True))
            )
            
            # Update fields
            self.overall_rating = aggregates['avg_overall'] or 0.0
            self.communication_rating = aggregates['avg_communication'] or 0.0
            self.knowledge_rating = aggregates['avg_knowledge'] or 0.0
            self.punctuality_rating = aggregates['avg_punctuality'] or 0.0
            self.professionalism_rating = aggregates['avg_professionalism'] or 0.0
            
            self.total_reviews = aggregates['total_count']
            self.five_star_count = aggregates['five_stars']
            self.four_star_count = aggregates['four_stars']
            self.three_star_count = aggregates['three_stars']
            self.two_star_count = aggregates['two_stars']
            self.one_star_count = aggregates['one_star']
            
            self.recommendation_count = aggregates['recommendations']
            self.recommendation_percentage = (
                (aggregates['recommendations'] / aggregates['total_count']) * 100
                if aggregates['total_count'] > 0 else 0.0
            )
            
            # Get last review date
            latest_review = reviews.order_by('-created_at').first()
            if latest_review:
                self.last_review_date = latest_review.created_at
            
            self.save()


class SkillRating(models.Model):
    """
    Ratings for specific skills
    """
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='skill_ratings')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'mentor'})
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    
    # Skill-specific ratings
    expertise_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    teaching_ability_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    practical_knowledge_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['skill', 'mentor', 'review']
    
    def __str__(self):
        return f"{self.mentor.full_name} - {self.skill.name} ({self.expertise_rating}★)"


class ReviewTemplate(models.Model):
    """
    Templates for common review types
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    review_type = models.CharField(max_length=20, choices=Review.REVIEW_TYPES)
    template_text = models.TextField()
    suggested_tags = models.ManyToManyField(ReviewTag, blank=True)
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
