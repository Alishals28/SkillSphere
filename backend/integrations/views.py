from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import secrets
import requests
from urllib.parse import urlencode

from .models import (
    IntegrationProvider, UserIntegration, CalendarIntegration,
    PaymentIntegration, VideoConferencingIntegration, IntegrationLog,
    WebhookEndpoint, WebhookEvent
)
from .serializers import (
    IntegrationProviderSerializer, UserIntegrationSerializer,
    CalendarIntegrationSerializer, PaymentIntegrationSerializer,
    VideoConferencingIntegrationSerializer, IntegrationLogSerializer
)
from .services import IntegrationServiceFactory


class IntegrationProviderListView(generics.ListAPIView):
    """
    List available integration providers
    GET /api/integrations/providers/
    """
    queryset = IntegrationProvider.objects.filter(is_active=True)
    serializer_class = IntegrationProviderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        provider_type = self.request.GET.get('type')
        if provider_type:
            queryset = queryset.filter(provider_type=provider_type)
        return queryset


class UserIntegrationListView(generics.ListCreateAPIView):
    """
    List user's integrations or create new integration
    GET/POST /api/integrations/
    """
    serializer_class = UserIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserIntegration.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserIntegrationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete user integration
    GET/PUT/DELETE /api/integrations/<id>/
    """
    serializer_class = UserIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserIntegration.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def initiate_oauth(request):
    """
    Initiate OAuth flow for integration
    POST /api/integrations/oauth/initiate/
    """
    provider_id = request.data.get('provider_id')
    redirect_uri = request.data.get('redirect_uri')
    
    if not provider_id:
        return Response(
            {'error': 'provider_id is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        provider = IntegrationProvider.objects.get(id=provider_id, is_active=True)
    except IntegrationProvider.DoesNotExist:
        return Response(
            {'error': 'Provider not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if provider.auth_type != 'oauth2':
        return Response(
            {'error': 'Provider does not support OAuth'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generate state parameter for security
    state = secrets.token_urlsafe(32)
    request.session[f'oauth_state_{provider.id}'] = state
    request.session[f'oauth_user_{provider.id}'] = request.user.id
    
    # Build authorization URL
    auth_params = {
        'client_id': provider.client_id,
        'redirect_uri': redirect_uri or request.build_absolute_uri(
            reverse('integrations:oauth-callback', kwargs={'provider_id': provider.id})
        ),
        'response_type': 'code',
        'scope': provider.scope,
        'state': state,
        'access_type': 'offline',  # For refresh tokens
        'prompt': 'consent'
    }
    
    authorization_url = f"{provider.authorization_url}?{urlencode(auth_params)}"
    
    return Response({
        'authorization_url': authorization_url,
        'state': state
    })


@api_view(['GET'])
def oauth_callback(request, provider_id):
    """
    Handle OAuth callback
    GET /api/integrations/oauth/callback/<provider_id>/
    """
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    
    if error:
        return Response(
            {'error': f'OAuth error: {error}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not code or not state:
        return Response(
            {'error': 'Missing authorization code or state'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        provider = IntegrationProvider.objects.get(id=provider_id, is_active=True)
    except IntegrationProvider.DoesNotExist:
        return Response(
            {'error': 'Provider not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Verify state parameter
    session_state = request.session.get(f'oauth_state_{provider.id}')
    if not session_state or session_state != state:
        return Response(
            {'error': 'Invalid state parameter'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get user from session
    user_id = request.session.get(f'oauth_user_{provider.id}')
    if not user_id:
        return Response(
            {'error': 'Invalid session'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Exchange code for tokens
    token_data = {
        'client_id': provider.client_id,
        'client_secret': provider.client_secret,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': request.build_absolute_uri(
            reverse('integrations:oauth-callback', kwargs={'provider_id': provider.id})
        )
    }
    
    try:
        response = requests.post(provider.token_url, data=token_data, timeout=10)
        
        if response.status_code == 200:
            token_info = response.json()
            
            # Create or update user integration
            user_integration, created = UserIntegration.objects.get_or_create(
                user_id=user_id,
                provider=provider,
                defaults={
                    'access_token': token_info.get('access_token', ''),
                    'refresh_token': token_info.get('refresh_token', ''),
                    'token_expires_at': timezone.now() + timedelta(
                        seconds=token_info.get('expires_in', 3600)
                    ) if token_info.get('expires_in') else None,
                    'status': 'active',
                    'permissions': token_info.get('scope', '').split(' ') if token_info.get('scope') else []
                }
            )
            
            if not created:
                # Update existing integration
                user_integration.access_token = token_info.get('access_token', '')
                user_integration.refresh_token = token_info.get('refresh_token', '') or user_integration.refresh_token
                user_integration.token_expires_at = timezone.now() + timedelta(
                    seconds=token_info.get('expires_in', 3600)
                ) if token_info.get('expires_in') else None
                user_integration.status = 'active'
                user_integration.save()
            
            # Clean up session
            request.session.pop(f'oauth_state_{provider.id}', None)
            request.session.pop(f'oauth_user_{provider.id}', None)
            
            return Response({
                'success': True,
                'integration_id': user_integration.id,
                'message': 'Integration connected successfully'
            })
        else:
            return Response(
                {'error': 'Failed to exchange authorization code'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return Response(
            {'error': f'OAuth callback error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_integration(request, integration_id):
    """
    Test integration connection
    POST /api/integrations/<id>/test/
    """
    try:
        integration = UserIntegration.objects.get(
            id=integration_id, 
            user=request.user
        )
    except UserIntegration.DoesNotExist:
        return Response(
            {'error': 'Integration not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        service = IntegrationServiceFactory.create_service(integration)
        connection_ok = service.test_connection()
        
        if connection_ok:
            integration.status = 'active'
            integration.last_sync = timezone.now()
            integration.save()
            
            return Response({
                'success': True,
                'message': 'Integration test successful'
            })
        else:
            return Response({
                'success': False,
                'message': 'Integration test failed'
            })
            
    except Exception as e:
        return Response(
            {'error': f'Test failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def sync_integration(request, integration_id):
    """
    Manually sync integration
    POST /api/integrations/<id>/sync/
    """
    try:
        integration = UserIntegration.objects.get(
            id=integration_id, 
            user=request.user
        )
    except UserIntegration.DoesNotExist:
        return Response(
            {'error': 'Integration not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not integration.sync_enabled:
        return Response(
            {'error': 'Sync is disabled for this integration'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        service = IntegrationServiceFactory.create_service(integration)
        
        # Perform sync based on provider type
        if integration.provider.provider_type == 'calendar':
            # Sync upcoming bookings to calendar
            from bookings.models import Booking
            upcoming_bookings = Booking.objects.filter(
                mentor=request.user if request.user.role == 'mentor' else None,
                learner=request.user if request.user.role == 'learner' else None,
                status='confirmed',
                requested_start_utc__gte=timezone.now()
            )[:10]  # Limit to next 10 bookings
            
            synced_count = 0
            for booking in upcoming_bookings:
                event = service.create_event(booking)
                if event:
                    synced_count += 1
            
            integration.last_sync = timezone.now()
            integration.save()
            
            return Response({
                'success': True,
                'message': f'Synced {synced_count} upcoming sessions to calendar'
            })
        else:
            return Response({
                'success': True,
                'message': 'Sync completed'
            })
            
    except Exception as e:
        return Response(
            {'error': f'Sync failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class CalendarIntegrationView(generics.RetrieveUpdateAPIView):
    """
    Calendar integration settings
    GET/PUT /api/integrations/<id>/calendar/
    """
    serializer_class = CalendarIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        integration = get_object_or_404(
            UserIntegration,
            id=self.kwargs['integration_id'],
            user=self.request.user,
            provider__provider_type='calendar'
        )
        
        calendar_settings, created = CalendarIntegration.objects.get_or_create(
            user_integration=integration
        )
        return calendar_settings


class PaymentIntegrationView(generics.RetrieveUpdateAPIView):
    """
    Payment integration settings
    GET/PUT /api/integrations/<id>/payment/
    """
    serializer_class = PaymentIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        integration = get_object_or_404(
            UserIntegration,
            id=self.kwargs['integration_id'],
            user=self.request.user,
            provider__provider_type='payment'
        )
        
        payment_settings, created = PaymentIntegration.objects.get_or_create(
            user_integration=integration
        )
        return payment_settings


class VideoIntegrationView(generics.RetrieveUpdateAPIView):
    """
    Video conferencing integration settings
    GET/PUT /api/integrations/<id>/video/
    """
    serializer_class = VideoConferencingIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        integration = get_object_or_404(
            UserIntegration,
            id=self.kwargs['integration_id'],
            user=self.request.user,
            provider__provider_type='video'
        )
        
        video_settings, created = VideoConferencingIntegration.objects.get_or_create(
            user_integration=integration
        )
        return video_settings


class IntegrationLogView(generics.ListAPIView):
    """
    Integration logs
    GET /api/integrations/<id>/logs/
    """
    serializer_class = IntegrationLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        integration = get_object_or_404(
            UserIntegration,
            id=self.kwargs['integration_id'],
            user=self.request.user
        )
        return IntegrationLog.objects.filter(
            user_integration=integration
        ).order_by('-created_at')


@api_view(['POST'])
def webhook_handler(request, provider_name, endpoint_path):
    """
    Generic webhook handler
    POST /api/integrations/webhook/<provider_name>/<endpoint_path>/
    """
    try:
        # Find webhook endpoint
        webhook_endpoint = WebhookEndpoint.objects.get(
            provider__name=provider_name,
            url_path=endpoint_path,
            is_active=True
        )
    except WebhookEndpoint.DoesNotExist:
        return Response(
            {'error': 'Webhook endpoint not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Create webhook event record
    webhook_event = WebhookEvent.objects.create(
        endpoint=webhook_endpoint,
        event_type=request.headers.get('X-Event-Type', 'unknown'),
        event_id=request.headers.get('X-Event-Id', ''),
        payload=request.data,
        headers=dict(request.headers),
        source_ip=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Update endpoint statistics
    webhook_endpoint.total_received += 1
    webhook_endpoint.last_received = timezone.now()
    webhook_endpoint.save()
    
    # Process webhook asynchronously (in a real app, you'd use Celery)
    # process_webhook_event.delay(webhook_event.id)
    
    return Response({'success': True, 'event_id': webhook_event.id})
