from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.utils import timezone
from datetime import timedelta


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
        
        # For now, return mock data that matches the frontend expectations
        # In production, this would query real models
        
        # Basic user stats (start with realistic but low numbers for new users)
        stats = {
            'sessions_completed': 2,
            'badges_earned': 1,
            'hours_learned': 3,
            'streak_days': 2
        }
        
        # Sample upcoming sessions
        upcoming_sessions = [
            {
                'id': 1,
                'mentor_name': 'Dr. Sarah Johnson',
                'mentor_avatar': 'SJ',
                'topic': 'Python Fundamentals',
                'start_time': (timezone.now() + timedelta(days=1)).isoformat(),
                'duration': 60,
                'status': 'confirmed'
            },
            {
                'id': 2,
                'mentor_name': 'Alex Chen',
                'mentor_avatar': 'AC',
                'topic': 'Web Development Basics',
                'start_time': (timezone.now() + timedelta(days=3)).isoformat(),
                'duration': 90,
                'status': 'pending'
            }
        ]
        
        # Sample recommended mentors
        recommended_mentors = [
            {
                'id': 1,
                'name': 'Emily Rodriguez',
                'avatar': 'ER',
                'specialty': 'Full Stack Development',
                'rating': 4.9,
                'session_count': 156
            },
            {
                'id': 2,
                'name': 'Michael Davis',
                'avatar': 'MD',
                'specialty': 'Data Science & ML',
                'rating': 4.8,
                'session_count': 203
            },
            {
                'id': 3,
                'name': 'Lisa Thompson',
                'avatar': 'LT',
                'specialty': 'UI/UX Design',
                'rating': 4.9,
                'session_count': 89
            }
        ]
        
        # Sample recent activity
        recent_activity = [
            {
                'type': 'session',
                'icon': '📚',
                'text': 'Completed session with Dr. Sarah Johnson',
                'time': (timezone.now() - timedelta(hours=5)).isoformat()
            },
            {
                'type': 'badge',
                'icon': '🏆',
                'text': 'Earned "First Steps" badge',
                'time': (timezone.now() - timedelta(days=1)).isoformat()
            },
            {
                'type': 'session',
                'icon': '📚',
                'text': 'Booked session with Alex Chen',
                'time': (timezone.now() - timedelta(days=2)).isoformat()
            }
        ]
        
        # Progress data
        progress = {
            'monthly_goal_progress': 25,  # 25% towards monthly goal
            'monthly_sessions': 2,
            'monthly_goal': 8
        }

        return Response({
            'stats': stats,
            'upcoming_sessions': upcoming_sessions,
            'recommended_mentors': recommended_mentors,
            'recent_activity': recent_activity,
            'progress': progress
        })


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
        stats = {
            'sessions_completed': 47,
            'total_students': 23,
            'average_rating': 4.8,
            'total_earnings': 2350
        }
        
        upcoming_sessions = [
            {
                'id': 1,
                'learner_name': 'John Smith',
                'learner_avatar': 'JS',
                'topic': 'Python Fundamentals',
                'start_time': (timezone.now() + timedelta(hours=2)).isoformat(),
                'duration': 60,
                'status': 'confirmed'
            }
        ]
        
        recent_reviews = [
            {
                'id': 1,
                'learner_name': 'Jane Doe',
                'rating': 5,
                'comment': 'Excellent mentor! Very helpful and patient.',
                'created_at': (timezone.now() - timedelta(days=1)).isoformat()
            }
        ]
        
        earnings = {
            'monthly_earnings': 890,
            'monthly_sessions': 18,
            'hourly_rate': 50
        }

        return Response({
            'stats': stats,
            'upcoming_sessions': upcoming_sessions,
            'recent_reviews': recent_reviews,
            'earnings': earnings
        })
