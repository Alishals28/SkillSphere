from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, datetime
import pytz


class WeeklyAvailability(models.Model):
    """Weekly recurring availability pattern for mentors"""
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    mentor = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='weekly_availability',
        limit_choices_to={'role': 'mentor'}
    )
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()  # In mentor's timezone
    end_time = models.TimeField()    # In mentor's timezone
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('mentor', 'weekday', 'start_time', 'end_time')
        ordering = ['weekday', 'start_time']
        indexes = [
            models.Index(fields=['mentor', 'weekday', 'is_active']),
        ]

    def __str__(self):
        return f"{self.mentor.full_name} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time")


class AvailabilitySlot(models.Model):
    """Specific time slots (can be one-time or generated from weekly pattern)"""
    mentor = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='availability_slots',
        limit_choices_to={'role': 'mentor'}
    )
    start_utc = models.DateTimeField()
    end_utc = models.DateTimeField()
    is_booked = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)  # Manually blocked by mentor
    booking = models.OneToOneField(
        'bookings.Booking', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='availability_slot'
    )
    weekly_availability = models.ForeignKey(
        WeeklyAvailability, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="If this slot was generated from weekly pattern"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_utc']
        indexes = [
            models.Index(fields=['mentor', 'start_utc']),
            models.Index(fields=['start_utc', 'end_utc']),
            models.Index(fields=['is_booked', 'is_blocked']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(start_utc__lt=models.F('end_utc')),
                name='start_before_end'
            ),
        ]

    def __str__(self):
        status = "Booked" if self.is_booked else "Blocked" if self.is_blocked else "Available"
        return f"{self.mentor.full_name} - {self.start_utc} ({status})"

    @property
    def is_available(self):
        """Check if slot is available for booking"""
        return not self.is_booked and not self.is_blocked and self.start_utc > timezone.now()

    @property
    def duration_minutes(self):
        """Get duration in minutes"""
        return int((self.end_utc - self.start_utc).total_seconds() / 60)

    def convert_to_timezone(self, target_timezone):
        """Convert slot times to specific timezone"""
        tz = pytz.timezone(target_timezone)
        return {
            'start': self.start_utc.astimezone(tz),
            'end': self.end_utc.astimezone(tz),
        }

    def clean(self):
        if self.start_utc >= self.end_utc:
            raise ValidationError("Start time must be before end time")
        
        # Check for overlapping slots for the same mentor
        overlapping = AvailabilitySlot.objects.filter(
            mentor=self.mentor,
            start_utc__lt=self.end_utc,
            end_utc__gt=self.start_utc
        ).exclude(pk=self.pk)
        
        if overlapping.exists():
            raise ValidationError("This slot overlaps with existing availability")


class AvailabilityException(models.Model):
    """Exceptions to regular availability (vacation, breaks, etc.)"""
    EXCEPTION_TYPES = [
        ('unavailable', 'Unavailable'),
        ('vacation', 'Vacation'),
        ('break', 'Break'),
        ('busy', 'Busy'),
        ('custom', 'Custom'),
    ]

    mentor = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='availability_exceptions',
        limit_choices_to={'role': 'mentor'}
    )
    start_utc = models.DateTimeField()
    end_utc = models.DateTimeField()
    exception_type = models.CharField(max_length=20, choices=EXCEPTION_TYPES, default='unavailable')
    reason = models.TextField(blank=True)
    is_all_day = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_utc']
        indexes = [
            models.Index(fields=['mentor', 'start_utc']),
            models.Index(fields=['start_utc', 'end_utc']),
        ]

    def __str__(self):
        return f"{self.mentor.full_name} - {self.get_exception_type_display()} ({self.start_utc.date()})"

    def clean(self):
        if self.start_utc >= self.end_utc:
            raise ValidationError("Start time must be before end time")


class MentorAvailabilitySettings(models.Model):
    """Global availability settings for mentors"""
    mentor = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='availability_settings',
        limit_choices_to={'role': 'mentor'}
    )
    min_booking_notice_hours = models.PositiveIntegerField(
        default=24,
        help_text="Minimum hours notice required for booking"
    )
    max_booking_advance_days = models.PositiveIntegerField(
        default=60,
        help_text="Maximum days in advance bookings can be made"
    )
    default_session_duration_minutes = models.PositiveIntegerField(
        default=60,
        help_text="Default session duration in minutes"
    )
    buffer_minutes_between_sessions = models.PositiveIntegerField(
        default=15,
        help_text="Buffer time between sessions"
    )
    auto_approve_bookings = models.BooleanField(
        default=False,
        help_text="Automatically approve booking requests"
    )
    is_accepting_new_bookings = models.BooleanField(
        default=True,
        help_text="Whether mentor is currently accepting new bookings"
    )
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        help_text="Mentor's timezone for availability"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mentor Availability Settings"
        verbose_name_plural = "Mentor Availability Settings"

    def __str__(self):
        return f"{self.mentor.full_name} - Availability Settings"
