from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, timedelta
import pytz
from .models import (
    WeeklyAvailability, 
    AvailabilitySlot, 
    AvailabilityException,
    MentorAvailabilitySettings
)


class WeeklyAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for weekly availability patterns"""
    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)
    
    class Meta:
        model = WeeklyAvailability
        fields = [
            'id', 'weekday', 'weekday_display', 'start_time', 'end_time', 
            'is_active', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        validated_data['mentor'] = self.context['request'].user
        return super().create(validated_data)


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    """Serializer for availability slots"""
    is_available = serializers.ReadOnlyField()
    duration_minutes = serializers.ReadOnlyField()
    mentor_name = serializers.CharField(source='mentor.full_name', read_only=True)
    
    class Meta:
        model = AvailabilitySlot
        fields = [
            'id', 'start_utc', 'end_utc', 'is_booked', 'is_blocked',
            'is_available', 'duration_minutes', 'notes', 'mentor_name',
            'weekly_availability', 'created_at'
        ]
        read_only_fields = ['is_booked', 'booking']

    def create(self, validated_data):
        validated_data['mentor'] = self.context['request'].user
        return super().create(validated_data)


class AvailabilitySlotPublicSerializer(serializers.ModelSerializer):
    """Public serializer for availability slots (for learners browsing)"""
    duration_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = AvailabilitySlot
        fields = ['id', 'start_utc', 'end_utc', 'duration_minutes']


class AvailabilityExceptionSerializer(serializers.ModelSerializer):
    """Serializer for availability exceptions"""
    exception_type_display = serializers.CharField(source='get_exception_type_display', read_only=True)
    
    class Meta:
        model = AvailabilityException
        fields = [
            'id', 'start_utc', 'end_utc', 'exception_type', 'exception_type_display',
            'reason', 'is_all_day', 'created_at'
        ]

    def create(self, validated_data):
        validated_data['mentor'] = self.context['request'].user
        return super().create(validated_data)


class MentorAvailabilitySettingsSerializer(serializers.ModelSerializer):
    """Serializer for mentor availability settings"""
    
    class Meta:
        model = MentorAvailabilitySettings
        fields = [
            'min_booking_notice_hours', 'max_booking_advance_days',
            'default_session_duration_minutes', 'buffer_minutes_between_sessions',
            'auto_approve_bookings', 'is_accepting_new_bookings', 'timezone',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        validated_data['mentor'] = self.context['request'].user
        return super().create(validated_data)


class AvailabilityBulkCreateSerializer(serializers.Serializer):
    """Serializer for bulk creating availability slots"""
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    weekdays = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=6),
        help_text="List of weekdays (0=Monday, 6=Sunday)"
    )
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    session_duration_minutes = serializers.IntegerField(min_value=15, max_value=480)
    break_duration_minutes = serializers.IntegerField(min_value=0, max_value=60, default=15)
    
    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("End date must be after start date")
        
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("End time must be after start time")
        
        # Check if date range is reasonable (not more than 3 months)
        if (data['end_date'] - data['start_date']).days > 90:
            raise serializers.ValidationError("Date range cannot exceed 90 days")
        
        return data

    def create(self, validated_data):
        mentor = self.context['request'].user
        created_slots = []
        
        current_date = validated_data['start_date']
        end_date = validated_data['end_date']
        
        while current_date <= end_date:
            if current_date.weekday() in validated_data['weekdays']:
                # Create slots for this day
                current_time = datetime.combine(current_date, validated_data['start_time'])
                end_time = datetime.combine(current_date, validated_data['end_time'])
                
                # Convert to mentor's timezone then to UTC
                mentor_tz = pytz.timezone(mentor.timezone)
                current_time = mentor_tz.localize(current_time)
                end_time = mentor_tz.localize(end_time)
                
                while current_time < end_time:
                    slot_end = current_time + timedelta(minutes=validated_data['session_duration_minutes'])
                    
                    if slot_end <= end_time:
                        slot = AvailabilitySlot.objects.create(
                            mentor=mentor,
                            start_utc=current_time.astimezone(pytz.UTC),
                            end_utc=slot_end.astimezone(pytz.UTC)
                        )
                        created_slots.append(slot)
                    
                    current_time = slot_end + timedelta(minutes=validated_data['break_duration_minutes'])
            
            current_date += timedelta(days=1)
        
        return created_slots


class MentorAvailabilityCalendarSerializer(serializers.Serializer):
    """Serializer for mentor availability calendar view"""
    date = serializers.DateField()
    available_slots = AvailabilitySlotPublicSerializer(many=True)
    total_slots = serializers.IntegerField()
    booked_slots = serializers.IntegerField()
    exceptions = AvailabilityExceptionSerializer(many=True)
