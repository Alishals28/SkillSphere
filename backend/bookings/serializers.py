from rest_framework import serializers
from django.db.models import Avg, Count
from django.utils import timezone
from .models import Booking, BookingStatusHistory
from skills.serializers import SkillSerializer


class BookingSerializer(serializers.ModelSerializer):
    """Full booking serializer for participants"""
    mentor_name = serializers.CharField(source='mentor.full_name', read_only=True)
    learner_name = serializers.CharField(source='learner.full_name', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    duration_hours = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_in_progress = serializers.ReadOnlyField()
    can_be_cancelled = serializers.ReadOnlyField()
    requested_skills = SkillSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'mentor', 'mentor_name', 'learner', 'learner_name',
            'subject', 'requested_skills', 'requested_start_utc', 'requested_end_utc',
            'confirmed_start_utc', 'confirmed_end_utc', 'status', 'status_display',
            'hourly_rate', 'total_amount', 'currency', 'learner_notes', 'mentor_notes',
            'meeting_url', 'meeting_id', 'learner_rating', 'learner_feedback',
            'mentor_feedback', 'duration_minutes', 'duration_hours', 'is_upcoming',
            'is_in_progress', 'can_be_cancelled', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'total_amount', 'confirmed_start_utc', 'confirmed_end_utc', 'status',
            'meeting_url', 'meeting_id'
        ]


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings"""
    from skills.models import Skill
    requested_skills = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Skill.objects.filter(is_active=True),
        required=False
    )
    
    class Meta:
        model = Booking
        fields = [
            'mentor', 'subject', 'requested_skills', 'requested_start_utc',
            'requested_end_utc', 'learner_notes'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, data):
        user = self.context['request'].user
        
        # Ensure user is a learner
        if user.role != 'learner':
            raise serializers.ValidationError("Only learners can create bookings")
        
        # Ensure mentor is approved
        mentor = data['mentor']
        if not mentor.can_mentor():
            raise serializers.ValidationError("Selected mentor is not available")
        
        # Validate timing
        if data['requested_start_utc'] >= data['requested_end_utc']:
            raise serializers.ValidationError("Start time must be before end time")
        
        # Check if booking is in the future
        if data['requested_start_utc'] <= timezone.now():
            raise serializers.ValidationError("Booking must be in the future")
        
        # Check mentor availability settings
        if hasattr(mentor, 'availability_settings'):
            settings = mentor.availability_settings
            
            # Check minimum notice
            min_notice = timezone.now() + timezone.timedelta(hours=settings.min_booking_notice_hours)
            if data['requested_start_utc'] < min_notice:
                raise serializers.ValidationError(
                    f"Booking requires at least {settings.min_booking_notice_hours} hours notice"
                )
            
            # Check maximum advance booking
            max_advance = timezone.now() + timezone.timedelta(days=settings.max_booking_advance_days)
            if data['requested_start_utc'] > max_advance:
                raise serializers.ValidationError(
                    f"Bookings cannot be made more than {settings.max_booking_advance_days} days in advance"
                )
        
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['learner'] = user
        
        # Set hourly rate from mentor's current rate
        mentor = validated_data['mentor']
        validated_data['hourly_rate'] = mentor.hourly_rate
        
        # Extract skills
        skills = validated_data.pop('requested_skills', [])
        
        booking = super().create(validated_data)
        
        # Add skills
        if skills:
            booking.requested_skills.set(skills)
        
        # Calculate total amount
        booking.calculate_total_amount()
        booking.save()
        
        return booking


class BookingStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating booking status"""
    status = serializers.ChoiceField(choices=Booking.STATUS_CHOICES)
    reason = serializers.CharField(required=False, allow_blank=True)
    confirmed_start_utc = serializers.DateTimeField(required=False)
    confirmed_end_utc = serializers.DateTimeField(required=False)
    mentor_notes = serializers.CharField(required=False, allow_blank=True)
    meeting_url = serializers.URLField(required=False, allow_blank=True)
    meeting_id = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        booking = self.context['booking']
        user = self.context['request'].user
        new_status = data['status']
        
        # Validate status transitions
        valid_transitions = {
            'pending': ['confirmed', 'declined', 'cancelled_by_mentor'],
            'confirmed': ['cancelled_by_learner', 'cancelled_by_mentor', 'in_progress', 'completed', 'no_show_learner', 'no_show_mentor'],
            'in_progress': ['completed', 'cancelled_by_mentor'],
        }
        
        if booking.status not in valid_transitions:
            raise serializers.ValidationError(f"Cannot change status from {booking.status}")
        
        if new_status not in valid_transitions[booking.status]:
            raise serializers.ValidationError(f"Cannot change status from {booking.status} to {new_status}")
        
        # Check permissions
        if new_status in ['confirmed', 'declined', 'cancelled_by_mentor', 'no_show_learner'] and user != booking.mentor:
            raise serializers.ValidationError("Only the mentor can perform this action")
        
        if new_status in ['cancelled_by_learner', 'no_show_mentor'] and user != booking.learner:
            raise serializers.ValidationError("Only the learner can perform this action")
        
        # Validate confirmed times if provided
        if data.get('confirmed_start_utc') and data.get('confirmed_end_utc'):
            if data['confirmed_start_utc'] >= data['confirmed_end_utc']:
                raise serializers.ValidationError("Confirmed start time must be before confirmed end time")
        
        return data


class BookingFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for booking feedback"""
    
    class Meta:
        model = Booking
        fields = ['learner_rating', 'learner_feedback', 'mentor_feedback']

    def validate_learner_rating(self, value):
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class BookingListSerializer(serializers.ModelSerializer):
    """Simplified booking serializer for lists"""
    mentor_name = serializers.CharField(source='mentor.full_name', read_only=True)
    learner_name = serializers.CharField(source='learner.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_upcoming = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'mentor_name', 'learner_name', 'subject',
            'requested_start_utc', 'requested_end_utc', 'status', 'status_display',
            'total_amount', 'currency', 'is_upcoming', 'created_at'
        ]


class BookingStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for booking status history"""
    changed_by_name = serializers.CharField(source='changed_by.full_name', read_only=True)
    
    class Meta:
        model = BookingStatusHistory
        fields = [
            'id', 'from_status', 'to_status', 'changed_by', 'changed_by_name',
            'reason', 'created_at'
        ]


class BookingStatisticsSerializer(serializers.Serializer):
    """Serializer for booking statistics"""
    total_bookings = serializers.IntegerField()
    confirmed_bookings = serializers.IntegerField()
    completed_bookings = serializers.IntegerField()
    cancelled_bookings = serializers.IntegerField()
    average_rating = serializers.FloatField()
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    upcoming_bookings = serializers.IntegerField()


class BookingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating bookings"""
    
    class Meta:
        model = Booking
        fields = [
            'subject', 'requested_start_utc', 'requested_end_utc',
            'learner_notes', 'mentor_notes', 'hourly_rate'
        ]
    
    def validate(self, data):
        user = self.context['request'].user
        booking = self.instance
        
        # Only allow updates for certain statuses
        if booking.status not in ['pending', 'confirmed']:
            raise serializers.ValidationError(
                "Booking can only be updated when pending or confirmed"
            )
        
        # Learners can only update certain fields
        if user.role == 'learner' and user == booking.learner:
            allowed_fields = {'subject', 'learner_notes'}
            provided_fields = set(data.keys())
            if not provided_fields.issubset(allowed_fields):
                raise serializers.ValidationError(
                    "Learners can only update subject and notes"
                )
        
        # Mentors can update more fields
        elif user.role == 'mentor' and user == booking.mentor:
            # Mentors can update timing and rates before confirmation
            if booking.status == 'confirmed':
                allowed_fields = {'mentor_notes'}
                provided_fields = set(data.keys())
                if not provided_fields.issubset(allowed_fields):
                    raise serializers.ValidationError(
                        "Once confirmed, mentors can only update notes"
                    )
        else:
            raise serializers.ValidationError(
                "Only booking participants can update bookings"
            )
        
        # Validate timing if provided
        if 'requested_start_utc' in data and 'requested_end_utc' in data:
            if data['requested_start_utc'] >= data['requested_end_utc']:
                raise serializers.ValidationError("Start time must be before end time")
            
            if data['requested_start_utc'] <= timezone.now():
                raise serializers.ValidationError("Booking must be in the future")
        
        return data
