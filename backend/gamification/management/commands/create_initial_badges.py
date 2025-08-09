"""
Management command to create initial simple badges.
"""

from django.core.management.base import BaseCommand
from gamification.models import Badge


class Command(BaseCommand):
    help = 'Create initial simple badges'
    
    def handle(self, *args, **options):
        badges_data = [
            # Learning badges
            {
                'name': 'First Steps',
                'description': 'Complete your first session',
                'category': 'learning',
                'icon': '🎯',
                'requirement_type': 'first_session',
                'requirement_count': 1,
            },
            {
                'name': 'Getting Started',
                'description': 'Complete 5 sessions',
                'category': 'learning',
                'icon': '📈',
                'requirement_type': 'sessions_completed',
                'requirement_count': 5,
            },
            {
                'name': 'Dedicated Learner',
                'description': 'Complete 25 sessions',
                'category': 'learning',
                'icon': '🎓',
                'requirement_type': 'sessions_completed',
                'requirement_count': 25,
            },
            
            # Teaching badges
            {
                'name': 'First Mentor',
                'description': 'Teach your first session',
                'category': 'teaching',
                'icon': '👨‍🏫',
                'requirement_type': 'sessions_taught',
                'requirement_count': 1,
            },
            {
                'name': 'Helpful Teacher',
                'description': 'Teach 10 sessions',
                'category': 'teaching',
                'icon': '🌟',
                'requirement_type': 'sessions_taught',
                'requirement_count': 10,
            },
            
            # Quality badges
            {
                'name': 'Highly Rated',
                'description': 'Maintain a 4.5+ star average rating',
                'category': 'quality',
                'icon': '⭐',
                'requirement_type': 'high_rating',
                'requirement_count': 4.5,
            },
            
            # Milestone badges
            {
                'name': 'Century Club',
                'description': 'Complete 100 total sessions',
                'category': 'milestones',
                'icon': '💯',
                'requirement_type': 'sessions_completed',
                'requirement_count': 100,
            },
            
            # Special badges
            {
                'name': 'Feedback Champion',
                'description': 'Write 10 session reviews',
                'category': 'special',
                'icon': '📝',
                'requirement_type': 'reviews_written',
                'requirement_count': 10,
            },
        ]
        
        created_count = 0
        for badge_data in badges_data:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created badge: {badge.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} new badges')
        )
