from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from bookings.models import Booking
from notifications.services import NotificationService
from notifications.models import NotificationPreference


class Command(BaseCommand):
    help = 'Send session reminder notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--minutes',
            type=int,
            default=30,
            help='Minutes before session to send reminder (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending'
        )

    def handle(self, *args, **options):
        minutes_before = options['minutes']
        dry_run = options['dry_run']
        
        # Calculate the time window for reminders
        now = timezone.now()
        reminder_time = now + timedelta(minutes=minutes_before)
        
        # Find confirmed bookings starting in the specified time window
        # (Give a 5-minute buffer to account for command execution timing)
        bookings = Booking.objects.filter(
            status='confirmed',
            confirmed_start_utc__gte=now + timedelta(minutes=minutes_before - 5),
            confirmed_start_utc__lte=now + timedelta(minutes=minutes_before + 5)
        ).select_related('mentor', 'learner')
        
        reminder_count = 0
        
        for booking in bookings:
            # Check if we've already sent a reminder for this booking
            existing_reminders = booking.notifications.filter(
                type='session_reminder'
            ).exists()
            
            if existing_reminders:
                self.stdout.write(
                    self.style.WARNING(
                        f'Reminder already sent for booking {booking.id}'
                    )
                )
                continue
            
            if dry_run:
                self.stdout.write(
                    f'Would send reminder for booking {booking.id}: {booking.subject} '
                    f'with {booking.mentor.full_name} and {booking.learner.full_name} '
                    f'starting at {booking.confirmed_start_utc}'
                )
            else:
                # Get user preferences for reminder timing
                for user in [booking.mentor, booking.learner]:
                    preferences, _ = NotificationPreference.objects.get_or_create(
                        user=user
                    )
                    
                    # Use user's preferred reminder time or default
                    user_reminder_minutes = preferences.session_reminder_minutes
                    
                    # Only send if this matches the user's preferred timing
                    if abs(user_reminder_minutes - minutes_before) <= 5:
                        try:
                            NotificationService.send_session_reminder_notification(
                                booking, user_reminder_minutes
                            )
                            reminder_count += 1
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Sent reminder to {user.email} for booking {booking.id}'
                                )
                            )
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(
                                    f'Failed to send reminder to {user.email}: {str(e)}'
                                )
                            )
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Dry run completed. Would send {len(bookings) * 2} reminder notifications.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Sent {reminder_count} reminder notifications for {len(bookings)} bookings.'
                )
            )
