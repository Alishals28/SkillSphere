"""
Simple Badge Service

Service for awarding badges based on user accomplishments.
"""

from django.db.models import Count, Avg, Q
from .models import Badge, UserBadge


class BadgeService:
    """Simple service for checking and awarding badges"""
    
    @staticmethod
    def check_and_award_badges(user):
        """Check all badges and award any that the user has earned"""
        from bookings.models import Booking
        
        # Get user's stats
        total_sessions = Booking.objects.filter(
            Q(mentor=user) | Q(learner=user),
            status='completed'
        ).count()
        
        mentor_sessions = Booking.objects.filter(
            mentor=user, status='completed'
        ).count()
        
        learner_sessions = Booking.objects.filter(
            learner=user, status='completed'
        ).count()
        
        # Get all active badges user hasn't earned
        earned_badge_ids = UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
        available_badges = Badge.objects.filter(
            is_active=True
        ).exclude(id__in=earned_badge_ids)
        
        newly_awarded = []
        
        for badge in available_badges:
            earned = False
            
            # Check badge requirements
            if badge.requirement_type == 'first_session':
                earned = total_sessions >= 1
            
            elif badge.requirement_type == 'sessions_completed':
                earned = total_sessions >= badge.requirement_count
            
            elif badge.requirement_type == 'sessions_taught':
                earned = mentor_sessions >= badge.requirement_count
            
            elif badge.requirement_type == 'sessions_learned':
                earned = learner_sessions >= badge.requirement_count
            
            elif badge.requirement_type == 'high_rating':
                # Check average rating
                avg_rating = Booking.objects.filter(
                    mentor=user, 
                    status='completed',
                    learner_rating__isnull=False
                ).aggregate(avg=Avg('learner_rating'))['avg']
                earned = (avg_rating or 0) >= badge.requirement_count
            
            elif badge.requirement_type == 'reviews_written':
                review_count = Booking.objects.filter(
                    learner=user,
                    status='completed'
                ).exclude(learner_feedback='').count()
                earned = review_count >= badge.requirement_count
            
            # Award badge if earned
            if earned:
                user_badge = UserBadge.objects.create(
                    user=user,
                    badge=badge
                )
                newly_awarded.append(user_badge)
        
        return newly_awarded
    
    @staticmethod
    def get_user_badges(user):
        """Get all badges earned by a user"""
        return UserBadge.objects.filter(user=user).select_related('badge')
    
    @staticmethod
    def get_available_badges():
        """Get all available badges"""
        return Badge.objects.filter(is_active=True)
