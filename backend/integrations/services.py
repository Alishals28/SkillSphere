from abc import ABC, abstractmethod
import requests
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import logging
from .models import UserIntegration, IntegrationLog

logger = logging.getLogger(__name__)


class BaseIntegrationService(ABC):
    """Base class for all integration services"""
    
    def __init__(self, user_integration: UserIntegration):
        self.user_integration = user_integration
        self.provider = user_integration.provider
        self.user = user_integration.user
    
    def log_action(self, level, action_type, message, **kwargs):
        """Log integration action"""
        IntegrationLog.objects.create(
            user_integration=self.user_integration,
            level=level,
            action_type=action_type,
            message=message,
            **kwargs
        )
    
    def is_authenticated(self):
        """Check if integration is properly authenticated"""
        return (
            self.user_integration.status == 'active' and
            not self.user_integration.is_token_expired()
        )
    
    @abstractmethod
    def test_connection(self):
        """Test the integration connection"""
        pass
    
    @abstractmethod
    def refresh_token(self):
        """Refresh the access token if needed"""
        pass


class GoogleCalendarService(BaseIntegrationService):
    """Google Calendar integration service"""
    
    def __init__(self, user_integration: UserIntegration):
        super().__init__(user_integration)
        self.api_base = "https://www.googleapis.com/calendar/v3"
    
    def test_connection(self):
        """Test Google Calendar API connection"""
        try:
            response = requests.get(
                f"{self.api_base}/users/me/calendarList",
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_action('info', 'api_call', 'Calendar connection test successful')
                return True
            else:
                self.log_action('error', 'api_call', f'Calendar connection test failed: {response.status_code}')
                return False
                
        except Exception as e:
            self.log_action('error', 'api_call', f'Calendar connection test error: {str(e)}')
            return False
    
    def refresh_token(self):
        """Refresh Google OAuth token"""
        if not self.user_integration.refresh_token:
            return False
        
        try:
            token_data = {
                'client_id': self.provider.client_id,
                'client_secret': self.provider.client_secret,
                'refresh_token': self.user_integration.refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(
                'https://oauth2.googleapis.com/token',
                data=token_data,
                timeout=10
            )
            
            if response.status_code == 200:
                token_info = response.json()
                self.user_integration.access_token = token_info['access_token']
                self.user_integration.token_expires_at = timezone.now() + timedelta(
                    seconds=token_info.get('expires_in', 3600)
                )
                self.user_integration.save()
                
                self.log_action('info', 'auth', 'Token refreshed successfully')
                return True
            else:
                self.log_action('error', 'auth', f'Token refresh failed: {response.status_code}')
                return False
                
        except Exception as e:
            self.log_action('error', 'auth', f'Token refresh error: {str(e)}')
            return False
    
    def create_event(self, booking):
        """Create calendar event for booking"""
        if not self.is_authenticated():
            if not self.refresh_token():
                return None
        
        try:
            calendar_settings = getattr(self.user_integration, 'calendar_settings', None)
            if not calendar_settings:
                return None
            
            # Determine participant name
            if self.user.role == 'mentor':
                participant = booking.learner.full_name
            else:
                participant = booking.mentor.full_name
            
            # Create event data
            event_data = {
                'summary': calendar_settings.event_title_template.format(
                    participant=participant,
                    subject=booking.subject,
                    duration=booking.duration_minutes
                ),
                'description': calendar_settings.event_description_template.format(
                    subject=booking.subject,
                    duration=booking.duration_minutes,
                    mentor=booking.mentor.full_name,
                    learner=booking.learner.full_name
                ),
                'start': {
                    'dateTime': booking.requested_start_utc.isoformat(),
                    'timeZone': 'UTC'
                },
                'end': {
                    'dateTime': (booking.requested_start_utc + timedelta(
                        minutes=booking.duration_minutes
                    )).isoformat(),
                    'timeZone': 'UTC'
                }
            }
            
            # Add reminders if configured
            if calendar_settings.add_reminders and calendar_settings.reminder_minutes:
                event_data['reminders'] = {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': minutes}
                        for minutes in calendar_settings.reminder_minutes
                    ]
                }
            
            # Create the event
            calendar_id = calendar_settings.default_calendar_id or 'primary'
            response = requests.post(
                f"{self.api_base}/calendars/{calendar_id}/events",
                headers=self._get_headers(),
                json=event_data,
                timeout=10
            )
            
            if response.status_code == 200:
                event = response.json()
                self.log_action(
                    'info', 'create', 
                    f'Calendar event created for booking {booking.id}',
                    booking_id=booking.id,
                    external_id=event['id']
                )
                return event
            else:
                self.log_action(
                    'error', 'create',
                    f'Failed to create calendar event: {response.status_code}',
                    booking_id=booking.id,
                    response_data=response.json() if response.content else None
                )
                return None
                
        except Exception as e:
            self.log_action(
                'error', 'create',
                f'Error creating calendar event: {str(e)}',
                booking_id=booking.id
            )
            return None
    
    def update_event(self, event_id, booking):
        """Update existing calendar event"""
        # Similar implementation to create_event but using PUT request
        pass
    
    def delete_event(self, event_id):
        """Delete calendar event"""
        if not self.is_authenticated():
            if not self.refresh_token():
                return False
        
        try:
            calendar_settings = getattr(self.user_integration, 'calendar_settings', None)
            if not calendar_settings:
                return False
            
            calendar_id = calendar_settings.default_calendar_id or 'primary'
            response = requests.delete(
                f"{self.api_base}/calendars/{calendar_id}/events/{event_id}",
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                self.log_action('info', 'delete', f'Calendar event {event_id} deleted')
                return True
            else:
                self.log_action('error', 'delete', f'Failed to delete event: {response.status_code}')
                return False
                
        except Exception as e:
            self.log_action('error', 'delete', f'Error deleting event: {str(e)}')
            return False
    
    def _get_headers(self):
        """Get API request headers"""
        return {
            'Authorization': f'Bearer {self.user_integration.access_token}',
            'Content-Type': 'application/json'
        }


class ZoomService(BaseIntegrationService):
    """Zoom integration service"""
    
    def __init__(self, user_integration: UserIntegration):
        super().__init__(user_integration)
        self.api_base = "https://api.zoom.us/v2"
    
    def test_connection(self):
        """Test Zoom API connection"""
        try:
            response = requests.get(
                f"{self.api_base}/users/me",
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_action('info', 'api_call', 'Zoom connection test successful')
                return True
            else:
                self.log_action('error', 'api_call', f'Zoom connection test failed: {response.status_code}')
                return False
                
        except Exception as e:
            self.log_action('error', 'api_call', f'Zoom connection test error: {str(e)}')
            return False
    
    def refresh_token(self):
        """Refresh Zoom OAuth token"""
        # Similar implementation to Google Calendar
        pass
    
    def create_meeting(self, booking):
        """Create Zoom meeting for booking"""
        if not self.is_authenticated():
            if not self.refresh_token():
                return None
        
        try:
            video_settings = getattr(self.user_integration, 'video_settings', None)
            if not video_settings:
                return None
            
            meeting_data = {
                'topic': f"Mentoring Session: {booking.subject}",
                'type': 2,  # Scheduled meeting
                'start_time': booking.requested_start_utc.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'duration': booking.duration_minutes,
                'timezone': 'UTC',
                'settings': {
                    'waiting_room': video_settings.enable_waiting_room,
                    'auto_recording': 'cloud' if video_settings.auto_record else 'none',
                    'mute_upon_entry': video_settings.mute_participants_on_entry,
                    'join_before_host': video_settings.allow_join_before_host,
                }
            }
            
            response = requests.post(
                f"{self.api_base}/users/me/meetings",
                headers=self._get_headers(),
                json=meeting_data,
                timeout=10
            )
            
            if response.status_code == 201:
                meeting = response.json()
                self.log_action(
                    'info', 'create',
                    f'Zoom meeting created for booking {booking.id}',
                    booking_id=booking.id,
                    external_id=meeting['id']
                )
                return meeting
            else:
                self.log_action(
                    'error', 'create',
                    f'Failed to create Zoom meeting: {response.status_code}',
                    booking_id=booking.id
                )
                return None
                
        except Exception as e:
            self.log_action(
                'error', 'create',
                f'Error creating Zoom meeting: {str(e)}',
                booking_id=booking.id
            )
            return None
    
    def _get_headers(self):
        """Get API request headers"""
        return {
            'Authorization': f'Bearer {self.user_integration.access_token}',
            'Content-Type': 'application/json'
        }


class StripeService(BaseIntegrationService):
    """Stripe payment integration service"""
    
    def __init__(self, user_integration: UserIntegration):
        super().__init__(user_integration)
        self.api_base = "https://api.stripe.com/v1"
    
    def test_connection(self):
        """Test Stripe API connection"""
        try:
            response = requests.get(
                f"{self.api_base}/account",
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_action('info', 'api_call', 'Stripe connection test successful')
                return True
            else:
                self.log_action('error', 'api_call', f'Stripe connection test failed: {response.status_code}')
                return False
                
        except Exception as e:
            self.log_action('error', 'api_call', f'Stripe connection test error: {str(e)}')
            return False
    
    def refresh_token(self):
        """Stripe uses API keys, no token refresh needed"""
        return True
    
    def create_payment_intent(self, booking):
        """Create Stripe payment intent for booking"""
        try:
            payment_data = {
                'amount': int(booking.total_amount * 100),  # Convert to cents
                'currency': 'usd',
                'metadata': {
                    'booking_id': str(booking.id),
                    'mentor_id': str(booking.mentor.id),
                    'learner_id': str(booking.learner.id)
                }
            }
            
            response = requests.post(
                f"{self.api_base}/payment_intents",
                headers=self._get_headers(),
                data=payment_data,
                timeout=10
            )
            
            if response.status_code == 200:
                payment_intent = response.json()
                self.log_action(
                    'info', 'create',
                    f'Payment intent created for booking {booking.id}',
                    booking_id=booking.id,
                    external_id=payment_intent['id']
                )
                return payment_intent
            else:
                self.log_action(
                    'error', 'create',
                    f'Failed to create payment intent: {response.status_code}',
                    booking_id=booking.id
                )
                return None
                
        except Exception as e:
            self.log_action(
                'error', 'create',
                f'Error creating payment intent: {str(e)}',
                booking_id=booking.id
            )
            return None
    
    def _get_headers(self):
        """Get API request headers"""
        return {
            'Authorization': f'Bearer {self.user_integration.api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }


class IntegrationServiceFactory:
    """Factory for creating integration services"""
    
    SERVICE_MAP = {
        'google_calendar': GoogleCalendarService,
        'outlook_calendar': GoogleCalendarService,  # Can be extended for Outlook
        'zoom': ZoomService,
        'teams': ZoomService,  # Can be extended for Teams
        'stripe': StripeService,
        'paypal': StripeService,  # Can be extended for PayPal
    }
    
    @classmethod
    def create_service(cls, user_integration: UserIntegration):
        """Create appropriate service for integration"""
        service_class = cls.SERVICE_MAP.get(user_integration.provider.name)
        if service_class:
            return service_class(user_integration)
        else:
            raise ValueError(f"No service available for provider: {user_integration.provider.name}")
    
    @classmethod
    def get_available_services(cls):
        """Get list of available service types"""
        return list(cls.SERVICE_MAP.keys())
