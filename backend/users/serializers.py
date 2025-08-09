from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User, UserInterest, SocialProfile, TwoFactorAuth


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for references in other models"""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'profile_picture', 'is_mentor_approved'
        )
        read_only_fields = fields


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    interests = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'password_confirm', 
            'first_name', 'last_name', 'role', 'bio', 'timezone',
            'phone_number', 'country', 'date_of_birth',
            'learning_goals', 'experience_level', 'preferred_session_duration',
            'interests'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Validate mentor-specific fields if role is mentor
        if attrs.get('role') == 'mentor':
            if not attrs.get('bio'):
                raise serializers.ValidationError({"bio": "Bio is required for mentors."})
        
        return attrs

    def create(self, validated_data):
        # Remove non-model fields
        password_confirm = validated_data.pop('password_confirm')
        interests_data = validated_data.pop('interests', [])
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        # Add interests
        for interest in interests_data:
            UserInterest.objects.create(user=user, interest=interest.strip())
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile (read/update)"""
    
    interests = serializers.SerializerMethodField()
    full_name = serializers.ReadOnlyField()
    social_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'bio', 'timezone', 'phone_number', 'country', 'date_of_birth',
            'profile_picture', 'is_email_verified', 'is_mentor_approved',
            'learning_goals', 'experience_level', 'preferred_session_duration',
            'mentor_bio', 'teaching_experience', 'hourly_rate', 'portfolio_url',
            'linkedin_url', 'github_url', 'is_available', 'interests',
            'social_profile', 'created_at', 'updated_at', 'last_active'
        )
        read_only_fields = (
            'id', 'username', 'email', 'is_email_verified', 'is_mentor_approved',
            'created_at', 'updated_at', 'last_active'
        )

    def get_interests(self, obj):
        return [interest.interest for interest in obj.interests.all()]

    def get_social_profile(self, obj):
        try:
            social = obj.social_profile
            return {
                'provider': social.provider,
                'avatar_url': social.avatar_url
            }
        except:
            return None

    def update(self, instance, validated_data):
        # Handle interests separately
        interests_data = self.initial_data.get('interests', [])
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # Update interests
        if interests_data is not None:
            instance.interests.all().delete()
            for interest in interests_data:
                UserInterest.objects.create(user=instance, interest=interest.strip())
        
        return instance


class PublicMentorProfileSerializer(serializers.ModelSerializer):
    """Public serializer for mentor profiles (for browsing)"""
    
    full_name = serializers.ReadOnlyField()
    skills = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    total_sessions = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    response_rate = serializers.SerializerMethodField()
    availability_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'full_name', 'bio', 'mentor_bio',
            'profile_picture', 'country', 'hourly_rate', 'portfolio_url',
            'linkedin_url', 'github_url', 'teaching_experience',
            'is_available', 'skills', 'tags', 'rating', 'total_sessions',
            'total_reviews', 'response_rate', 'availability_count',
            'timezone', 'created_at'
        )

    def get_skills(self, obj):
        from skills.serializers import MentorSkillSerializer
        return MentorSkillSerializer(
            obj.mentor_skills.select_related('skill', 'skill__category').order_by('-is_primary', '-proficiency'),
            many=True
        ).data

    def get_tags(self, obj):
        return [tag.tag for tag in obj.mentor_tags.all()]

    def get_rating(self, obj):
        from django.db.models import Avg
        avg_rating = obj.mentor_bookings.filter(
            status='completed',
            learner_rating__isnull=False
        ).aggregate(avg_rating=Avg('learner_rating'))['avg_rating']
        return round(avg_rating, 1) if avg_rating else 0.0

    def get_total_sessions(self, obj):
        return obj.mentor_bookings.filter(status='completed').count()

    def get_total_reviews(self, obj):
        return obj.mentor_bookings.filter(
            status='completed',
            learner_feedback__isnull=False
        ).exclude(learner_feedback='').count()

    def get_response_rate(self, obj):
        total_requests = obj.mentor_bookings.filter(status__in=['pending', 'confirmed', 'declined']).count()
        if total_requests == 0:
            return 100.0
        
        responded = obj.mentor_bookings.filter(status__in=['confirmed', 'declined']).count()
        return round((responded / total_requests) * 100, 1)

    def get_availability_count(self, obj):
        from availability.models import AvailabilitySlot
        from django.utils import timezone
        
        return AvailabilitySlot.objects.filter(
            mentor=obj,
            start_utc__gt=timezone.now(),
            is_booked=False,
            is_blocked=False
        ).count()


