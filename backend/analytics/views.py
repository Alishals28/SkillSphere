from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count, Avg, Sum, F, Case, When, IntegerField, DecimalField
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth import get_user_model

from .models import (
    AnalyticsEvent, MentorAnalytics, LearnerAnalytics, 
    PlatformAnalytics, SkillAnalytics, UserEngagementMetrics
)
from bookings.models import Booking
from skills.models import Skill
from chat.models import Message

User = get_user_model()


class MentorDashboardView(APIView):
    """
    Comprehensive mentor dashboard analytics
    GET /api/analytics/mentor/dashboard/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'mentor':
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        mentor = request.user
        period = request.GET.get('period', '30')  # days
        
        # Get or create mentor analytics
        analytics, _ = MentorAnalytics.objects.get_or_create(mentor=mentor)
        
        # Calculate date ranges
        end_date = timezone.now()
        start_date = end_date - timedelta(days=int(period))
        
        # Session statistics
        sessions_data = self._get_mentor_sessions_data(mentor, start_date, end_date)
        
        # Earnings data
        earnings_data = self._get_mentor_earnings_data(mentor, start_date, end_date)
        
        # Rating and review data
        rating_data = self._get_mentor_rating_data(mentor)
        
        # Engagement metrics
        engagement_data = self._get_mentor_engagement_data(mentor, start_date, end_date)
        
        # Upcoming sessions
        upcoming_sessions = self._get_upcoming_sessions(mentor)
        
        # Recent activity
        recent_activity = self._get_recent_activity(mentor)
        
        return Response({
            'mentor_info': {
                'id': mentor.id,
                'name': mentor.full_name,
                'profile_picture': mentor.profile_picture.url if mentor.profile_picture else None,
                'rating': analytics.average_rating,
                'total_sessions': analytics.total_sessions,
                'total_earnings': analytics.total_earnings,
            },
            'sessions': sessions_data,
            'earnings': earnings_data,
            'ratings': rating_data,
            'engagement': engagement_data,
            'upcoming_sessions': upcoming_sessions,
            'recent_activity': recent_activity,
            'period': period
        })
    
    def _get_mentor_sessions_data(self, mentor, start_date, end_date):
        """Get session statistics for mentor"""
        sessions_qs = Booking.objects.filter(
            mentor=mentor,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        total_sessions = sessions_qs.count()
        completed_sessions = sessions_qs.filter(status='completed').count()
        cancelled_sessions = sessions_qs.filter(status='cancelled').count()
        pending_sessions = sessions_qs.filter(status='pending').count()
        
        # Sessions over time (daily)
        sessions_timeline = sessions_qs.extra({
            'date': 'date(created_at)'
        }).values('date').annotate(
            count=Count('id'),
            completed=Count(Case(When(status='completed', then=1), output_field=IntegerField())),
            cancelled=Count(Case(When(status='cancelled', then=1), output_field=IntegerField()))
        ).order_by('date')
        
        return {
            'total': total_sessions,
            'completed': completed_sessions,
            'cancelled': cancelled_sessions,
            'pending': pending_sessions,
            'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            'timeline': list(sessions_timeline)
        }
    
    def _get_mentor_earnings_data(self, mentor, start_date, end_date):
        """Get earnings data for mentor"""
        bookings_qs = Booking.objects.filter(
            mentor=mentor,
            status='completed',
            confirmed_start_utc__gte=start_date,
            confirmed_start_utc__lte=end_date
        )
        
        total_earnings = bookings_qs.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Earnings over time
        earnings_timeline = bookings_qs.extra({
            'date': 'date(confirmed_start_utc)'
        }).values('date').annotate(
            earnings=Sum('total_amount')
        ).order_by('date')
        
        # Average session value
        avg_session_value = bookings_qs.aggregate(
            avg=Avg('total_amount')
        )['avg'] or 0
        
        # Top paying skills
        top_skills = bookings_qs.values(
            'primary_skill__name'
        ).annotate(
            earnings=Sum('total_amount'),
            sessions=Count('id')
        ).order_by('-earnings')[:5]
        
        return {
            'total_earnings': total_earnings,
            'average_session_value': avg_session_value,
            'timeline': list(earnings_timeline),
            'top_skills': list(top_skills)
        }
    
    def _get_mentor_rating_data(self, mentor):
        """Get rating and review data"""
        bookings_qs = Booking.objects.filter(
            mentor=mentor,
            status='completed',
            learner_rating__isnull=False
        )
        
        ratings_data = bookings_qs.aggregate(
            average_rating=Avg('learner_rating'),
            total_reviews=Count('learner_rating'),
            five_stars=Count(Case(When(learner_rating=5, then=1), output_field=IntegerField())),
            four_stars=Count(Case(When(learner_rating=4, then=1), output_field=IntegerField())),
            three_stars=Count(Case(When(learner_rating=3, then=1), output_field=IntegerField())),
            two_stars=Count(Case(When(learner_rating=2, then=1), output_field=IntegerField())),
            one_star=Count(Case(When(learner_rating=1, then=1), output_field=IntegerField()))
        )
        
        # Recent reviews
        recent_reviews = bookings_qs.filter(
            learner_feedback__isnull=False
        ).exclude(learner_feedback='').order_by('-updated_at')[:5].values(
            'learner__first_name',
            'learner_rating',
            'learner_feedback',
            'updated_at',
            'subject'
        )
        
        return {
            **ratings_data,
            'recent_reviews': list(recent_reviews)
        }
    
    def _get_mentor_engagement_data(self, mentor, start_date, end_date):
        """Get engagement metrics"""
        # Profile views (would come from analytics events)
        profile_views = AnalyticsEvent.objects.filter(
            event_type='profile_view',
            event_data__mentor_id=mentor.id,
            created_at__gte=start_date,
            created_at__lte=end_date
        ).count()
        
        # Response time (average time to respond to bookings)
        response_times = Booking.objects.filter(
            mentor=mentor,
            confirmed_at__isnull=False,
            created_at__gte=start_date
        ).annotate(
            response_time=F('confirmed_at') - F('created_at')
        ).aggregate(avg_response_time=Avg('response_time'))
        
        # Messages sent
        messages_sent = Message.objects.filter(
            sender=mentor,
            created_at__gte=start_date,
            created_at__lte=end_date
        ).count()
        
        return {
            'profile_views': profile_views,
            'average_response_time_hours': response_times['avg_response_time'].total_seconds() / 3600 if response_times['avg_response_time'] else 0,
            'messages_sent': messages_sent
        }
    
    def _get_upcoming_sessions(self, mentor):
        """Get upcoming sessions for mentor"""
        upcoming = Booking.objects.filter(
            mentor=mentor,
            status__in=['confirmed', 'pending'],
            requested_start_utc__gte=timezone.now()
        ).order_by('requested_start_utc')[:5]
        
        return [{
            'id': session.id,
            'learner_name': session.learner.full_name,
            'subject': session.subject,
            'start_time': session.requested_start_utc,
            'duration': session.duration_minutes,
            'status': session.status
        } for session in upcoming]
    
    def _get_recent_activity(self, mentor):
        """Get recent activity for mentor"""
        recent_bookings = Booking.objects.filter(
            mentor=mentor
        ).order_by('-created_at')[:10]
        
        activity = []
        for booking in recent_bookings:
            activity.append({
                'type': 'booking',
                'description': f"Session with {booking.learner.first_name} - {booking.subject}",
                'status': booking.status,
                'timestamp': booking.created_at
            })
        
        return activity


class LearnerDashboardView(APIView):
    """
    Comprehensive learner dashboard analytics
    GET /api/analytics/learner/dashboard/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'learner':
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        learner = request.user
        period = request.GET.get('period', '30')  # days
        
        # Get or create learner analytics
        analytics, _ = LearnerAnalytics.objects.get_or_create(learner=learner)
        
        # Calculate date ranges
        end_date = timezone.now()
        start_date = end_date - timedelta(days=int(period))
        
        # Learning progress
        learning_data = self._get_learner_progress_data(learner, start_date, end_date)
        
        # Spending data
        spending_data = self._get_learner_spending_data(learner, start_date, end_date)
        
        # Skills data
        skills_data = self._get_learner_skills_data(learner)
        
        # Upcoming sessions
        upcoming_sessions = self._get_learner_upcoming_sessions(learner)
        
        # Learning goals
        goals_data = self._get_learning_goals_data(learner)
        
        return Response({
            'learner_info': {
                'id': learner.id,
                'name': learner.full_name,
                'profile_picture': learner.profile_picture.url if learner.profile_picture else None,
                'total_sessions': analytics.total_sessions,
                'learning_hours': analytics.total_learning_hours,
                'total_spent': analytics.total_spent,
            },
            'learning_progress': learning_data,
            'spending': spending_data,
            'skills': skills_data,
            'upcoming_sessions': upcoming_sessions,
            'goals': goals_data,
            'period': period
        })
    
    def _get_learner_progress_data(self, learner, start_date, end_date):
        """Get learning progress data"""
        sessions_qs = Booking.objects.filter(
            learner=learner,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        progress_data = sessions_qs.aggregate(
            total_sessions=Count('id'),
            completed_sessions=Count(Case(When(status='completed', then=1), output_field=IntegerField())),
            cancelled_sessions=Count(Case(When(status='cancelled', then=1), output_field=IntegerField())),
            total_hours=Sum('duration_minutes') / 60.0
        )
        
        # Learning timeline
        learning_timeline = sessions_qs.filter(
            status='completed'
        ).extra({
            'date': 'date(confirmed_start_utc)'
        }).values('date').annotate(
            sessions=Count('id'),
            hours=Sum('duration_minutes') / 60.0
        ).order_by('date')
        
        return {
            **progress_data,
            'completion_rate': (progress_data['completed_sessions'] / progress_data['total_sessions'] * 100) if progress_data['total_sessions'] > 0 else 0,
            'timeline': list(learning_timeline)
        }
    
    def _get_learner_spending_data(self, learner, start_date, end_date):
        """Get spending data for learner"""
        bookings_qs = Booking.objects.filter(
            learner=learner,
            status='completed',
            confirmed_start_utc__gte=start_date,
            confirmed_start_utc__lte=end_date
        )
        
        spending_data = bookings_qs.aggregate(
            total_spent=Sum('total_amount'),
            average_session_cost=Avg('total_amount')
        )
        
        # Spending timeline
        spending_timeline = bookings_qs.extra({
            'date': 'date(confirmed_start_utc)'
        }).values('date').annotate(
            spent=Sum('total_amount')
        ).order_by('date')
        
        # Spending by skill
        spending_by_skill = bookings_qs.values(
            'primary_skill__name'
        ).annotate(
            spent=Sum('total_amount'),
            sessions=Count('id')
        ).order_by('-spent')[:5]
        
        return {
            **spending_data,
            'timeline': list(spending_timeline),
            'by_skill': list(spending_by_skill)
        }
    
    def _get_learner_skills_data(self, learner):
        """Get skills learning data"""
        # Skills being learned (from bookings)
        skills_progress = Booking.objects.filter(
            learner=learner,
            status='completed'
        ).values(
            'primary_skill__name',
            'primary_skill__id'
        ).annotate(
            sessions_count=Count('id'),
            total_hours=Sum('duration_minutes') / 60.0,
            average_rating=Avg('learner_rating')
        ).order_by('-sessions_count')
        
        return {
            'skills_progress': list(skills_progress)
        }
    
    def _get_learner_upcoming_sessions(self, learner):
        """Get upcoming sessions for learner"""
        upcoming = Booking.objects.filter(
            learner=learner,
            status__in=['confirmed', 'pending'],
            requested_start_utc__gte=timezone.now()
        ).order_by('requested_start_utc')[:5]
        
        return [{
            'id': session.id,
            'mentor_name': session.mentor.full_name,
            'subject': session.subject,
            'start_time': session.requested_start_utc,
            'duration': session.duration_minutes,
            'status': session.status
        } for session in upcoming]
    
    def _get_learning_goals_data(self, learner):
        """Get learning goals progress"""
        # This would integrate with AI learning paths
        return {
            'active_goals': 0,
            'completed_goals': 0,
            'goal_completion_rate': 0
        }


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def platform_analytics(request):
    """
    Platform-wide analytics for admins
    GET /api/analytics/platform/
    """
    period = request.GET.get('period', '30')  # days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=int(period))
    
    # User statistics
    user_stats = User.objects.aggregate(
        total_users=Count('id'),
        total_mentors=Count(Case(When(role='mentor', then=1), output_field=IntegerField())),
        total_learners=Count(Case(When(role='learner', then=1), output_field=IntegerField())),
        active_mentors=Count(Case(When(
            role='mentor', 
            last_active__gte=start_date, 
            then=1
        ), output_field=IntegerField())),
        new_users=Count(Case(When(
            created_at__gte=start_date, 
            then=1
        ), output_field=IntegerField()))
    )
    
    # Session statistics
    session_stats = Booking.objects.filter(
        created_at__gte=start_date
    ).aggregate(
        total_sessions=Count('id'),
        completed_sessions=Count(Case(When(status='completed', then=1), output_field=IntegerField())),
        cancelled_sessions=Count(Case(When(status='cancelled', then=1), output_field=IntegerField())),
        total_revenue=Sum('total_amount', filter=Q(status='completed')),
        average_rating=Avg('learner_rating', filter=Q(status='completed'))
    )
    
    # Growth trends
    daily_growth = User.objects.filter(
        created_at__gte=start_date
    ).extra({
        'date': 'date(created_at)'
    }).values('date').annotate(
        new_users=Count('id'),
        new_mentors=Count(Case(When(role='mentor', then=1), output_field=IntegerField())),
        new_learners=Count(Case(When(role='learner', then=1), output_field=IntegerField()))
    ).order_by('date')
    
    # Session trends
    daily_sessions = Booking.objects.filter(
        created_at__gte=start_date
    ).extra({
        'date': 'date(created_at)'
    }).values('date').annotate(
        sessions=Count('id'),
        revenue=Sum('total_amount', filter=Q(status='completed'))
    ).order_by('date')
    
    # Top skills by demand
    top_skills = Booking.objects.filter(
        created_at__gte=start_date
    ).values(
        'primary_skill__name'
    ).annotate(
        sessions=Count('id'),
        revenue=Sum('total_amount', filter=Q(status='completed'))
    ).order_by('-sessions')[:10]
    
    return Response({
        'period': period,
        'user_statistics': user_stats,
        'session_statistics': session_stats,
        'growth_trends': list(daily_growth),
        'session_trends': list(daily_sessions),
        'top_skills': list(top_skills)
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def track_event(request):
    """
    Track analytics event
    POST /api/analytics/track/
    """
    event_type = request.data.get('event_type')
    event_data = request.data.get('event_data', {})
    session_id = request.data.get('session_id', '')
    
    if not event_type:
        return Response({'error': 'event_type is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get client info
    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    referrer = request.META.get('HTTP_REFERER', '')
    
    # Create analytics event
    AnalyticsEvent.objects.create(
        user=request.user,
        event_type=event_type,
        event_data=event_data,
        session_id=session_id,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer
    )
    
    return Response({'status': 'Event tracked successfully'})


class SkillAnalyticsView(APIView):
    """
    Analytics for specific skills
    GET /api/analytics/skills/<skill_id>/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, skill_id):
        try:
            skill = Skill.objects.get(id=skill_id)
        except Skill.DoesNotExist:
            return Response({'error': 'Skill not found'}, status=status.HTTP_404_NOT_FOUND)
        
        period = request.GET.get('period', '30')
        end_date = timezone.now()
        start_date = end_date - timedelta(days=int(period))
        
        # Skill demand data
        skill_bookings = Booking.objects.filter(
            primary_skill=skill,
            created_at__gte=start_date
        )
        
        demand_data = skill_bookings.aggregate(
            total_sessions=Count('id'),
            unique_learners=Count('learner', distinct=True),
            average_rating=Avg('learner_rating', filter=Q(status='completed')),
            total_revenue=Sum('total_amount', filter=Q(status='completed'))
        )
        
        # Mentor data
        mentors_data = User.objects.filter(
            role='mentor',
            mentor_skills__skill=skill
        ).aggregate(
            total_mentors=Count('id'),
            average_rate=Avg('mentor_skills__hourly_rate'),
            min_rate=Min('mentor_skills__hourly_rate'),
            max_rate=Max('mentor_skills__hourly_rate')
        )
        
        # Demand timeline
        demand_timeline = skill_bookings.extra({
            'date': 'date(created_at)'
        }).values('date').annotate(
            sessions=Count('id')
        ).order_by('date')
        
        return Response({
            'skill': {
                'id': skill.id,
                'name': skill.name,
                'category': skill.category.name if skill.category else None
            },
            'demand': demand_data,
            'mentors': mentors_data,
            'timeline': list(demand_timeline),
            'period': period
        })
