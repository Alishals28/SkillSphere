from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from users.models import User
# Temporarily comment out imports that might cause issues
# from bookings.models import Booking
# from reviews.models import Review
# from gamification.models import Badge, UserBadge
from mentoring_sessions.models import Session


class LearnerDashboardView(APIView):
    """
    API endpoint for learner dashboard data
    GET /api/dashboard/learner/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'learner':
            return Response(
                {'error': 'Only learners can access this endpoint'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        user = request.user
        now = timezone.now()
        
        # Get user statistics
        stats = self.get_user_stats(user, now)
        
        # Get upcoming sessions
        upcoming_sessions = self.get_upcoming_sessions(user, now)
        
        # Get recommended mentors
        recommended_mentors = self.get_recommended_mentors(user)
        
        # Get recent activity
        recent_activity = self.get_recent_activity(user)
        
        # Get progress data
        progress_data = self.get_progress_data(user)

        return Response({
            'stats': stats,
            'upcoming_sessions': upcoming_sessions,
            'recommended_mentors': recommended_mentors,
            'recent_activity': recent_activity,
            'progress': progress_data
        })

    def get_user_stats(self, user, now):
        """Calculate user statistics"""
        # Get completed sessions count
        completed_sessions = Booking.objects.filter(
            learner=user,
            status='completed'
        ).count()
        
        # Get badges earned
        badges_earned = UserBadge.objects.filter(user=user).count()
        
        # Calculate total learning hours (estimate: 1 hour per session)
        total_hours = completed_sessions * 1  # Simplified calculation
        
        # Calculate current streak (consecutive days with activity)
        streak_days = self.calculate_streak(user, now)
        
        return {
            'sessions_completed': completed_sessions,
            'badges_earned': badges_earned,
            'hours_learned': total_hours,
            'streak_days': streak_days
        }

    def get_upcoming_sessions(self, user, now):
        """Get upcoming sessions for the user"""
        upcoming_bookings = Booking.objects.filter(
            learner=user,
            start_time__gt=now,
            status__in=['confirmed', 'pending']
        ).select_related('mentor').order_by('start_time')[:5]
        
        sessions = []
        for booking in upcoming_bookings:
            sessions.append({
                'id': booking.id,
                'mentor_name': f"{booking.mentor.first_name} {booking.mentor.last_name}",
                'mentor_avatar': booking.mentor.first_name[0] + booking.mentor.last_name[0],
                'topic': booking.topic or 'General Mentoring',
                'start_time': booking.start_time,
                'duration': booking.duration,
                'status': booking.status
            })
        
        return sessions

    def get_recommended_mentors(self, user):
        """Get recommended mentors based on user's interests and goals"""
        # Get mentors with good ratings and availability
        mentors = User.objects.filter(
            role='mentor',
            is_mentor_approved=True,
            is_active=True
        ).annotate(
            avg_rating=Count('received_reviews'),
            session_count=Count('mentor_bookings')
        ).order_by('-avg_rating', '-session_count')[:5]
        
        recommendations = []
        for mentor in mentors:
            # Calculate average rating
            reviews = Review.objects.filter(mentor=mentor)
            avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 4.5
            
            recommendations.append({
                'id': mentor.id,
                'name': f"{mentor.first_name} {mentor.last_name}",
                'avatar': mentor.first_name[0] + mentor.last_name[0],
                'specialty': mentor.bio[:50] + '...' if mentor.bio else 'General Mentoring',
                'rating': round(avg_rating, 1),
                'session_count': mentor.session_count or 0
            })
        
        return recommendations

    def get_recent_activity(self, user):
        """Get recent user activities"""
        activities = []
        
        # Recent completed sessions
        recent_sessions = Booking.objects.filter(
            learner=user,
            status='completed',
            end_time__gte=timezone.now() - timedelta(days=30)
        ).select_related('mentor').order_by('-end_time')[:3]
        
        for session in recent_sessions:
            activities.append({
                'type': 'session',
                'icon': '📚',
                'text': f'Completed session with {session.mentor.first_name} {session.mentor.last_name}',
                'time': session.end_time
            })
        
        # Recent badges
        recent_badges = UserBadge.objects.filter(
            user=user,
            earned_at__gte=timezone.now() - timedelta(days=30)
        ).select_related('badge').order_by('-earned_at')[:2]
        
        for user_badge in recent_badges:
            activities.append({
                'type': 'badge',
                'icon': '🏆',
                'text': f'Earned "{user_badge.badge.name}" badge',
                'time': user_badge.earned_at
            })
        
        # Sort by time and return recent 5
        activities.sort(key=lambda x: x['time'], reverse=True)
        return activities[:5]

    def get_progress_data(self, user):
        """Get user progress data"""
        # Monthly goal progress (example: 8 sessions per month)
        monthly_goal = 8
        current_month_sessions = Booking.objects.filter(
            learner=user,
            status='completed',
            start_time__month=timezone.now().month,
            start_time__year=timezone.now().year
        ).count()
        
        monthly_progress = min(100, (current_month_sessions / monthly_goal) * 100)
        
        return {
            'monthly_goal_progress': round(monthly_progress),
            'monthly_sessions': current_month_sessions,
            'monthly_goal': monthly_goal
        }

    def calculate_streak(self, user, now):
        """Calculate consecutive days with learning activity"""
        # Simplified streak calculation
        # In a real app, you'd track daily activities more precisely
        recent_sessions = Booking.objects.filter(
            learner=user,
            status='completed',
            end_time__gte=now - timedelta(days=30)
        ).order_by('-end_time')
        
        if not recent_sessions:
            return 0
        
        # Simple calculation: count recent session days
        session_dates = set()
        for session in recent_sessions:
            session_dates.add(session.end_time.date())
        
        # Calculate consecutive days (simplified)
        streak = 0
        current_date = now.date()
        
        while current_date in session_dates:
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak


