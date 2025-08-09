from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
import pytz

from .models import (
    WeeklyAvailability, 
    AvailabilitySlot, 
    AvailabilityException,
    MentorAvailabilitySettings
)
from .serializers import (
    WeeklyAvailabilitySerializer,
    AvailabilitySlotSerializer,
    AvailabilitySlotPublicSerializer,
    AvailabilityExceptionSerializer,
    MentorAvailabilitySettingsSerializer,
    AvailabilityBulkCreateSerializer,
    MentorAvailabilityCalendarSerializer
)
from users.permissions import IsMentor, IsMentorOrAdmin


class WeeklyAvailabilityListView(generics.ListCreateAPIView):
    """
    List and create weekly availability patterns
    GET/POST /api/availability/weekly/
    """
    serializer_class = WeeklyAvailabilitySerializer
    permission_classes = [IsMentor]
    
    def get_queryset(self):
        return WeeklyAvailability.objects.filter(
            mentor=self.request.user,
            is_active=True
        ).order_by('weekday', 'start_time')


class WeeklyAvailabilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete weekly availability
    GET/PUT/PATCH/DELETE /api/availability/weekly/{id}/
    """
    serializer_class = WeeklyAvailabilitySerializer
    permission_classes = [IsMentor]
    
    def get_queryset(self):
        return WeeklyAvailability.objects.filter(mentor=self.request.user)


class AvailabilitySlotListView(generics.ListCreateAPIView):
    """
    List and create availability slots
    GET/POST /api/availability/slots/
    """
    serializer_class = AvailabilitySlotSerializer
    permission_classes = [IsMentor]
    
    def get_queryset(self):
        queryset = AvailabilitySlot.objects.filter(mentor=self.request.user)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(start_utc__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_utc__lte=end_date)
        
        # Filter by status
        is_booked = self.request.query_params.get('is_booked')
        if is_booked is not None:
            queryset = queryset.filter(is_booked=is_booked.lower() == 'true')
        
        is_blocked = self.request.query_params.get('is_blocked')
        if is_blocked is not None:
            queryset = queryset.filter(is_blocked=is_blocked.lower() == 'true')
        
        # Only future slots by default
        only_future = self.request.query_params.get('only_future', 'true')
        if only_future.lower() == 'true':
            queryset = queryset.filter(start_utc__gt=timezone.now())
        
        return queryset.order_by('start_utc')


class AvailabilitySlotDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete availability slot
    GET/PUT/PATCH/DELETE /api/availability/slots/{id}/
    """
    serializer_class = AvailabilitySlotSerializer
    permission_classes = [IsMentor]
    
    def get_queryset(self):
        return AvailabilitySlot.objects.filter(mentor=self.request.user)


class PublicMentorAvailabilityView(generics.ListAPIView):
    """
    Public view of mentor's available slots (for learners)
    GET /api/mentors/{mentor_id}/availability/
    """
    serializer_class = AvailabilitySlotPublicSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        mentor_id = self.kwargs['mentor_id']
        now = timezone.now()
        
        queryset = AvailabilitySlot.objects.filter(
            mentor_id=mentor_id,
            mentor__role='mentor',
            mentor__is_mentor_approved=True,
            start_utc__gt=now,
            is_booked=False,
            is_blocked=False
        ).order_by('start_utc')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(start_utc__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_utc__lte=end_date)
        
        # Limit to next 30 days by default
        if not end_date:
            max_date = now + timedelta(days=30)
            queryset = queryset.filter(start_utc__lte=max_date)
        
        return queryset


class AvailabilityExceptionListView(generics.ListCreateAPIView):
    """
    List and create availability exceptions
    GET/POST /api/availability/exceptions/
    """
    serializer_class = AvailabilityExceptionSerializer
    permission_classes = [IsMentor]
    
    def get_queryset(self):
        return AvailabilityException.objects.filter(
            mentor=self.request.user
        ).order_by('start_utc')


class AvailabilityExceptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete availability exception
    GET/PUT/PATCH/DELETE /api/availability/exceptions/{id}/
    """
    serializer_class = AvailabilityExceptionSerializer
    permission_classes = [IsMentor]
    
    def get_queryset(self):
        return AvailabilityException.objects.filter(mentor=self.request.user)


class MentorAvailabilitySettingsView(APIView):
    """
    Get or update mentor availability settings
    GET/PUT /api/availability/settings/
    """
    permission_classes = [IsMentor]
    
    def get(self, request):
        settings, created = MentorAvailabilitySettings.objects.get_or_create(
            mentor=request.user
        )
        serializer = MentorAvailabilitySettingsSerializer(settings)
        return Response(serializer.data)
    
    def put(self, request):
        settings, created = MentorAvailabilitySettings.objects.get_or_create(
            mentor=request.user
        )
        serializer = MentorAvailabilitySettingsSerializer(
            settings, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsMentor])
def bulk_create_slots(request):
    """
    Bulk create availability slots
    POST /api/availability/slots/bulk/
    """
    serializer = AvailabilityBulkCreateSerializer(
        data=request.data, 
        context={'request': request}
    )
    
    if serializer.is_valid():
        created_slots = serializer.save()
        response_data = {
            'created_count': len(created_slots),
            'slots': AvailabilitySlotSerializer(created_slots, many=True).data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsMentor])
def block_time_period(request):
    """
    Block a time period (create exception)
    POST /api/availability/block/
    """
    start_utc = request.data.get('start_utc')
    end_utc = request.data.get('end_utc')
    reason = request.data.get('reason', 'Blocked by mentor')
    exception_type = request.data.get('exception_type', 'unavailable')
    
    if not start_utc or not end_utc:
        return Response(
            {'error': 'start_utc and end_utc are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create exception
    exception = AvailabilityException.objects.create(
        mentor=request.user,
        start_utc=start_utc,
        end_utc=end_utc,
        reason=reason,
        exception_type=exception_type
    )
    
    # Block overlapping slots
    overlapping_slots = AvailabilitySlot.objects.filter(
        mentor=request.user,
        start_utc__lt=end_utc,
        end_utc__gt=start_utc,
        is_booked=False
    )
    
    blocked_count = overlapping_slots.update(is_blocked=True)
    
    return Response({
        'exception': AvailabilityExceptionSerializer(exception).data,
        'blocked_slots_count': blocked_count
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def mentor_availability_calendar(request, mentor_id):
    """
    Get mentor's availability in calendar format
    GET /api/mentors/{mentor_id}/availability/calendar/
    """
    from users.models import User
    from django.shortcuts import get_object_or_404
    
    mentor = get_object_or_404(
        User, 
        id=mentor_id, 
        role='mentor', 
        is_mentor_approved=True
    )
    
    # Get date range (default to next 30 days)
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    else:
        start_date = timezone.now().date()
    
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        end_date = start_date + timedelta(days=30)
    
    calendar_data = []
    current_date = start_date
    
    while current_date <= end_date:
        # Get slots for this date
        day_start = timezone.make_aware(datetime.combine(current_date, datetime.min.time()))
        day_end = timezone.make_aware(datetime.combine(current_date, datetime.max.time()))
        
        available_slots = AvailabilitySlot.objects.filter(
            mentor=mentor,
            start_utc__gte=day_start,
            start_utc__lte=day_end,
            is_booked=False,
            is_blocked=False
        ).order_by('start_utc')
        
        total_slots = AvailabilitySlot.objects.filter(
            mentor=mentor,
            start_utc__gte=day_start,
            start_utc__lte=day_end
        ).count()
        
        booked_slots = AvailabilitySlot.objects.filter(
            mentor=mentor,
            start_utc__gte=day_start,
            start_utc__lte=day_end,
            is_booked=True
        ).count()
        
        exceptions = AvailabilityException.objects.filter(
            mentor=mentor,
            start_utc__lte=day_end,
            end_utc__gte=day_start
        )
        
        calendar_data.append({
            'date': current_date,
            'available_slots': AvailabilitySlotPublicSerializer(available_slots, many=True).data,
            'total_slots': total_slots,
            'booked_slots': booked_slots,
            'exceptions': AvailabilityExceptionSerializer(exceptions, many=True).data
        })
        
        current_date += timedelta(days=1)
    
    return Response(calendar_data)


@api_view(['POST'])
@permission_classes([IsMentor])
def generate_slots_from_weekly(request):
    """
    Generate availability slots from weekly patterns
    POST /api/availability/generate-from-weekly/
    """
    start_date_str = request.data.get('start_date')
    end_date_str = request.data.get('end_date')
    
    if not start_date_str or not end_date_str:
        return Response(
            {'error': 'start_date and end_date are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    
    if (end_date - start_date).days > 90:
        return Response(
            {'error': 'Date range cannot exceed 90 days'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get mentor's weekly availability patterns
    weekly_patterns = WeeklyAvailability.objects.filter(
        mentor=request.user,
        is_active=True
    )
    
    created_slots = []
    current_date = start_date
    
    while current_date <= end_date:
        weekday = current_date.weekday()
        
        # Find patterns for this weekday
        day_patterns = weekly_patterns.filter(weekday=weekday)
        
        for pattern in day_patterns:
            # Create slot for this pattern
            slot_start = datetime.combine(current_date, pattern.start_time)
            slot_end = datetime.combine(current_date, pattern.end_time)
            
            # Convert to mentor's timezone then to UTC
            mentor_tz = pytz.timezone(request.user.timezone)
            slot_start_utc = mentor_tz.localize(slot_start).astimezone(pytz.UTC)
            slot_end_utc = mentor_tz.localize(slot_end).astimezone(pytz.UTC)
            
            # Check if slot already exists
            existing = AvailabilitySlot.objects.filter(
                mentor=request.user,
                start_utc=slot_start_utc,
                end_utc=slot_end_utc
            ).exists()
            
            if not existing:
                slot = AvailabilitySlot.objects.create(
                    mentor=request.user,
                    start_utc=slot_start_utc,
                    end_utc=slot_end_utc,
                    weekly_availability=pattern
                )
                created_slots.append(slot)
        
        current_date += timedelta(days=1)
    
    return Response({
        'created_count': len(created_slots),
        'message': f'Generated {len(created_slots)} availability slots'
    }, status=status.HTTP_201_CREATED)
