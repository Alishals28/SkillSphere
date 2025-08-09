from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from icalendar import Calendar, Event
from datetime import datetime
import pytz

from bookings.models import Booking
from users.models import User


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_user_calendar(request):
    """
    Export user's bookings as iCal file
    GET /api/bookings/calendar.ics
    """
    user = request.user
    
    # Get user's bookings
    if user.role == 'mentor':
        bookings = Booking.objects.filter(
            mentor=user,
            status__in=['confirmed', 'completed']
        ).order_by('confirmed_start_utc')
    else:
        bookings = Booking.objects.filter(
            learner=user,
            status__in=['confirmed', 'completed']
        ).order_by('confirmed_start_utc')
    
    # Create calendar
    cal = Calendar()
    cal.add('prodid', '-//SkillSphere//Mentoring Sessions//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', f'SkillSphere - {user.full_name}')
    cal.add('x-wr-caldesc', f'Mentoring sessions for {user.full_name}')
    
    for booking in bookings:
        event = Event()
        
        # Basic event info
        event.add('uid', f'skillsphere-booking-{booking.id}@skillsphere.com')
        event.add('dtstart', booking.confirmed_start_utc or booking.requested_start_utc)
        event.add('dtend', booking.confirmed_end_utc or booking.requested_end_utc)
        event.add('dtstamp', booking.created_at)
        event.add('created', booking.created_at)
        event.add('last-modified', booking.updated_at)
        
        # Event details
        if user.role == 'mentor':
            other_user = booking.learner
            event.add('summary', f'Mentoring Session: {booking.subject}')
            event.add('description', 
                f'Mentoring session with {other_user.full_name}\\n'
                f'Subject: {booking.subject}\\n'
                f'Learner Notes: {booking.learner_notes or "None"}\\n'
                f'Session ID: {booking.id}'
            )
        else:
            other_user = booking.mentor
            event.add('summary', f'Learning Session: {booking.subject}')
            event.add('description',
                f'Learning session with {other_user.full_name}\\n'
                f'Subject: {booking.subject}\\n'
                f'Your Notes: {booking.learner_notes or "None"}\\n'
                f'Session ID: {booking.id}'
            )
        
        # Add participants
        event.add('organizer', f'MAILTO:{booking.mentor.email}')
        event.add('attendee', f'MAILTO:{booking.learner.email}')
        
        # Status based on booking status
        if booking.status == 'confirmed':
            event.add('status', 'CONFIRMED')
        elif booking.status == 'completed':
            event.add('status', 'CONFIRMED')
        else:
            event.add('status', 'TENTATIVE')
        
        # Location (meeting URL if available)
        if booking.meeting_url:
            event.add('location', booking.meeting_url)
            event.add('url', booking.meeting_url)
        
        # Categories
        event.add('categories', ['SkillSphere', 'Mentoring'])
        
        # Reminder (30 minutes before)
        from icalendar import Alarm
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', f'SkillSphere session starting soon: {booking.subject}')
        alarm.add('trigger', '-PT30M')  # 30 minutes before
        event.add_component(alarm)
        
        cal.add_component(event)
    
    # Generate response
    response = HttpResponse(cal.to_ical(), content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="skillsphere-{user.role}-calendar.ics"'
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_booking_ical(request, booking_id):
    """
    Export specific booking as iCal file
    GET /api/bookings/{id}/calendar.ics
    """
    user = request.user
    
    # Get booking
    if user.role == 'mentor':
        booking = get_object_or_404(Booking, id=booking_id, mentor=user)
    else:
        booking = get_object_or_404(Booking, id=booking_id, learner=user)
    
    # Create calendar with single event
    cal = Calendar()
    cal.add('prodid', '-//SkillSphere//Mentoring Session//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    
    event = Event()
    
    # Basic event info
    event.add('uid', f'skillsphere-booking-{booking.id}@skillsphere.com')
    event.add('dtstart', booking.confirmed_start_utc or booking.requested_start_utc)
    event.add('dtend', booking.confirmed_end_utc or booking.requested_end_utc)
    event.add('dtstamp', booking.created_at)
    event.add('created', booking.created_at)
    event.add('last-modified', booking.updated_at)
    
    # Event details
    if user.role == 'mentor':
        other_user = booking.learner
        event.add('summary', f'Mentoring Session: {booking.subject}')
        event.add('description', 
            f'Mentoring session with {other_user.full_name}\\n'
            f'Subject: {booking.subject}\\n'
            f'Learner Notes: {booking.learner_notes or "None"}\\n'
            f'Session ID: {booking.id}'
        )
    else:
        other_user = booking.mentor
        event.add('summary', f'Learning Session: {booking.subject}')
        event.add('description',
            f'Learning session with {other_user.full_name}\\n'
            f'Subject: {booking.subject}\\n'
            f'Your Notes: {booking.learner_notes or "None"}\\n'
            f'Session ID: {booking.id}'
        )
    
    # Add participants
    event.add('organizer', f'MAILTO:{booking.mentor.email}')
    event.add('attendee', f'MAILTO:{booking.learner.email}')
    
    # Status
    if booking.status == 'confirmed':
        event.add('status', 'CONFIRMED')
    elif booking.status == 'completed':
        event.add('status', 'CONFIRMED')
    else:
        event.add('status', 'TENTATIVE')
    
    # Location
    if booking.meeting_url:
        event.add('location', booking.meeting_url)
        event.add('url', booking.meeting_url)
    
    # Categories
    event.add('categories', ['SkillSphere', 'Mentoring'])
    
    # Reminder
    from icalendar import Alarm
    alarm = Alarm()
    alarm.add('action', 'DISPLAY')
    alarm.add('description', f'SkillSphere session starting soon: {booking.subject}')
    alarm.add('trigger', '-PT30M')  # 30 minutes before
    event.add_component(alarm)
    
    cal.add_component(event)
    
    # Generate response
    response = HttpResponse(cal.to_ical(), content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="skillsphere-session-{booking.id}.ics"'
    return response
