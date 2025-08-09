from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Avg
from .models import (
    Review, ReviewTag, ReviewHelpful, ReviewReport, 
    ReviewResponse, MentorRating, SkillRating, ReviewTemplate
)
from bookings.models import Booking
from skills.models import Skill

User = get_user_model()


class ReviewTagSerializer(serializers.ModelSerializer):
    """Serializer for review tags"""
    
    class Meta:
        model = ReviewTag
        fields = ['id', 'name', 'category', 'description']
        read_only_fields = ['usage_count']


class ReviewHelpfulSerializer(serializers.ModelSerializer):
    """Serializer for review helpful votes"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = ReviewHelpful
        fields = ['id', 'user', 'user_name', 'created_at']
        read_only_fields = ['created_at']


class ReviewResponseSerializer(serializers.ModelSerializer):
    """Serializer for review responses"""
    responder_name = serializers.CharField(source='responder.full_name', read_only=True)
    responder_role = serializers.CharField(source='responder.role', read_only=True)
    
    class Meta:
        model = ReviewResponse
        fields = [
            'id', 'responder', 'responder_name', 'responder_role',
            'response_text', 'is_approved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'responder_name', 'responder_role', 'created_at', 'updated_at']


class SkillRatingSerializer(serializers.ModelSerializer):
    """Serializer for skill-specific ratings"""
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    
    class Meta:
        model = SkillRating
        fields = [
            'id', 'skill', 'skill_name', 'expertise_rating',
            'teaching_ability_rating', 'practical_knowledge_rating', 'created_at'
        ]
        read_only_fields = ['id', 'skill_name', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    """Comprehensive review serializer"""
    reviewer_name = serializers.CharField(source='reviewer.full_name', read_only=True)
    reviewer_profile_picture = serializers.SerializerMethodField()
    reviewee_name = serializers.CharField(source='reviewee.full_name', read_only=True)
    
    tags = ReviewTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=ReviewTag.objects.all(), 
        write_only=True,
        required=False
    )
    
    response = ReviewResponseSerializer(read_only=True)
    helpful_votes = ReviewHelpfulSerializer(many=True, read_only=True)
    skill_ratings = SkillRatingSerializer(many=True, read_only=True)
    
    booking_subject = serializers.CharField(source='booking.subject', read_only=True)
    booking_date = serializers.DateTimeField(source='booking.confirmed_start_utc', read_only=True)
    
    average_detailed_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'reviewer', 'reviewer_name', 'reviewer_profile_picture',
            'reviewee', 'reviewee_name', 'booking', 'booking_subject', 'booking_date',
            'review_type', 'overall_rating', 'communication_rating',
            'knowledge_rating', 'punctuality_rating', 'professionalism_rating',
            'review_text', 'pros', 'cons', 'would_recommend',
            'tags', 'tag_ids', 'is_verified', 'is_anonymous', 'is_featured',
            'helpful_count', 'reported_count', 'response', 'helpful_votes',
            'skill_ratings', 'average_detailed_rating', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'reviewer_name', 'reviewer_profile_picture', 'reviewee_name',
            'booking_subject', 'booking_date', 'is_verified', 'helpful_count',
            'reported_count', 'response', 'helpful_votes', 'skill_ratings',
            'average_detailed_rating', 'created_at', 'updated_at'
        ]
    
    def get_reviewer_profile_picture(self, obj):
        """Get reviewer profile picture URL"""
        if obj.is_anonymous:
            return None
        if obj.reviewer.profile_picture:
            return obj.reviewer.profile_picture.url
        return None
    
    def create(self, validated_data):
        """Create review with tags"""
        tag_ids = validated_data.pop('tag_ids', [])
        review = Review.objects.create(**validated_data)
        
        if tag_ids:
            review.tags.set(tag_ids)
            # Update tag usage counts
            for tag in tag_ids:
                tag.usage_count += 1
                tag.save()
        
        return review
    
    def update(self, instance, validated_data):
        """Update review with tags"""
        tag_ids = validated_data.pop('tag_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        
        return instance
    
    def validate(self, data):
        """Validate review data"""
        # Check if user can review this booking
        booking = data.get('booking')
        reviewer = data.get('reviewer')
        reviewee = data.get('reviewee')
        review_type = data.get('review_type')
        
        if booking:
            # Validate review permissions
            if review_type == 'mentor_review':
                if reviewer != booking.learner or reviewee != booking.mentor:
                    raise serializers.ValidationError(
                        "Only the learner can review the mentor for this booking"
                    )
            elif review_type == 'learner_review':
                if reviewer != booking.mentor or reviewee != booking.learner:
                    raise serializers.ValidationError(
                        "Only the mentor can review the learner for this booking"
                    )
            
            # Check if booking is completed
            if booking.status != 'completed':
                raise serializers.ValidationError(
                    "Can only review completed sessions"
                )
            
            # Check for duplicate reviews
            if Review.objects.filter(
                reviewer=reviewer,
                reviewee=reviewee,
                booking=booking,
                review_type=review_type
            ).exists():
                raise serializers.ValidationError(
                    "You have already reviewed this session"
                )
        
        return data


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating reviews"""
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=ReviewTag.objects.all(), 
        required=False
    )
    
    skill_ratings = SkillRatingSerializer(many=True, required=False)
    
    class Meta:
        model = Review
        fields = [
            'booking', 'reviewee', 'review_type', 'overall_rating',
            'communication_rating', 'knowledge_rating', 'punctuality_rating',
            'professionalism_rating', 'review_text', 'pros', 'cons',
            'would_recommend', 'tag_ids', 'skill_ratings', 'is_anonymous'
        ]
    
    def create(self, validated_data):
        """Create review with skill ratings"""
        tag_ids = validated_data.pop('tag_ids', [])
        skill_ratings_data = validated_data.pop('skill_ratings', [])
        
        # Set reviewer from request user
        validated_data['reviewer'] = self.context['request'].user
        
        review = Review.objects.create(**validated_data)
        
        # Add tags
        if tag_ids:
            review.tags.set(tag_ids)
        
        # Create skill ratings
        for skill_rating_data in skill_ratings_data:
            SkillRating.objects.create(
                review=review,
                mentor=review.reviewee,
                **skill_rating_data
            )
        
        return review


class ReviewListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing reviews"""
    reviewer_name = serializers.SerializerMethodField()
    reviewer_profile_picture = serializers.SerializerMethodField()
    tags = ReviewTagSerializer(many=True, read_only=True)
    response = ReviewResponseSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'reviewer_name', 'reviewer_profile_picture',
            'overall_rating', 'review_text', 'pros', 'cons',
            'would_recommend', 'tags', 'helpful_count',
            'response', 'created_at'
        ]
    
    def get_reviewer_name(self, obj):
        """Get reviewer name (anonymous if needed)"""
        if obj.is_anonymous:
            return "Anonymous"
        return obj.reviewer.full_name
    
    def get_reviewer_profile_picture(self, obj):
        """Get reviewer profile picture (None if anonymous)"""
        if obj.is_anonymous:
            return None
        if obj.reviewer.profile_picture:
            return obj.reviewer.profile_picture.url
        return None


class MentorRatingSerializer(serializers.ModelSerializer):
    """Serializer for mentor rating aggregates"""
    mentor_name = serializers.CharField(source='mentor.full_name', read_only=True)
    recent_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = MentorRating
        fields = [
            'id', 'mentor', 'mentor_name', 'overall_rating', 'total_reviews',
            'communication_rating', 'knowledge_rating', 'punctuality_rating',
            'professionalism_rating', 'five_star_count', 'four_star_count',
            'three_star_count', 'two_star_count', 'one_star_count',
            'recommendation_count', 'recommendation_percentage',
            'last_review_date', 'recent_reviews'
        ]
        read_only_fields = ['recent_reviews']
    
    def get_recent_reviews(self, obj):
        """Get recent reviews for this mentor"""
        recent_reviews = Review.objects.filter(
            reviewee=obj.mentor,
            review_type='mentor_review',
            is_approved=True
        ).order_by('-created_at')[:3]
        
        return ReviewListSerializer(recent_reviews, many=True).data


class ReviewReportSerializer(serializers.ModelSerializer):
    """Serializer for review reports"""
    reporter_name = serializers.CharField(source='reporter.full_name', read_only=True)
    review_text = serializers.CharField(source='review.review_text', read_only=True)
    
    class Meta:
        model = ReviewReport
        fields = [
            'id', 'review', 'reporter', 'reporter_name', 'reason',
            'description', 'review_text', 'is_resolved', 'resolution_notes',
            'created_at', 'resolved_at', 'resolved_by'
        ]
        read_only_fields = [
            'id', 'reporter_name', 'review_text', 'created_at', 'resolved_at'
        ]


class ReviewTemplateSerializer(serializers.ModelSerializer):
    """Serializer for review templates"""
    suggested_tags = ReviewTagSerializer(many=True, read_only=True)
    
    class Meta:
        model = ReviewTemplate
        fields = [
            'id', 'name', 'description', 'review_type', 'template_text',
            'suggested_tags', 'usage_count'
        ]
        read_only_fields = ['usage_count']


class ReviewStatsSerializer(serializers.Serializer):
    """Serializer for review statistics"""
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()
    rating_distribution = serializers.DictField()
    recent_reviews_count = serializers.IntegerField()
    recommendation_rate = serializers.FloatField()


class BulkReviewActionSerializer(serializers.Serializer):
    """Serializer for bulk review actions"""
    review_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    action = serializers.ChoiceField(choices=[
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('feature', 'Feature'),
        ('unfeature', 'Unfeature'),
        ('delete', 'Delete')
    ])
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
