from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404

from .models import Booking
from .serializers import (
    BookingSerializer,
    BookingCreateSerializer,
    BookingUpdateSerializer,
    BookingStatusUpdateSerializer,
    BookingListSerializer,
    BookingStatisticsSerializer
)
from users.permissions import IsMentor, IsMentorOrAdmin
from users.models import User
from availability.models import AvailabilitySlot


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
    
    # TODO: Send notification to learner
    
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
    
    # TODO: Send notification to other party
    
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
