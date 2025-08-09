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
    subject = models.CharField(max_length=200, default='Mentoring Session', help_text="What will be covered in this session")
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
    
    # Advanced booking relationships
    recurring_template = models.ForeignKey(
        'RecurringBookingTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_bookings',
        help_text="If this booking was generated from a recurring template"
    )
    booking_template = models.ForeignKey(
        'BookingTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings_created',
        help_text="Template used to create this booking"
    )
    package_purchase = models.ForeignKey(
        'BookingPackagePurchase',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings_used',
        help_text="Package purchase used for this booking"
    )
    
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
    to_status = models.CharField(max_length=30, default='pending')
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


class RecurringBookingTemplate(models.Model):
    """Template for recurring booking sessions"""
    FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ]
    
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recurring_templates_as_mentor'
    )
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recurring_templates_as_learner'
    )
    
    # Template details
    title = models.CharField(max_length=200, default='Recurring Mentoring Session')
    description = models.TextField(blank=True)
    subject = models.CharField(max_length=200, help_text="Session topic/subject")
    
    # Recurrence settings
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    interval = models.PositiveIntegerField(default=1, help_text="Every X weeks/months")
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES, null=True, blank=True)
    time_utc = models.TimeField(help_text="Session time in UTC")
    duration_minutes = models.PositiveIntegerField(default=60)
    
    # Period settings
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank for indefinite")
    max_sessions = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum number of sessions")
    
    # Pricing
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Status
    is_active = models.BooleanField(default=True)
    paused_until = models.DateField(null=True, blank=True, help_text="Pause until this date")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['mentor', 'is_active']),
            models.Index(fields=['learner', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['frequency', 'weekday']),
        ]
    
    def __str__(self):
        return f"Recurring: {self.learner.full_name} → {self.mentor.full_name} ({self.frequency})"
    
    def get_next_session_date(self):
        """Calculate the next session date based on the template"""
        from datetime import datetime, timedelta
        import calendar
        
        today = timezone.now().date()
        
        if self.end_date and today > self.end_date:
            return None
            
        if self.paused_until and today <= self.paused_until:
            return self.paused_until + timedelta(days=1)
        
        # Count existing sessions
        existing_sessions = self.generated_bookings.count()
        if self.max_sessions and existing_sessions >= self.max_sessions:
            return None
        
        # Find next occurrence
        current_date = max(self.start_date, today)
        
        if self.frequency == 'weekly':
            # Find next occurrence of the weekday
            days_ahead = self.weekday - current_date.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7 * self.interval
            return current_date + timedelta(days=days_ahead)
            
        elif self.frequency == 'biweekly':
            # Every 2 weeks on the specified weekday
            days_ahead = self.weekday - current_date.weekday()
            if days_ahead <= 0:
                days_ahead += 14
            return current_date + timedelta(days=days_ahead)
            
        elif self.frequency == 'monthly':
            # Same weekday of the month (e.g., first Monday)
            # This is a simplified implementation
            next_month = current_date.replace(day=1) + timedelta(days=32)
            next_month = next_month.replace(day=1)
            # Find the correct weekday in the next month
            for day in range(1, 8):
                test_date = next_month.replace(day=day)
                if test_date.weekday() == self.weekday:
                    return test_date
        
        return None


