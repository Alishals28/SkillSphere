from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta
import uuid

from .models import User
from .serializers import (
    UserRegistrationSerializer, 
    UserProfileSerializer,
    PublicMentorProfileSerializer,
    DetailedMentorProfileSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailVerificationSerializer,
    ChangePasswordSerializer
)
from .permissions import IsOwnerOrReadOnly, IsAdmin, IsEmailVerified


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Send verification email
        self.send_verification_email(user)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Registration successful. Please check your email to verify your account.'
        }, status=status.HTTP_201_CREATED)

    def send_verification_email(self, user):
        """Send email verification"""
        verification_url = f"{settings.EMAIL_VERIFICATION_URL}?token={user.email_verification_token}"
        
        subject = 'Verify your SkillSphere account'
        message = f"""
        Hi {user.first_name},
        
        Welcome to SkillSphere! Please verify your email address by clicking the link below:
        
        {verification_url}
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        The SkillSphere Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom login view that returns user data along with tokens
    POST /api/auth/login/
    """
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get user data
            user = authenticate(
                username=request.data.get('email'),
                password=request.data.get('password')
            )
            if user:
                user.update_last_active()
                response.data['user'] = UserProfileSerializer(user).data
        
        return response


class LogoutView(APIView):
    """
    Logout view that blacklists the refresh token
    POST /api/auth/logout/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile
    GET/PUT/PATCH /api/users/me/
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # If changing to mentor role, require approval
        if serializer.validated_data.get('role') == 'mentor' and instance.role != 'mentor':
            instance.role = 'mentor'
            instance.is_mentor_approved = False
            instance.save()
            serializer = self.get_serializer(instance)
            
            return Response({
                **serializer.data,
                'message': 'Role change to mentor submitted for approval.'
            })
        
        self.perform_update(serializer)
        return Response(serializer.data)


class EmailVerificationView(APIView):
    """
    Email verification endpoint
    POST /api/auth/verify-email/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        user = get_object_or_404(User, email_verification_token=token, is_email_verified=False)
        
        user.is_email_verified = True
        user.save()
        
        return Response({
            'message': 'Email verified successfully!'
        }, status=status.HTTP_200_OK)


class ResendVerificationEmailView(APIView):
    """
    Resend verification email
    POST /api/auth/resend-verification/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        
        if user.is_email_verified:
            return Response({
                'message': 'Email is already verified.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate new token
        user.email_verification_token = uuid.uuid4()
        user.save()
        
        # Send email (reuse method from registration)
        registration_view = UserRegistrationView()
        registration_view.send_verification_email(user)
        
        return Response({
            'message': 'Verification email sent successfully!'
        }, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """
    Password reset request
    POST /api/auth/password-reset/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Generate reset token
        user.password_reset_token = uuid.uuid4()
        user.password_reset_expires = timezone.now() + timedelta(hours=24)
        user.save()
        
        # Send reset email
        reset_url = f"{settings.PASSWORD_RESET_URL}?token={user.password_reset_token}"
        
        subject = 'Reset your SkillSphere password'
        message = f"""
        Hi {user.first_name},
        
        You requested a password reset for your SkillSphere account. Click the link below to reset your password:
        
        {reset_url}
        
        This link will expire in 24 hours. If you didn't request this reset, please ignore this email.
        
        Best regards,
        The SkillSphere Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return Response({
            'message': 'Password reset email sent successfully!'
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    Password reset confirmation
    POST /api/auth/password-reset-confirm/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        new_password = serializer.validated_data['password']
        
        # Reset password
        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.save()
        
        return Response({
            'message': 'Password reset successfully!'
        }, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """
    Change password for authenticated users
    POST /api/auth/change-password/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Password changed successfully!'
        }, status=status.HTTP_200_OK)