class MentorDashboardView(APIView):
    """
    API endpoint for mentor dashboard data
    GET /api/dashboard/mentor/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'mentor':
            return Response(
                {'error': 'Only mentors can access this endpoint'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        user = request.user
        
        # Mock data for mentor dashboard
        mock_data = {
            'stats': {
                'sessions_completed': 47,
                'total_students': 23,
                'average_rating': 4.8,
                'total_earnings': 2350
            },
            'upcoming_sessions': [
                {
                    'id': 1,
                    'learner_name': 'Alice Johnson',
                    'learner_avatar': 'AJ',
                    'topic': 'React Development',
                    'start_time': '2025-08-11T10:00:00Z',
                    'duration': 60,
                    'status': 'confirmed'
                },
                {
                    'id': 2,
                    'learner_name': 'Bob Smith',
                    'learner_avatar': 'BS',
                    'topic': 'Python Fundamentals',
                    'start_time': '2025-08-11T14:30:00Z',
                    'duration': 90,
                    'status': 'confirmed'
                },
                {
                    'id': 3,
                    'learner_name': 'Carol Davis',
                    'learner_avatar': 'CD',
                    'topic': 'Data Science',
                    'start_time': '2025-08-12T09:00:00Z',
                    'duration': 60,
                    'status': 'pending'
                }
            ],
            'recent_reviews': [
                {
                    'id': 1,
                    'learner_name': 'David Wilson',
                    'rating': 5,
                    'comment': 'Excellent mentor! Very patient and knowledgeable.',
                    'created_at': '2025-08-09T16:30:00Z'
                },
                {
                    'id': 2,
                    'learner_name': 'Emma Brown',
                    'rating': 5,
                    'comment': 'Great session, learned so much about React hooks!',
                    'created_at': '2025-08-08T11:15:00Z'
                },
                {
                    'id': 3,
                    'learner_name': 'Frank Miller',
                    'rating': 4,
                    'comment': 'Very helpful with debugging. Would book again.',
                    'created_at': '2025-08-07T15:45:00Z'
                }
            ],
            'earnings': {
                'monthly_earnings': 1200,
                'monthly_sessions': 24,
                'hourly_rate': 50
            }
        }

        return Response(mock_data)