class GroupBooking(models.Model):
    """Group mentoring session booking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_bookings_as_mentor'
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_group_bookings',
        help_text="User who created the group booking"
    )
    
    # Session details
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.CharField(max_length=200)
    
    # Timing
    scheduled_start_utc = models.DateTimeField()
    scheduled_end_utc = models.DateTimeField()
    actual_start_utc = models.DateTimeField(null=True, blank=True)
    actual_end_utc = models.DateTimeField(null=True, blank=True)
    
    # Group settings
    max_participants = models.PositiveIntegerField(default=5)
    min_participants = models.PositiveIntegerField(default=2)
    current_participants = models.PositiveIntegerField(default=1)
    
    # Pricing
    price_per_person = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    
    # Status
    status = models.CharField(max_length=30, choices=[
        ('open', 'Open for Registration'),
        ('full', 'Full'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='open')
    
    # Meeting details
    meeting_url = models.URLField(blank=True)
    meeting_id = models.CharField(max_length=100, blank=True)
    meeting_password = models.CharField(max_length=50, blank=True)
    
    # Requirements
    prerequisites = models.TextField(blank=True, help_text="Prerequisites for participants")
    materials_needed = models.TextField(blank=True, help_text="Materials participants should prepare")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['mentor', 'status']),
            models.Index(fields=['scheduled_start_utc']),
            models.Index(fields=['status', 'scheduled_start_utc']),
        ]
    
    def __str__(self):
        return f"Group: {self.title} ({self.current_participants}/{self.max_participants})"
    
    def can_join(self):
        """Check if the group booking can accept more participants"""
        return (
            self.status == 'open' and 
            self.current_participants < self.max_participants and
            self.scheduled_start_utc > timezone.now()
        )
    
    def is_ready_to_confirm(self):
        """Check if group has minimum participants to confirm"""
        return self.current_participants >= self.min_participants


class GroupBookingParticipant(models.Model):
    """Participant in a group booking"""
    group_booking = models.ForeignKey(
        GroupBooking,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_participations'
    )
    
    # Participation details
    joined_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('registered', 'Registered'),
        ('confirmed', 'Confirmed'),
        ('attended', 'Attended'),
        ('no_show', 'No Show'),
        ('cancelled', 'Cancelled'),
    ], default='registered')
    
    # Payment
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ], default='pending')
    
    # Feedback
    rating = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5
    feedback = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['group_booking', 'learner']
        indexes = [
            models.Index(fields=['learner', 'status']),
            models.Index(fields=['group_booking', 'status']),
        ]
    
    def __str__(self):
        return f"{self.learner.full_name} in {self.group_booking.title}"


class BookingPackage(models.Model):
    """Predefined booking packages (e.g., 5 sessions for discount)"""
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='booking_packages'
    )
    
    # Package details
    name = models.CharField(max_length=200)
    description = models.TextField()
    session_count = models.PositiveIntegerField()
    validity_days = models.PositiveIntegerField(help_text="Days to use all sessions")
    
    # Pricing
    regular_price = models.DecimalField(max_digits=10, decimal_places=2)
    package_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Settings
    is_active = models.BooleanField(default=True)
    auto_schedule = models.BooleanField(default=False, help_text="Auto-schedule sessions weekly")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['mentor', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.session_count} sessions for {self.mentor.full_name}"
    
    def calculate_savings(self):
        """Calculate total savings with this package"""
        return self.regular_price - self.package_price


class BookingPackagePurchase(models.Model):
    """User purchase of a booking package"""
    package = models.ForeignKey(
        BookingPackage,
        on_delete=models.CASCADE,
        related_name='purchases'
    )
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='package_purchases'
    )
    
    # Purchase details
    purchased_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Usage tracking
    sessions_used = models.PositiveIntegerField(default=0)
    sessions_remaining = models.PositiveIntegerField()
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['learner', 'is_active']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.learner.full_name} - {self.package.name} ({self.sessions_remaining} left)"
    
    def can_use_session(self):
        """Check if package can be used for booking"""
        return (
            self.is_active and 
            self.sessions_remaining > 0 and 
            self.expires_at > timezone.now()
        )
    
    def use_session(self):
        """Mark one session as used"""
        if self.can_use_session():
            self.sessions_used += 1
            self.sessions_remaining -= 1
            if self.sessions_remaining == 0:
                self.is_active = False
            self.save()
            return True
        return False


class BookingTemplate(models.Model):
    """Reusable booking templates for mentors"""
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='booking_templates'
    )
    
    # Template details
    name = models.CharField(max_length=200)
    description = models.TextField()
    default_subject = models.CharField(max_length=200)
    default_duration_minutes = models.PositiveIntegerField(default=60)
    
    # Default settings
    default_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    requires_approval = models.BooleanField(default=True)
    auto_confirm = models.BooleanField(default=False)
    
    # Content
    preparation_notes = models.TextField(blank=True, help_text="What learners should prepare")
    session_outline = models.TextField(blank=True, help_text="Typical session structure")
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True, help_text="Visible to learners")
    
    # Usage stats
    times_used = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['mentor', 'is_active']),
            models.Index(fields=['is_public', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} by {self.mentor.full_name}"


# Add relationship fields to existing Booking model
# We'll do this via a migration or by adding a foreign key field