class MentorListView(generics.ListAPIView):
    """
    Enhanced mentor listing with advanced search and filtering
    GET /api/mentors/
    """
    serializer_class = PublicMentorProfileSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['country', 'is_available']
    search_fields = ['first_name', 'last_name', 'mentor_bio', 'bio']
    ordering_fields = ['hourly_rate', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
        from django.db.models import Q, Avg, Count, Exists, OuterRef
        from skills.models import MentorSkill
        from availability.models import AvailabilitySlot
        from django.utils import timezone
        
        queryset = User.objects.filter(
            role='mentor',
            is_mentor_approved=True,
            is_email_verified=True
        ).select_related().prefetch_related(
            'mentor_skills__skill',
            'mentor_tags',
            'mentor_bookings'
        )
        
        # Get search parameters
        search_query = self.request.query_params.get('search', None)
        skills_param = self.request.query_params.get('skills', None)
        min_rating = self.request.query_params.get('min_rating', None)
        max_rating = self.request.query_params.get('max_rating', None)
        min_rate = self.request.query_params.get('min_rate', None)
        max_rate = self.request.query_params.get('max_rate', None)
        timezone_param = self.request.query_params.get('timezone', None)
        available_now = self.request.query_params.get('available_now', None)
        available_today = self.request.query_params.get('available_today', None)
        available_this_week = self.request.query_params.get('available_this_week', None)
        has_availability = self.request.query_params.get('has_availability', None)
        sort_by = self.request.query_params.get('sort_by', '-created_at')
        
        # Full-text search
        if search_query:
            search_vector = SearchVector('first_name', weight='A') + \
                          SearchVector('last_name', weight='A') + \
                          SearchVector('mentor_bio', weight='B') + \
                          SearchVector('bio', weight='C') + \
                          SearchVector('teaching_experience', weight='C')
            
            search_query_obj = SearchQuery(search_query)
            queryset = queryset.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query_obj)
            ).filter(search=search_query_obj).order_by('-rank', '-created_at')
        
        # Skills filter
        if skills_param:
            skill_names = [s.strip() for s in skills_param.split(',')]
            # Try to match by name or ID
            skill_ids = []
            for skill in skill_names:
                if skill.isdigit():
                    skill_ids.append(int(skill))
                else:
                    # Search by name (case-insensitive)
                    from skills.models import Skill
                    skill_obj = Skill.objects.filter(
                        Q(name__icontains=skill) | Q(slug__iexact=skill)
                    ).first()
                    if skill_obj:
                        skill_ids.append(skill_obj.id)
            
            if skill_ids:
                queryset = queryset.filter(
                    mentor_skills__skill__id__in=skill_ids
                ).distinct()
        
        # Rating filter
        if min_rating or max_rating:
            avg_rating_subquery = User.objects.filter(
                mentor_bookings__status='completed',
                mentor_bookings__learner_rating__isnull=False,
                pk=OuterRef('pk')
            ).aggregate(avg_rating=Avg('mentor_bookings__learner_rating'))['avg_rating']
            
            queryset = queryset.annotate(avg_rating=avg_rating_subquery)
            
            if min_rating:
                queryset = queryset.filter(avg_rating__gte=float(min_rating))
            if max_rating:
                queryset = queryset.filter(avg_rating__lte=float(max_rating))
        
        # Rate filter
        if min_rate:
            queryset = queryset.filter(hourly_rate__gte=float(min_rate))
        if max_rate:
            queryset = queryset.filter(hourly_rate__lte=float(max_rate))
        
        # Timezone filter
        if timezone_param:
            queryset = queryset.filter(timezone=timezone_param)
        
        # Availability filters
        now = timezone.now()
        if available_now == 'true':
            # Has slots available in the next 2 hours
            queryset = queryset.filter(
                Exists(AvailabilitySlot.objects.filter(
                    mentor=OuterRef('pk'),
                    start_utc__gte=now,
                    start_utc__lte=now + timezone.timedelta(hours=2),
                    is_booked=False,
                    is_blocked=False
                ))
            )
        
        if available_today == 'true':
            # Has slots available today
            end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            queryset = queryset.filter(
                Exists(AvailabilitySlot.objects.filter(
                    mentor=OuterRef('pk'),
                    start_utc__gte=now,
                    start_utc__lte=end_of_day,
                    is_booked=False,
                    is_blocked=False
                ))
            )
        
        if available_this_week == 'true':
            # Has slots available this week
            end_of_week = now + timezone.timedelta(days=7)
            queryset = queryset.filter(
                Exists(AvailabilitySlot.objects.filter(
                    mentor=OuterRef('pk'),
                    start_utc__gte=now,
                    start_utc__lte=end_of_week,
                    is_booked=False,
                    is_blocked=False
                ))
            )
        
        if has_availability == 'true':
            # Has any future availability
            queryset = queryset.filter(
                Exists(AvailabilitySlot.objects.filter(
                    mentor=OuterRef('pk'),
                    start_utc__gt=now,
                    is_booked=False,
                    is_blocked=False
                ))
            )
        
        # Sorting
        if sort_by == 'rating':
            queryset = queryset.annotate(
                avg_rating=Avg('mentor_bookings__learner_rating')
            ).order_by('avg_rating', 'created_at')
        elif sort_by == '-rating':
            queryset = queryset.annotate(
                avg_rating=Avg('mentor_bookings__learner_rating')
            ).order_by('-avg_rating', '-created_at')
        elif sort_by == 'total_sessions':
            queryset = queryset.annotate(
                session_count=Count('mentor_bookings', filter=Q(mentor_bookings__status='completed'))
            ).order_by('session_count', 'created_at')
        elif sort_by == '-total_sessions':
            queryset = queryset.annotate(
                session_count=Count('mentor_bookings', filter=Q(mentor_bookings__status='completed'))
            ).order_by('-session_count', '-created_at')
        elif sort_by == 'availability':
            queryset = queryset.annotate(
                availability_count=Count('availability_slots', filter=Q(
                    availability_slots__start_utc__gt=now,
                    availability_slots__is_booked=False,
                    availability_slots__is_blocked=False
                ))
            ).order_by('-availability_count', '-created_at')
        elif sort_by == 'relevance' and search_query:
            # Already sorted by rank above
            pass
        else:
            # Default sorting
            queryset = queryset.order_by(sort_by)
        
        return queryset


