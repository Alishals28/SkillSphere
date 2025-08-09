from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import secrets
import pyotp

from .models import TwoFactorAuth, TwoFactorSession, TwoFactorAuditLog
from .serializers import TwoFactorSetupSerializer, TwoFactorVerifySerializer


class TwoFactorSetupView(APIView):
    """
    Setup Two-Factor Authentication for user
    POST /api/auth/2fa/setup/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Get or create 2FA record
        two_fa, created = TwoFactorAuth.objects.get_or_create(user=user)
        
        if two_fa.is_enabled:
            return Response({
                'error': '2FA is already enabled for this account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate new secret key
        secret_key = two_fa.generate_secret_key()
        qr_code = two_fa.generate_qr_code()
        
        # Log setup attempt
        TwoFactorAuditLog.objects.create(
            user=user,
            action='setup',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'secret_key': secret_key,
            'qr_code': qr_code,
            'backup_tokens': [],  # Will be generated after verification
            'setup_uri': two_fa.get_totp_uri()
        })


class TwoFactorEnableView(APIView):
    """
    Enable 2FA after verifying setup token
    POST /api/auth/2fa/enable/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = TwoFactorVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        token = serializer.validated_data['token']
        
        try:
            two_fa = TwoFactorAuth.objects.get(user=user)
        except TwoFactorAuth.DoesNotExist:
            return Response({
                'error': '2FA setup not found. Please setup 2FA first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify the token
        if not two_fa.verify_token(token):
            TwoFactorAuditLog.objects.create(
                user=user,
                action='failed',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={'reason': 'Invalid token during setup'}
            )
            return Response({
                'error': 'Invalid verification code'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Enable 2FA and generate backup tokens
        two_fa.is_enabled = True
        two_fa.setup_completed_at = timezone.now()
        two_fa.save()
        
        backup_tokens = two_fa.generate_backup_tokens()
        
        # Log successful enablement
        TwoFactorAuditLog.objects.create(
            user=user,
            action='enabled',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        TwoFactorAuditLog.objects.create(
            user=user,
            action='backup_generated',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'count': len(backup_tokens)}
        )
        
        return Response({
            'message': '2FA has been enabled successfully',
            'backup_tokens': backup_tokens
        })


class TwoFactorDisableView(APIView):
    """
    Disable Two-Factor Authentication
    POST /api/auth/2fa/disable/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = TwoFactorVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        token = serializer.validated_data['token']
        
        try:
            two_fa = TwoFactorAuth.objects.get(user=user, is_enabled=True)
        except TwoFactorAuth.DoesNotExist:
            return Response({
                'error': '2FA is not enabled for this account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify current token or backup token
        is_valid = two_fa.verify_token(token) or two_fa.use_backup_token(token)
        
        if not is_valid:
            TwoFactorAuditLog.objects.create(
                user=user,
                action='failed',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={'reason': 'Invalid token during disable'}
            )
            return Response({
                'error': 'Invalid verification code'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Disable 2FA
        two_fa.disable_2fa()
        
        # Log disable action
        TwoFactorAuditLog.objects.create(
            user=user,
            action='disabled',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'message': '2FA has been disabled successfully'
        })


class TwoFactorStatusView(APIView):
    """
    Get 2FA status for current user
    GET /api/auth/2fa/status/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        try:
            two_fa = TwoFactorAuth.objects.get(user=user)
            return Response({
                'is_enabled': two_fa.is_enabled,
                'setup_completed_at': two_fa.setup_completed_at,
                'last_used_at': two_fa.last_used_at,
                'backup_tokens_count': len(two_fa.backup_tokens),
                'recovery_email': two_fa.recovery_email,
                'recovery_phone': two_fa.recovery_phone
            })
        except TwoFactorAuth.DoesNotExist:
            return Response({
                'is_enabled': False,
                'setup_completed_at': None,
                'last_used_at': None,
                'backup_tokens_count': 0,
                'recovery_email': '',
                'recovery_phone': ''
            })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def two_factor_login(request):
    """
    Enhanced login with 2FA support
    POST /api/auth/2fa/login/
    """
    email = request.data.get('email')
    password = request.data.get('password')
    token_2fa = request.data.get('token_2fa')
    session_token = request.data.get('session_token')
    
    if not email or not password:
        return Response({
            'error': 'Email and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Authenticate user
    user = authenticate(request, username=email, password=password)
    if not user:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check if user has 2FA enabled
    try:
        two_fa = TwoFactorAuth.objects.get(user=user, is_enabled=True)
    except TwoFactorAuth.DoesNotExist:
        # No 2FA enabled, proceed with normal login
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'requires_2fa': False
        })
    
    # 2FA is enabled, check if we have a session token
    if session_token:
        try:
            session = TwoFactorSession.objects.get(
                session_token=session_token,
                user=user,
                is_verified=True
            )
            if not session.is_expired():
                # Valid 2FA session, proceed with login
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)
                session.delete()  # Clean up session
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'requires_2fa': False
                })
        except TwoFactorSession.objects.DoesNotExist:
            pass
    
    # Need 2FA verification
    if not token_2fa:
        # Create temporary session
        session_token = secrets.token_urlsafe(32)
        TwoFactorSession.objects.create(
            user=user,
            session_token=session_token,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        return Response({
            'requires_2fa': True,
            'session_token': session_token,
            'message': 'Please provide 2FA verification code'
        }, status=status.HTTP_202_ACCEPTED)
    
    # Verify 2FA token
    if session_token:
        try:
            session = TwoFactorSession.objects.get(session_token=session_token, user=user)
            if not session.can_attempt():
                return Response({
                    'error': 'Too many attempts or session expired'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            session.record_attempt()
            
            # Check if it's a backup token or TOTP token
            is_valid = two_fa.verify_token(token_2fa)
            if not is_valid:
                is_valid = two_fa.use_backup_token(token_2fa)
                if is_valid:
                    TwoFactorAuditLog.objects.create(
                        user=user,
                        action='backup_used',
                        ip_address=request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
            
            if is_valid:
                session.verify()
                
                TwoFactorAuditLog.objects.create(
                    user=user,
                    action='verified',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)
                session.delete()  # Clean up session
                
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'requires_2fa': False
                })
            else:
                TwoFactorAuditLog.objects.create(
                    user=user,
                    action='failed',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    details={'reason': 'Invalid 2FA token during login'}
                )
                
                return Response({
                    'error': 'Invalid 2FA code',
                    'attempts_remaining': session.max_attempts - session.verification_attempts
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except TwoFactorSession.DoesNotExist:
            return Response({
                'error': 'Invalid session token'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'error': 'Session token required for 2FA verification'
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def regenerate_backup_tokens(request):
    """
    Regenerate backup tokens
    POST /api/auth/2fa/backup-tokens/regenerate/
    """
    user = request.user
    
    try:
        two_fa = TwoFactorAuth.objects.get(user=user, is_enabled=True)
    except TwoFactorAuth.DoesNotExist:
        return Response({
            'error': '2FA is not enabled for this account'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify current 2FA token for security
    token = request.data.get('token')
    if not token or not two_fa.verify_token(token):
        return Response({
            'error': 'Valid 2FA token required to regenerate backup tokens'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate new backup tokens
    backup_tokens = two_fa.generate_backup_tokens()
    
    # Log the action
    TwoFactorAuditLog.objects.create(
        user=user,
        action='backup_generated',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        details={'count': len(backup_tokens)}
    )
    
    return Response({
        'backup_tokens': backup_tokens,
        'message': 'New backup tokens generated. Store them securely.'
    })