class DetailedMentorProfileSerializer(PublicMentorProfileSerializer):
    """Detailed mentor profile with availability and reviews"""
    
    recent_reviews = serializers.SerializerMethodField()
    next_available_slots = serializers.SerializerMethodField()
    specializations = serializers.SerializerMethodField()
    
    class Meta(PublicMentorProfileSerializer.Meta):
        fields = PublicMentorProfileSerializer.Meta.fields + (
            'recent_reviews', 'next_available_slots', 'specializations'
        )

    def get_recent_reviews(self, obj):
        recent_bookings = obj.mentor_bookings.filter(
            status='completed',
            learner_feedback__isnull=False
        ).exclude(learner_feedback='').order_by('-updated_at')[:5]
        
        reviews = []
        for booking in recent_bookings:
            reviews.append({
                'id': booking.id,
                'learner_name': booking.learner.first_name,  # Only first name for privacy
                'rating': booking.learner_rating,
                'feedback': booking.learner_feedback,
                'date': booking.updated_at,
                'subject': booking.subject
            })
        return reviews

    def get_next_available_slots(self, obj):
        from availability.models import AvailabilitySlot
        from availability.serializers import AvailabilitySlotPublicSerializer
        from django.utils import timezone
        
        slots = AvailabilitySlot.objects.filter(
            mentor=obj,
            start_utc__gt=timezone.now(),
            is_booked=False,
            is_blocked=False
        ).order_by('start_utc')[:10]
        
        return AvailabilitySlotPublicSerializer(slots, many=True).data

    def get_specializations(self, obj):
        """Get primary skills as specializations"""
        return obj.mentor_skills.filter(is_primary=True).values_list('skill__name', flat=True)


class MentorSearchSerializer(serializers.Serializer):
    """Serializer for mentor search parameters"""
    search = serializers.CharField(required=False, help_text="Search in name, bio, skills")
    skills = serializers.CharField(required=False, help_text="Comma-separated skill names or IDs")
    min_rating = serializers.FloatField(min_value=0, max_value=5, required=False)
    max_rating = serializers.FloatField(min_value=0, max_value=5, required=False)
    min_rate = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    max_rate = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    country = serializers.CharField(required=False)
    timezone = serializers.CharField(required=False)
    available_now = serializers.BooleanField(required=False)
    available_today = serializers.BooleanField(required=False)
    available_this_week = serializers.BooleanField(required=False)
    has_availability = serializers.BooleanField(required=False)
    experience_level = serializers.ChoiceField(
        choices=['beginner', 'intermediate', 'advanced'],
        required=False
    )
    sort_by = serializers.ChoiceField(
        choices=[
            'rating', '-rating', 'hourly_rate', '-hourly_rate',
            'total_sessions', '-total_sessions', 'created_at', '-created_at',
            'availability', 'relevance'
        ],
        default='-rating'
    )

    def validate(self, data):
        if data.get('min_rating') and data.get('max_rating'):
            if data['min_rating'] > data['max_rating']:
                raise serializers.ValidationError("min_rating cannot be greater than max_rating")
        
        if data.get('min_rate') and data.get('max_rate'):
            if data['min_rate'] > data['max_rate']:
                raise serializers.ValidationError("min_rate cannot be greater than max_rate")
        
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    token = serializers.UUIDField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Validate token
        try:
            user = User.objects.get(
                password_reset_token=attrs['token'],
                password_reset_expires__gt=timezone.now()
            )
        except User.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid or expired token."})
        
        attrs['user'] = user
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification"""
    token = serializers.UUIDField(required=True)

    def validate_token(self, value):
        try:
            user = User.objects.get(
                email_verification_token=value,
                is_email_verified=False
            )
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid verification token.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class TwoFactorSetupSerializer(serializers.Serializer):
    """Serializer for setting up 2FA"""
    password = serializers.CharField(required=True)
    
    def validate_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Password is incorrect.")
        return value


class TwoFactorVerifySerializer(serializers.Serializer):
    """Serializer for verifying 2FA codes"""
    code = serializers.CharField(max_length=6, min_length=6)
    
    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Code must be 6 digits.")
        return value


class TwoFactorEnableSerializer(serializers.Serializer):
    """Serializer for enabling 2FA"""
    code = serializers.CharField(max_length=6, min_length=6)
    
    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Code must be 6 digits.")
        return value


class TwoFactorBackupTokenSerializer(serializers.Serializer):
    """Serializer for backup token verification"""
    token = serializers.CharField(max_length=16, min_length=16)


class TwoFactorStatusSerializer(serializers.ModelSerializer):
    """Serializer for 2FA status"""
    backup_tokens_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TwoFactorAuth
        fields = ['is_enabled', 'backup_tokens_count', 'created_at', 'last_used']
        read_only_fields = fields
    
    def get_backup_tokens_count(self, obj):
        return len([token for token in obj.backup_tokens if token])
