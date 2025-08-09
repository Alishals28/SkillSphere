from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Notification, NotificationPreference
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for creating and sending notifications"""
    
    @staticmethod
    def create_notification(
        user,
        notification_type: str,
        title: str,
        message: str,
        payload: Optional[Dict[str, Any]] = None,
        priority: str = 'normal',
        action_url: Optional[str] = None,
        action_text: Optional[str] = None,
        expires_at: Optional[timezone.datetime] = None,
        related_booking=None,
        related_session=None,
        send_email: bool = True
    ) -> Notification:
        """
        Create a notification and optionally send email
        """
        notification = Notification.objects.create(
            user=user,
            type=notification_type,
            title=title,
            message=message,
            payload=payload or {},
            priority=priority,
            action_url=action_url,
            action_text=action_text,
            expires_at=expires_at,
            related_booking=related_booking,
            related_session=related_session
        )
        
        # Send email if preferences allow it
        if send_email:
            NotificationService.send_email_notification(notification)
        
        return notification
    
    @staticmethod
    def send_email_notification(notification: Notification) -> bool:
        """
        Send email notification based on user preferences
        """
        try:
            # Get user preferences
            preferences, _ = NotificationPreference.objects.get_or_create(
                user=notification.user
            )
            
            # Check if user wants email for this type
            should_send_email = NotificationService._should_send_email(
                notification.type, preferences
            )
            
            if not should_send_email:
                return False
            
            # Prepare email content
            subject = f"SkillSphere: {notification.title}"
            
            # Create email context
            context = {
                'user': notification.user,
                'notification': notification,
                'action_url': notification.action_url,
                'action_text': notification.action_text or 'View Details',
                'site_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            }
            
            # Try to use template, fallback to plain text
            try:
                html_message = render_to_string(
                    f'notifications/email_{notification.type}.html',
                    context
                )
            except:
                html_message = None
            
            # Send email
            send_mail(
                subject=subject,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                html_message=html_message,
                fail_silently=True
            )
            
            logger.info(f"Email notification sent to {notification.user.email} for {notification.type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False
    
    @staticmethod
    def _should_send_email(notification_type: str, preferences: NotificationPreference) -> bool:
        """
        Check if email should be sent based on notification type and user preferences
        """
        email_mapping = {
            'booking_request': preferences.email_booking_requests,
            'booking_confirmed': preferences.email_booking_confirmations,
            'booking_cancelled': preferences.email_booking_confirmations,
            'booking_completed': preferences.email_booking_confirmations,
            'session_starting': preferences.email_session_reminders,
            'session_reminder': preferences.email_session_reminders,
            'feedback_received': preferences.email_feedback_received,
            'mentor_approved': preferences.email_general_updates,
            'mentor_rejected': preferences.email_general_updates,
            'general': preferences.email_general_updates,
            'system': preferences.email_general_updates,
        }
        
        return email_mapping.get(notification_type, True)
    
    @staticmethod
    def send_booking_request_notification(booking):
        """Send notification when new booking is requested"""
        NotificationService.create_notification(
            user=booking.mentor,
            notification_type='booking_request',
            title=f'New booking request from {booking.learner.full_name}',
            message=f'{booking.learner.full_name} has requested a session: "{booking.subject}"',
            payload={
                'booking_id': booking.id,
                'learner_name': booking.learner.full_name,
                'subject': booking.subject,
                'requested_start': booking.requested_start_utc.isoformat(),
                'requested_end': booking.requested_end_utc.isoformat(),
            },
            priority='high',
            action_url=f'/mentor/bookings/{booking.id}',
            action_text='Review Request',
            related_booking=booking,
            expires_at=timezone.now() + timezone.timedelta(days=7)
        )
    
    @staticmethod
    def send_booking_confirmed_notification(booking):
        """Send notification when booking is confirmed"""
        NotificationService.create_notification(
            user=booking.learner,
            notification_type='booking_confirmed',
            title=f'Session confirmed with {booking.mentor.full_name}',
            message=f'Your session "{booking.subject}" has been confirmed by {booking.mentor.full_name}',
            payload={
                'booking_id': booking.id,
                'mentor_name': booking.mentor.full_name,
                'subject': booking.subject,
                'confirmed_start': booking.confirmed_start_utc.isoformat() if booking.confirmed_start_utc else None,
                'confirmed_end': booking.confirmed_end_utc.isoformat() if booking.confirmed_end_utc else None,
            },
            priority='high',
            action_url=f'/learner/bookings/{booking.id}',
            action_text='View Session',
            related_booking=booking
        )
    
    @staticmethod
    def send_booking_cancelled_notification(booking, cancelled_by):
        """Send notification when booking is cancelled"""
        if cancelled_by == booking.mentor:
            # Notify learner
            user = booking.learner
            title = f'Session cancelled by {booking.mentor.full_name}'
            message = f'Your session "{booking.subject}" has been cancelled by the mentor'
        else:
            # Notify mentor
            user = booking.mentor
            title = f'Session cancelled by {booking.learner.full_name}'
            message = f'The session "{booking.subject}" has been cancelled by the learner'
        
        NotificationService.create_notification(
            user=user,
            notification_type='booking_cancelled',
            title=title,
            message=message,
            payload={
                'booking_id': booking.id,
                'cancelled_by': cancelled_by.full_name,
                'subject': booking.subject,
            },
            priority='normal',
            related_booking=booking
        )
    
    @staticmethod
    def send_session_reminder_notification(booking, minutes_before=30):
        """Send session reminder notification"""
        for user in [booking.mentor, booking.learner]:
            role = 'mentor' if user == booking.mentor else 'learner'
            other_user = booking.learner if user == booking.mentor else booking.mentor
            
            NotificationService.create_notification(
                user=user,
                notification_type='session_reminder',
                title=f'Session starting in {minutes_before} minutes',
                message=f'Your session "{booking.subject}" with {other_user.full_name} starts in {minutes_before} minutes',
                payload={
                    'booking_id': booking.id,
                    'other_user_name': other_user.full_name,
                    'subject': booking.subject,
                    'minutes_before': minutes_before,
                    'role': role
                },
                priority='urgent',
                action_url=f'/{role}/sessions/{booking.id}',
                action_text='Join Session',
                related_booking=booking,
                expires_at=booking.confirmed_start_utc or booking.requested_start_utc
            )
    
    @staticmethod
    def send_feedback_received_notification(booking, feedback_giver):
        """Send notification when feedback is received"""
        feedback_receiver = booking.mentor if feedback_giver == booking.learner else booking.learner
        
        NotificationService.create_notification(
            user=feedback_receiver,
            notification_type='feedback_received',
            title=f'New feedback from {feedback_giver.full_name}',
            message=f'You received feedback for the session "{booking.subject}"',
            payload={
                'booking_id': booking.id,
                'feedback_giver': feedback_giver.full_name,
                'subject': booking.subject,
            },
            priority='normal',
            action_url=f'/feedback/{booking.id}',
            action_text='View Feedback',
            related_booking=booking
        )
    
    @staticmethod
    def send_mentor_approval_notification(mentor, approved=True):
        """Send notification when mentor application is approved/rejected"""
        if approved:
            title = 'Mentor application approved!'
            message = 'Congratulations! Your mentor application has been approved. You can now start accepting bookings.'
            notification_type = 'mentor_approved'
            action_url = '/mentor/dashboard'
            action_text = 'Go to Dashboard'
        else:
            title = 'Mentor application update'
            message = 'Your mentor application requires review. Please check your email for details.'
            notification_type = 'mentor_rejected'
            action_url = '/apply-mentor'
            action_text = 'Reapply'
        
        NotificationService.create_notification(
            user=mentor,
            notification_type=notification_type,
            title=title,
            message=message,
            priority='high',
            action_url=action_url,
            action_text=action_text
        )
