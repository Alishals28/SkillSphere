from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404

from .models import (
    Booking, RecurringBookingTemplate, GroupBooking, GroupBookingParticipant,
    BookingPackage, BookingPackagePurchase, BookingTemplate
)
from .serializers import (
    BookingSerializer,
    BookingCreateSerializer,
    BookingUpdateSerializer,
    BookingStatusUpdateSerializer,
    BookingListSerializer,
    BookingStatisticsSerializer,
    RecurringBookingTemplateSerializer,
    GroupBookingSerializer,
    GroupBookingParticipantSerializer,
    BookingPackageSerializer,
    BookingPackagePurchaseSerializer,
    BookingTemplateSerializer,
    AdvancedBookingSerializer
)
from users.permissions import IsMentor, IsMentorOrAdmin
from users.models import User
from availability.models import AvailabilitySlot
from notifications.services import NotificationService


class BookingListView(generics.ListAPIView):
    """
    List bookings for the authenticated user
    GET /api/bookings/
    """
    serializer_class = BookingListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Booking.objects.all()
        
        # Filter based on user role
        if user.role == 'mentor':
            queryset = queryset.filter(mentor=user)
        else:
            queryset = queryset.filter(learner=user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(start_utc__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_utc__lte=end_date)
        
        # Filter by skill
        skill_id = self.request.query_params.get('skill')
        if skill_id:
            queryset = queryset.filter(skill_id=skill_id)
        
        return queryset.order_by('-created_at')


class BookingCreateView(generics.CreateAPIView):
    """
    Create a new booking
    POST /api/bookings/
    """
    serializer_class = BookingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Ensure learners can't book their own sessions
        if request.user.role == 'mentor':
            return Response(
                {'error': 'Mentors cannot create bookings'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save(learner=request.user)
            
            # Mark the availability slot as booked
            if booking.availability_slot:
                booking.availability_slot.is_booked = True
                booking.availability_slot.save()
            
            # Send notification to mentor
            NotificationService.send_booking_request_notification(booking)
            
            response_serializer = BookingSerializer(booking)
            return Response(
                response_serializer.data, 
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingDetailView(generics.RetrieveUpdateAPIView):
    """
    Get or update a specific booking
    GET/PUT/PATCH /api/bookings/{id}/
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Booking.objects.all()
        
        # Users can only access their own bookings
        if user.role == 'mentor':
            queryset = queryset.filter(mentor=user)
        else:
            queryset = queryset.filter(learner=user)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BookingUpdateSerializer
        return BookingSerializer


@api_view(['POST'])
@permission_classes([IsMentor])
def accept_booking(request, booking_id):
    """
    Accept a booking request
    POST /api/bookings/{booking_id}/accept/
    """
    booking = get_object_or_404(
        Booking, 
        id=booking_id, 
        mentor=request.user,
        status='pending'
    )
    
    booking.status = 'confirmed'
    booking.confirmed_at = timezone.now()
    booking.save()
    
    # Send notification to learner
    NotificationService.send_booking_confirmed_notification(booking)
    
    serializer = BookingSerializer(booking)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsMentor])
def decline_booking(request, booking_id):
    """
    Decline a booking request
    POST /api/bookings/{booking_id}/decline/
    """
    booking = get_object_or_404(
        Booking, 
        id=booking_id, 
        mentor=request.user,
        status='pending'
    )
    
    decline_reason = request.data.get('decline_reason', '')
    
    booking.status = 'declined'
    booking.decline_reason = decline_reason
    booking.save()
    
    # Free up the availability slot
    if booking.availability_slot:
        booking.availability_slot.is_booked = False
        booking.availability_slot.save()
    
    # TODO: Send notification to learner
    
    serializer = BookingSerializer(booking)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_booking(request, booking_id):
    """
    Cancel a booking
    POST /api/bookings/{booking_id}/cancel/
    """
    user = request.user
    
    # Get booking based on user role
    if user.role == 'mentor':
        booking = get_object_or_404(
            Booking, 
            id=booking_id, 
            mentor=user,
            status__in=['pending', 'confirmed']
        )
    else:
        booking = get_object_or_404(
            Booking, 
            id=booking_id, 
            learner=user,
            status__in=['pending', 'confirmed']
        )
    
    # Check if cancellation is allowed (e.g., not too close to session time)
    time_until_session = booking.start_utc - timezone.now()
    min_cancellation_time = timedelta(hours=2)  # 2 hours minimum notice
    
    if time_until_session < min_cancellation_time:
        return Response(
            {'error': 'Cannot cancel booking less than 2 hours before session'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    cancellation_reason = request.data.get('cancellation_reason', '')
    
    booking.status = 'cancelled'
    booking.cancellation_reason = cancellation_reason
    booking.cancelled_by = user.role
    booking.save()
    
    # Free up the availability slot
    if booking.availability_slot:
        booking.availability_slot.is_booked = False
        booking.availability_slot.save()
    
    # Send notification to other party
    NotificationService.send_booking_cancelled_notification(booking, user)
    
    serializer = BookingSerializer(booking)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsMentor])
def complete_booking(request, booking_id):
    """
    Mark a booking as completed
    POST /api/bookings/{booking_id}/complete/
    """
    booking = get_object_or_404(
        Booking, 
        id=booking_id, 
        mentor=request.user,
        status='confirmed'
    )
    
    # Check if session time has passed
    if booking.end_utc > timezone.now():
        return Response(
            {'error': 'Cannot complete booking before session end time'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    booking.status = 'completed'
    booking.completed_at = timezone.now()
    
    # Optional session notes from mentor
    session_notes = request.data.get('session_notes', '')
    if session_notes:
        booking.session_notes = session_notes
    
    booking.save()
    
    # TODO: Send notification to learner for feedback
    
    serializer = BookingSerializer(booking)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_feedback(request, booking_id):
    """
    Submit feedback for a completed booking
    POST /api/bookings/{booking_id}/feedback/
    """
    user = request.user
    
    # Get booking based on user role
    if user.role == 'mentor':
        booking = get_object_or_404(
            Booking, 
            id=booking_id, 
            mentor=user,
            status='completed'
        )
        feedback_field = 'mentor_feedback'
        rating_field = 'mentor_rating'
    else:
        booking = get_object_or_404(
            Booking, 
            id=booking_id, 
            learner=user,
            status='completed'
        )
        feedback_field = 'learner_feedback'
        rating_field = 'learner_rating'
    
    feedback = request.data.get('feedback', '')
    rating = request.data.get('rating')
    
    if not rating or not (1 <= int(rating) <= 5):
        return Response(
            {'error': 'Rating must be between 1 and 5'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    setattr(booking, feedback_field, feedback)
    setattr(booking, rating_field, int(rating))
    booking.save()
    
    # Send notification to the other party
    NotificationService.send_feedback_received_notification(booking, user)
    
    # Update mentor's overall rating
    if user.role != 'mentor':  # Learner giving feedback
        mentor = booking.mentor
        avg_rating = Booking.objects.filter(
            mentor=mentor,
            learner_rating__isnull=False
        ).aggregate(avg_rating=Avg('learner_rating'))['avg_rating']
        
        mentor.mentor_rating = round(avg_rating, 2) if avg_rating else None
        mentor.save()
    
    serializer = BookingSerializer(booking)
    return Response(serializer.data)


class MentorDashboardView(APIView):
    """
    Get mentor dashboard statistics
    GET /api/bookings/mentor-dashboard/
    """
    permission_classes = [IsMentor]
    
    def get(self, request):
        mentor = request.user
        now = timezone.now()
        
        # Basic stats
        total_bookings = Booking.objects.filter(mentor=mentor).count()
        pending_bookings = Booking.objects.filter(
            mentor=mentor, 
            status='pending'
        ).count()
        confirmed_bookings = Booking.objects.filter(
            mentor=mentor, 
            status='confirmed',
            start_utc__gt=now
        ).count()
        completed_bookings = Booking.objects.filter(
            mentor=mentor, 
            status='completed'
        ).count()
        
        # This week's sessions
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=7)
        
        this_week_sessions = Booking.objects.filter(
            mentor=mentor,
            start_utc__gte=week_start,
            start_utc__lt=week_end,
            status__in=['confirmed', 'completed']
        ).count()
        
        # Average rating
        avg_rating = Booking.objects.filter(
            mentor=mentor,
            learner_rating__isnull=False
        ).aggregate(avg_rating=Avg('learner_rating'))['avg_rating']
        
        # Recent bookings
        recent_bookings = Booking.objects.filter(
            mentor=mentor
        ).order_by('-created_at')[:5]
        
        # Upcoming sessions
        upcoming_sessions = Booking.objects.filter(
            mentor=mentor,
            status='confirmed',
            start_utc__gt=now
        ).order_by('start_utc')[:5]
        
        return Response({
            'stats': {
                'total_bookings': total_bookings,
                'pending_bookings': pending_bookings,
                'confirmed_bookings': confirmed_bookings,
                'completed_bookings': completed_bookings,
                'this_week_sessions': this_week_sessions,
                'average_rating': round(avg_rating, 2) if avg_rating else None
            },
            'recent_bookings': BookingListSerializer(recent_bookings, many=True).data,
            'upcoming_sessions': BookingListSerializer(upcoming_sessions, many=True).data
        })


class LearnerDashboardView(APIView):
    """
    Get learner dashboard statistics
    GET /api/bookings/learner-dashboard/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        learner = request.user
        now = timezone.now()
        
        # Basic stats
        total_bookings = Booking.objects.filter(learner=learner).count()
        pending_bookings = Booking.objects.filter(
            learner=learner, 
            status='pending'
        ).count()
        confirmed_bookings = Booking.objects.filter(
            learner=learner, 
            status='confirmed',
            start_utc__gt=now
        ).count()
        completed_bookings = Booking.objects.filter(
            learner=learner, 
            status='completed'
        ).count()
        
        # This month's sessions
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        
        this_month_sessions = Booking.objects.filter(
            learner=learner,
            start_utc__gte=month_start,
            start_utc__lt=next_month,
            status__in=['confirmed', 'completed']
        ).count()
        
        # Skills learned (unique skills from completed sessions)
        skills_learned = Booking.objects.filter(
            learner=learner,
            status='completed',
            skill__isnull=False
        ).values_list('skill__name', flat=True).distinct().count()
        
        # Recent bookings
        recent_bookings = Booking.objects.filter(
            learner=learner
        ).order_by('-created_at')[:5]
        
        # Upcoming sessions
        upcoming_sessions = Booking.objects.filter(
            learner=learner,
            status='confirmed',
            start_utc__gt=now
        ).order_by('start_utc')[:5]
        
        # Mentors worked with
        mentors_count = Booking.objects.filter(
            learner=learner,
            status='completed'
        ).values_list('mentor', flat=True).distinct().count()
        
        return Response({
            'stats': {
                'total_bookings': total_bookings,
                'pending_bookings': pending_bookings,
                'confirmed_bookings': confirmed_bookings,
                'completed_bookings': completed_bookings,
                'this_month_sessions': this_month_sessions,
                'skills_learned': skills_learned,
                'mentors_worked_with': mentors_count
            },
            'recent_bookings': BookingListSerializer(recent_bookings, many=True).data,
            'upcoming_sessions': BookingListSerializer(upcoming_sessions, many=True).data
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def booking_stats(request):
    """
    Get booking statistics
    GET /api/bookings/stats/
    """
    user = request.user
    
    if user.role == 'mentor':
        queryset = Booking.objects.filter(mentor=user)
    else:
        queryset = Booking.objects.filter(learner=user)
    
    # Stats by status
    stats_by_status = queryset.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Stats by month (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_stats = []
    
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        
        month_bookings = queryset.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        monthly_stats.append({
            'month': month_start.strftime('%Y-%m'),
            'count': month_bookings
        })
    
    # Skills stats (for learners)
    skills_stats = []
    if user.role != 'mentor':
        skills_stats = queryset.filter(
            skill__isnull=False
        ).values(
            'skill__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
    
    return Response({
        'status_breakdown': list(stats_by_status),
        'monthly_trends': monthly_stats,
        'top_skills': list(skills_stats) if skills_stats else []
    })


# Advanced Booking Views

class RecurringBookingTemplateViewSet(ModelViewSet):
    """ViewSet for managing recurring booking templates"""
    serializer_class = RecurringBookingTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'mentor':
            return RecurringBookingTemplate.objects.filter(mentor=user)
        elif user.role == 'learner':
            return RecurringBookingTemplate.objects.filter(learner=user)
        return RecurringBookingTemplate.objects.none()

    def perform_create(self, serializer):
        # Auto-assign mentor or learner based on user role
        if self.request.user.role == 'mentor':
            serializer.save(mentor=self.request.user)
        elif 'learner' not in serializer.validated_data and self.request.user.role == 'learner':
            serializer.save(learner=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def generate_bookings(self, request, pk=None):
        """Manually generate bookings from template"""
        template = self.get_object()
        try:
            count = template.generate_bookings()
            return Response({
                'message': f'Generated {count} bookings',
                'bookings_generated': template.bookings_generated
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle template active status"""
        template = self.get_object()
        template.is_active = not template.is_active
        template.save()
        return Response({
            'is_active': template.is_active,
            'message': f'Template {"activated" if template.is_active else "deactivated"}'
        })


class GroupBookingViewSet(ModelViewSet):
    """ViewSet for managing group bookings"""
    serializer_class = GroupBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'mentor':
            return GroupBooking.objects.filter(mentor=user)
        elif user.role == 'learner':
            # Learners can see groups they've joined or all available groups
            return GroupBooking.objects.filter(
                Q(participants__participant=user) |
                Q(status='pending', requested_start_utc__gte=timezone.now())
            ).distinct()
        return GroupBooking.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role == 'mentor':
            serializer.save(mentor=self.request.user)
        else:
            return Response(
                {'error': 'Only mentors can create group bookings'},
                status=status.HTTP_403_FORBIDDEN
            )

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a group booking"""
        group_booking = self.get_object()
        user = request.user
        
        if user.role != 'learner':
            return Response(
                {'error': 'Only learners can join group bookings'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already joined
        if group_booking.participants.filter(participant=user).exists():
            return Response(
                {'error': 'Already joined this group booking'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check capacity
        if group_booking.participants.filter(status='joined').count() >= group_booking.max_participants:
            return Response(
                {'error': 'Group booking is full'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Join the group
        participant = GroupBookingParticipant.objects.create(
            group_booking=group_booking,
            participant=user,
            status='joined'
        )
        
        # Send notification to mentor
        NotificationService.send_notification(
            recipient=group_booking.mentor,
            title="New Group Booking Participant",
            message=f"{user.full_name} joined your group session: {group_booking.title}",
            notification_type='booking'
        )
        
        return Response({
            'message': 'Successfully joined group booking',
            'participant_id': participant.id
        })

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a group booking"""
        group_booking = self.get_object()
        user = request.user
        
        try:
            participant = group_booking.participants.get(participant=user)
            participant.delete()
            
            return Response({'message': 'Successfully left group booking'})
        except GroupBookingParticipant.DoesNotExist:
            return Response(
                {'error': 'Not a participant in this group booking'},
                status=status.HTTP_400_BAD_REQUEST
            )


class BookingPackageViewSet(ModelViewSet):
    """ViewSet for managing booking packages"""
    serializer_class = BookingPackageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'mentor':
            return BookingPackage.objects.filter(mentor=user)
        elif user.role == 'learner':
            # Learners can see available packages
            return BookingPackage.objects.filter(is_active=True)
        return BookingPackage.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role == 'mentor':
            serializer.save(mentor=self.request.user)
        else:
            return Response(
                {'error': 'Only mentors can create booking packages'},
                status=status.HTTP_403_FORBIDDEN
            )

    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        """Purchase a booking package"""
        package = self.get_object()
        user = request.user
        
        if user.role != 'learner':
            return Response(
                {'error': 'Only learners can purchase packages'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not package.is_active:
            return Response(
                {'error': 'Package is not available for purchase'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create purchase
        purchase = BookingPackagePurchase.objects.create(
            package=package,
            learner=user,
            price_paid=package.price,
            currency=package.currency
        )
        
        # Send notification to mentor
        NotificationService.send_notification(
            recipient=package.mentor,
            title="Package Purchased",
            message=f"{user.full_name} purchased your package: {package.title}",
            notification_type='booking'
        )
        
        serializer = BookingPackagePurchaseSerializer(purchase)
        return Response({
            'message': 'Package purchased successfully',
            'purchase': serializer.data
        })


class BookingPackagePurchaseViewSet(ModelViewSet):
    """ViewSet for managing booking package purchases"""
    serializer_class = BookingPackagePurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch']  # Only allow read and limited updates

    def get_queryset(self):
        user = self.request.user
        if user.role == 'learner':
            return BookingPackagePurchase.objects.filter(learner=user)
        elif user.role == 'mentor':
            return BookingPackagePurchase.objects.filter(package__mentor=user)
        return BookingPackagePurchase.objects.none()


class BookingTemplateViewSet(ModelViewSet):
    """ViewSet for managing booking templates"""
    serializer_class = BookingTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsMentor]

    def get_queryset(self):
        return BookingTemplate.objects.filter(mentor=self.request.user)

    def perform_create(self, serializer):
        serializer.save(mentor=self.request.user)

    @action(detail=True, methods=['post'])
    def create_booking(self, request, pk=None):
        """Create a booking from this template"""
        template = self.get_object()
        data = request.data.copy()
        
        # Apply template defaults
        if 'duration_minutes' not in data:
            data['duration_minutes'] = template.default_duration_minutes
        if 'hourly_rate' not in data:
            data['hourly_rate'] = template.default_rate
        if 'currency' not in data:
            data['currency'] = template.currency
        if 'subject' not in data:
            data['subject'] = template.title
        
        # Merge template data
        if template.template_data:
            for key, value in template.template_data.items():
                if key not in data:
                    data[key] = value
        
        # Create booking
        data['mentor'] = template.mentor.id
        data['booking_template'] = template.id
        
        serializer = BookingCreateSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            booking = serializer.save()
            return Response(
                BookingSerializer(booking).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


# Enhanced Booking Management Views

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def advanced_booking_analytics(request):
    """Get advanced booking analytics"""
    user = request.user
    
    if user.role == 'mentor':
        bookings = Booking.objects.filter(mentor=user)
        
        # Recurring bookings stats
        recurring_stats = RecurringBookingTemplate.objects.filter(
            mentor=user
        ).aggregate(
            total_templates=Count('id'),
            active_templates=Count('id', filter=Q(is_active=True)),
            total_generated=Count('generated_bookings')
        )
        
        # Group booking stats
        group_stats = GroupBooking.objects.filter(
            mentor=user
        ).aggregate(
            total_groups=Count('id'),
            total_participants=Count('participants'),
            avg_rating=Avg('participants__rating')
        )
        
        # Package stats
        package_stats = BookingPackage.objects.filter(
            mentor=user
        ).aggregate(
            total_packages=Count('id'),
            active_packages=Count('id', filter=Q(is_active=True)),
            total_purchases=Count('purchases'),
            total_revenue=Count('purchases__price_paid')
        )
        
    else:  # learner
        bookings = Booking.objects.filter(learner=user)
        
        # Package purchases
        package_stats = BookingPackagePurchase.objects.filter(
            learner=user
        ).aggregate(
            total_purchases=Count('id'),
            active_purchases=Count('id', filter=Q(is_active=True)),
            sessions_remaining=Count('id')  # This would need a custom calculation
        )
        
        recurring_stats = {}
        group_stats = {}
    
    return Response({
        'booking_summary': {
            'total_bookings': bookings.count(),
            'completed_bookings': bookings.filter(status='completed').count(),
            'upcoming_bookings': bookings.filter(
                status__in=['pending', 'confirmed'],
                requested_start_utc__gte=timezone.now()
            ).count(),
        },
        'recurring_bookings': recurring_stats,
        'group_bookings': group_stats,
        'package_stats': package_stats,
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def book_with_package(request):
    """Create a booking using a package purchase"""
    user = request.user
    
    if user.role != 'learner':
        return Response(
            {'error': 'Only learners can book with packages'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    package_purchase_id = request.data.get('package_purchase_id')
    if not package_purchase_id:
        return Response(
            {'error': 'package_purchase_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        purchase = BookingPackagePurchase.objects.get(
            id=package_purchase_id,
            learner=user,
            is_active=True
        )
    except BookingPackagePurchase.DoesNotExist:
        return Response(
            {'error': 'Invalid or inactive package purchase'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if purchase.sessions_remaining <= 0:
        return Response(
            {'error': 'No sessions remaining in this package'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create booking
    data = request.data.copy()
    data['mentor'] = purchase.package.mentor.id
    data['learner'] = user.id
    data['package_purchase'] = purchase.id
    data['hourly_rate'] = 0  # Free since paid via package
    
    serializer = BookingCreateSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        booking = serializer.save()
        
        # Increment sessions used
        purchase.sessions_used += 1
        if purchase.sessions_used >= purchase.package.number_of_sessions:
            purchase.is_active = False
        purchase.save()
        
        return Response(
            AdvancedBookingSerializer(booking).data,
            status=status.HTTP_201_CREATED
        )
    else:
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