class MentorDetailView(generics.RetrieveAPIView):
    """
    Get detailed mentor profile
    GET /api/mentors/{id}/
    """
    serializer_class = DetailedMentorProfileSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return User.objects.filter(
            role='mentor',
            is_mentor_approved=True,
            is_email_verified=True
        ).select_related().prefetch_related(
            'mentor_skills__skill__category',
            'mentor_tags',
            'mentor_bookings__learner',
            'availability_slots'
        )


# Admin views for mentor approval
class PendingMentorsView(generics.ListAPIView):
    """
    List pending mentor applications (Admin only)
    GET /api/admin/mentors/pending/
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdmin]
    
    def get_queryset(self):
        return User.objects.filter(
            role='mentor',
            is_mentor_approved=False,
            is_email_verified=True
        ).order_by('created_at')


class ApproveMentorView(APIView):
    """
    Approve or reject mentor application (Admin only)
    POST /api/admin/mentors/{id}/approve/
    """
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        mentor = get_object_or_404(User, pk=pk, role='mentor')
        action = request.data.get('action')  # 'approve' or 'reject'
        
        if action == 'approve':
            mentor.is_mentor_approved = True
            mentor.save()
            
            # Send approval email
            subject = 'Your SkillSphere mentor application has been approved!'
            message = f"""
            Hi {mentor.first_name},
            
            Congratulations! Your mentor application has been approved. You can now start accepting session bookings from learners.
            
            Login to your dashboard to set up your availability and start mentoring!
            
            Best regards,
            The SkillSphere Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [mentor.email],
                fail_silently=False,
            )
            
            return Response({
                'message': f'Mentor {mentor.full_name} approved successfully!'
            }, status=status.HTTP_200_OK)
        
        elif action == 'reject':
            reason = request.data.get('reason', 'Application did not meet requirements.')
            
            # Send rejection email
            subject = 'Your SkillSphere mentor application'
            message = f"""
            Hi {mentor.first_name},
            
            Thank you for your interest in becoming a mentor on SkillSphere. Unfortunately, we cannot approve your application at this time.
            
            Reason: {reason}
            
            You may reapply after addressing the feedback above.
            
            Best regards,
            The SkillSphere Team
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [mentor.email],
                fail_silently=False,
            )
            
            # Reset to learner role
            mentor.role = 'learner'
            mentor.is_mentor_approved = False
            mentor.save()
            
            return Response({
                'message': f'Mentor application for {mentor.full_name} rejected.'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Invalid action. Use "approve" or "reject".'
        }, status=status.HTTP_400_BAD_REQUEST)
