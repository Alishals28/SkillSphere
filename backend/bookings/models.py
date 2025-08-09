from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
import uuid


class Booking(models.Model):
    """Session booking model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('declined', 'Declined'),
        ('cancelled_by_learner', 'Cancelled by Learner'),
        ('cancelled_by_mentor', 'Cancelled by Mentor'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('no_show_learner', 'No Show - Learner'),
        ('no_show_mentor', 'No Show - Mentor'),
    ]

    CANCELLATION_REASONS = [
        ('schedule_conflict', 'Schedule Conflict'),
        ('emergency', 'Emergency'),
        ('illness', 'Illness'),
        ('technical_issues', 'Technical Issues'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Participants
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mentor_bookings',
        limit_choices_to={'role': 'mentor'}
    )
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learner_bookings',
        limit_choices_to={'role': 'learner'}
    )
    
    # Session details
    subject = models.CharField(max_length=200, help_text="What will be covered in this session")
    requested_skills = models.ManyToManyField(
        'skills.Skill',
        blank=True,
        help_text="Skills to focus on during session"
    )
    
    # Timing
    requested_start_utc = models.DateTimeField()
    requested_end_utc = models.DateTimeField()
    confirmed_start_utc = models.DateTimeField(null=True, blank=True)
    confirmed_end_utc = models.DateTimeField(null=True, blank=True)
    
    # Status and workflow
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    # Pricing
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    
    # Communication
    learner_notes = models.TextField(
        blank=True,
        help_text="Notes from learner about what they want to learn"
    )
    mentor_notes = models.TextField(
        blank=True,
        help_text="Notes from mentor about the session"
    )
    admin_notes = models.TextField(blank=True, help_text="Internal admin notes")
    
    # Cancellation
    cancellation_reason = models.CharField(
        max_length=30,
        choices=CANCELLATION_REASONS,
        blank=True
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_bookings'
    )
    
    # Meeting details
    meeting_url = models.URLField(blank=True, help_text="Video call link")
    meeting_id = models.CharField(max_length=100, blank=True)
    meeting_password = models.CharField(max_length=50, blank=True)
    
    # Feedback and rating (after session)
    learner_rating = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5
    learner_feedback = models.TextField(blank=True)
    mentor_feedback = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['mentor', 'status']),
            models.Index(fields=['learner', 'status']),
            models.Index(fields=['status', 'requested_start_utc']),
            models.Index(fields=['requested_start_utc', 'requested_end_utc']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(requested_start_utc__lt=models.F('requested_end_utc')),
                name='requested_start_before_end'
            ),
        ]

    def __str__(self):
        return f"{self.subject} - {self.learner.full_name} with {self.mentor.full_name}"

    @property
    def duration_minutes(self):
        """Get session duration in minutes"""
        start = self.confirmed_start_utc or self.requested_start_utc
        end = self.confirmed_end_utc or self.requested_end_utc
        return int((end - start).total_seconds() / 60)

    @property
    def duration_hours(self):
        """Get session duration in hours"""
        return self.duration_minutes / 60

    @property
    def is_upcoming(self):
        """Check if session is in the future"""
        start_time = self.confirmed_start_utc or self.requested_start_utc
        return start_time > timezone.now()

    @property
    def is_in_progress(self):
        """Check if session is currently happening"""
        now = timezone.now()
        start_time = self.confirmed_start_utc or self.requested_start_utc
        end_time = self.confirmed_end_utc or self.requested_end_utc
        return start_time <= now <= end_time

    @property
    def can_be_cancelled(self):
        """Check if booking can still be cancelled"""
        if self.status in ['cancelled_by_learner', 'cancelled_by_mentor', 'completed']:
            return False
        
        start_time = self.confirmed_start_utc or self.requested_start_utc
        # Can cancel up to 2 hours before session
        return start_time > timezone.now() + timezone.timedelta(hours=2)

    def calculate_total_amount(self):
        """Calculate total amount based on duration and hourly rate"""
        if self.hourly_rate:
            self.total_amount = self.hourly_rate * Decimal(str(self.duration_hours))
            return self.total_amount
        return None

    def confirm_booking(self, confirmed_start=None, confirmed_end=None):
        """Confirm a pending booking"""
        if self.status != 'pending':
            raise ValidationError("Only pending bookings can be confirmed")
        
        self.status = 'confirmed'
        self.confirmed_at = timezone.now()
        
        if confirmed_start:
            self.confirmed_start_utc = confirmed_start
        else:
            self.confirmed_start_utc = self.requested_start_utc
            
        if confirmed_end:
            self.confirmed_end_utc = confirmed_end
        else:
            self.confirmed_end_utc = self.requested_end_utc
        
        # Calculate amount
        self.calculate_total_amount()
        self.save()

    def cancel_booking(self, cancelled_by, reason=None):
        """Cancel a booking"""
        if not self.can_be_cancelled:
            raise ValidationError("This booking cannot be cancelled")
        
        if cancelled_by.role == 'learner':
            self.status = 'cancelled_by_learner'
        elif cancelled_by.role == 'mentor':
            self.status = 'cancelled_by_mentor'
        
        self.cancelled_by = cancelled_by
        self.cancelled_at = timezone.now()
        if reason:
            self.cancellation_reason = reason
        
        self.save()

    def mark_completed(self):
        """Mark booking as completed"""
        if self.status != 'confirmed':
            raise ValidationError("Only confirmed bookings can be marked as completed")
        
        self.status = 'completed'
        self.save()

    def clean(self):
        # Validate times
        if self.requested_start_utc >= self.requested_end_utc:
            raise ValidationError("Start time must be before end time")
        
        # Validate confirmed times if they exist
        if self.confirmed_start_utc and self.confirmed_end_utc:
            if self.confirmed_start_utc >= self.confirmed_end_utc:
                raise ValidationError("Confirmed start time must be before confirmed end time")
        
        # Validate participants
        if self.mentor_id == self.learner_id:
            raise ValidationError("Mentor and learner cannot be the same person")
        
        # Check for overlapping confirmed bookings for the mentor
        if self.status == 'confirmed' and self.confirmed_start_utc and self.confirmed_end_utc:
            overlapping = Booking.objects.filter(
                mentor=self.mentor,
                status='confirmed',
                confirmed_start_utc__lt=self.confirmed_end_utc,
                confirmed_end_utc__gt=self.confirmed_start_utc
            ).exclude(pk=self.pk)
            
            if overlapping.exists():
                raise ValidationError("This booking overlaps with an existing confirmed booking")


class BookingStatusHistory(models.Model):
    """Track status changes for bookings"""
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    from_status = models.CharField(max_length=30, blank=True)
    to_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Booking Status Histories"

    def __str__(self):
        return f"{self.booking.id} - {self.from_status} → {self.to_status}"
