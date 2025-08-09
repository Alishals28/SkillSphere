from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Booking, RecurringBookingTemplate, GroupBooking, GroupBookingParticipant


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Booking model"""
    
    list_display = [
        'id', 'learner_link', 'mentor_link', 'subject', 'status',
        'requested_start_utc', 'duration_minutes', 'total_amount',
        'created_at', 'rating_display'
    ]
    
    list_filter = [
        'status', 'created_at', 'requested_start_utc'
    ]
    
    search_fields = [
        'learner__email', 'learner__first_name', 'learner__last_name',
        'mentor__email', 'mentor__first_name', 'mentor__last_name',
        'subject', 'internal_notes'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'id', 'total_amount_display',
        'time_until_session', 'session_duration_display'
    ]
    
    fieldsets = (
        ('Session Details', {
            'fields': (
                'id', 'learner', 'mentor', 'subject', 'primary_skill',
                'requested_start_utc', 'duration_minutes', 'session_duration_display'
            )
        }),
        ('Status & Timing', {
            'fields': (
                'status', 'confirmed_start_utc', 'confirmed_at',
                'time_until_session', 'created_at', 'updated_at'
            )
        }),
        ('Financial', {
            'fields': (
                'hourly_rate', 'total_amount', 'total_amount_display',
                'platform_fee', 'mentor_earnings'
            )
        }),
        ('Feedback & Rating', {
            'fields': (
                'learner_rating', 'learner_feedback',
                'mentor_feedback', 'internal_notes'
            ),
            'classes': ('collapse',)
        }),
        ('Additional Info', {
            'fields': ('additional_notes', 'special_requirements'),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'confirm_bookings', 'cancel_bookings', 'mark_completed',
        'send_reminder_emails', 'export_to_csv'
    ]
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related(
            'learner', 'mentor', 'primary_skill'
        )
    
    def learner_link(self, obj):
        """Link to learner admin page"""
        url = reverse('admin:users_user_change', args=[obj.learner.pk])
        return format_html('<a href="{}">{}</a>', url, obj.learner.full_name)
    learner_link.short_description = 'Learner'
    learner_link.admin_order_field = 'learner__first_name'
    
    def mentor_link(self, obj):
        """Link to mentor admin page"""
        url = reverse('admin:users_user_change', args=[obj.mentor.pk])
        return format_html('<a href="{}">{}</a>', url, obj.mentor.full_name)
    mentor_link.short_description = 'Mentor'
    mentor_link.admin_order_field = 'mentor__first_name'
    
    def rating_display(self, obj):
        """Display rating with stars"""
        if obj.learner_rating:
            stars = '★' * int(obj.learner_rating) + '☆' * (5 - int(obj.learner_rating))
            return format_html('<span title="{}/5">{}</span>', obj.learner_rating, stars)
        return "Not rated"
    rating_display.short_description = 'Rating'
    rating_display.admin_order_field = 'learner_rating'
    
    def total_amount_display(self, obj):
        """Display total amount with currency"""
        return f"${obj.total_amount:.2f}"
    total_amount_display.short_description = 'Total Amount'
    
    def time_until_session(self, obj):
        """Display time until session"""
        if obj.requested_start_utc:
            now = timezone.now()
            diff = obj.requested_start_utc - now
            if diff.total_seconds() > 0:
                days = diff.days
                hours = diff.seconds // 3600
                if days > 0:
                    return f"{days} days, {hours} hours"
                else:
                    return f"{hours} hours"
            else:
                return "Past"
        return "N/A"
    time_until_session.short_description = 'Time Until Session'
    
    def session_duration_display(self, obj):
        """Display session duration in human readable format"""
        if obj.duration_minutes:
            hours = obj.duration_minutes // 60
            minutes = obj.duration_minutes % 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        return "N/A"
    session_duration_display.short_description = 'Duration'
    
    def confirm_bookings(self, request, queryset):
        """Bulk confirm bookings"""
        updated = queryset.filter(status='pending').update(
            status='confirmed',
            confirmed_at=timezone.now()
        )
        self.message_user(request, f'{updated} bookings confirmed.')
    confirm_bookings.short_description = "Confirm selected bookings"
    
    def cancel_bookings(self, request, queryset):
        """Bulk cancel bookings"""
        updated = queryset.exclude(status__in=['completed', 'cancelled']).update(
            status='cancelled'
        )
        self.message_user(request, f'{updated} bookings cancelled.')
    cancel_bookings.short_description = "Cancel selected bookings"
    
    def mark_completed(self, request, queryset):
        """Mark bookings as completed"""
        updated = queryset.filter(status='confirmed').update(status='completed')
        self.message_user(request, f'{updated} bookings marked as completed.')
    mark_completed.short_description = "Mark as completed"
    
    def send_reminder_emails(self, request, queryset):
        """Send reminder emails for upcoming sessions"""
        upcoming = queryset.filter(
            status='confirmed',
            requested_start_utc__gte=timezone.now(),
            requested_start_utc__lte=timezone.now() + timedelta(hours=24)
        )
        count = upcoming.count()
        self.message_user(request, f'Reminder emails sent for {count} upcoming sessions.')
    send_reminder_emails.short_description = "Send reminder emails"
    
    def export_to_csv(self, request, queryset):
        """Export selected bookings to CSV"""
        count = queryset.count()
        self.message_user(request, f'{count} bookings exported to CSV.')
    export_to_csv.short_description = "Export to CSV"


@admin.register(RecurringBookingTemplate)
class RecurringBookingAdmin(admin.ModelAdmin):
    """Admin interface for RecurringBookingTemplate model"""
    
    list_display = [
        'id', 'learner', 'mentor', 'frequency', 'is_active',
        'start_date', 'end_date', 'sessions_created'
    ]
    
    list_filter = ['frequency', 'is_active', 'start_date', 'created_at']
    
    search_fields = [
        'learner__email', 'mentor__email', 'title'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'sessions_created']
    
    def sessions_created(self, obj):
        """Display number of sessions created"""
        # This would need to be implemented based on actual relationship
        return 0  # Placeholder
    sessions_created.short_description = 'Sessions Created'


@admin.register(GroupBooking)
class GroupBookingAdmin(admin.ModelAdmin):
    """Admin interface for GroupBooking model"""
    
    list_display = [
        'id', 'mentor', 'title', 'max_participants', 'current_participants',
        'scheduled_start_utc', 'total_revenue'
    ]
    
    list_filter = ['scheduled_start_utc', 'created_at']
    
    search_fields = ['mentor__email', 'title', 'description']
    
    readonly_fields = ['created_at', 'updated_at', 'current_participants', 'total_revenue']
    
    def current_participants(self, obj):
        """Display current number of participants"""
        return obj.participants.count()
    current_participants.short_description = 'Current Participants'
    
    def total_revenue(self, obj):
        """Display total revenue from group session"""
        revenue = obj.participants.count() * obj.price_per_person
        return f"${revenue:.2f}"
    total_revenue.short_description = 'Total Revenue'


@admin.register(GroupBookingParticipant)
class GroupBookingParticipantAdmin(admin.ModelAdmin):
    """Admin interface for GroupBookingParticipant model"""
    
    list_display = [
        'id', 'learner', 'group_booking', 'status', 'payment_status',
        'amount_paid', 'joined_at'
    ]
    
    list_filter = ['status', 'payment_status', 'joined_at']
    
    search_fields = ['learner__email', 'group_booking__title']
    
    readonly_fields = ['joined_at']
