from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Avg, Count, F, Value, CharField
from django.db.models.functions import Concat
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.utils import timezone
from datetime import timedelta
import re

from users.models import User
from users.serializers import PublicMentorProfileSerializer, DetailedMentorProfileSerializer
from skills.models import Skill, SkillCategory, MentorSkill
from bookings.models import Booking
from availability.models import AvailabilitySlot


class AdvancedMentorSearchView(APIView):
    """
    Advanced mentor search with filtering, sorting, and ranking
    GET /api/search/mentors/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get query parameters
        search_query = request.GET.get('q', '').strip()
        skills = request.GET.get('skills', '').strip()
        categories = request.GET.get('categories', '').strip()
        min_rating = request.GET.get('min_rating')
        max_rating = request.GET.get('max_rating')
        min_rate = request.GET.get('min_rate')
        max_rate = request.GET.get('max_rate')
        country = request.GET.get('country', '').strip()
        timezone_filter = request.GET.get('timezone', '').strip()
        experience_level = request.GET.get('experience_level', '').strip()
        availability_filter = request.GET.get('availability')
        sort_by = request.GET.get('sort_by', 'relevance')
        page_size = int(request.GET.get('page_size', 20))
        page = int(request.GET.get('page', 1))
        
        # Start with base queryset
        queryset = User.objects.filter(
            role='mentor',
            is_mentor_approved=True,
            is_available=True
        ).select_related().prefetch_related(
            'mentor_skills__skill',
            'mentor_skills__skill__category'
        )
        
        # Apply text search
        if search_query:
            queryset = self._apply_text_search(queryset, search_query)
        
        # Apply skill filters
        if skills:
            queryset = self._apply_skill_filters(queryset, skills)
        
        # Apply category filters
        if categories:
            queryset = self._apply_category_filters(queryset, categories)
        
        # Apply rating filters
        if min_rating or max_rating:
            queryset = self._apply_rating_filters(queryset, min_rating, max_rating)
        
        # Apply rate filters
        if min_rate or max_rate:
            queryset = self._apply_rate_filters(queryset, min_rate, max_rate)
        
        # Apply location filters
        if country:
            queryset = queryset.filter(country__icontains=country)
        
        if timezone_filter:
            queryset = queryset.filter(timezone__icontains=timezone_filter)
        
        # Apply experience level filter
        if experience_level:
            queryset = self._apply_experience_filter(queryset, experience_level)
        
        # Apply availability filter
        if availability_filter:
            queryset = self._apply_availability_filter(queryset, availability_filter)
        
        # Apply sorting
        queryset = self._apply_sorting(queryset, sort_by, search_query)
        
        # Calculate total before pagination
        total_count = queryset.count()
        
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        mentors = queryset[start:end]
        
        # Serialize results
        serializer = PublicMentorProfileSerializer(mentors, many=True)
        
        # Prepare response
        return Response({
            'results': serializer.data,
            'pagination': {
                'total': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size
            },
            'filters_applied': {
                'search_query': search_query,
                'skills': skills,
                'categories': categories,
                'min_rating': min_rating,
                'max_rating': max_rating,
                'min_rate': min_rate,
                'max_rate': max_rate,
                'country': country,
                'timezone': timezone_filter,
                'experience_level': experience_level,
                'availability': availability_filter,
                'sort_by': sort_by
            }
        })
    
    def _apply_text_search(self, queryset, search_query):
        """Apply full-text search across mentor profiles"""
        # Create search vectors for different fields with different weights
        search_vector = (
            SearchVector('first_name', weight='A') +
            SearchVector('last_name', weight='A') +
            SearchVector('mentor_bio', weight='B') +
            SearchVector('bio', weight='B') +
            SearchVector('teaching_experience', weight='C') +
            SearchVector('mentor_skills__skill__name', weight='A')
        )
        
        search_query_obj = SearchQuery(search_query)
        
        return queryset.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query_obj)
        ).filter(search=search_query_obj)
    
    def _apply_skill_filters(self, queryset, skills):
        """Filter by specific skills"""
        skill_list = [s.strip() for s in skills.split(',') if s.strip()]
        
        # Handle both skill names and IDs
        skill_conditions = Q()
        for skill in skill_list:
            if skill.isdigit():
                skill_conditions |= Q(mentor_skills__skill__id=int(skill))
            else:
                skill_conditions |= Q(mentor_skills__skill__name__icontains=skill)
        
        return queryset.filter(skill_conditions).distinct()
    
    def _apply_category_filters(self, queryset, categories):
        """Filter by skill categories"""
        category_list = [c.strip() for c in categories.split(',') if c.strip()]
        
        category_conditions = Q()
        for category in category_list:
            if category.isdigit():
                category_conditions |= Q(mentor_skills__skill__category__id=int(category))
            else:
                category_conditions |= Q(mentor_skills__skill__category__name__icontains=category)
        
        return queryset.filter(category_conditions).distinct()
    
    def _apply_rating_filters(self, queryset, min_rating, max_rating):
        """Filter by average rating"""
        # Annotate with average rating
        queryset = queryset.annotate(
            avg_rating=Avg(
                'mentor_bookings__learner_rating',
                filter=Q(mentor_bookings__status='completed')
            )
        )
        
        if min_rating:
            queryset = queryset.filter(avg_rating__gte=float(min_rating))
        
        if max_rating:
            queryset = queryset.filter(avg_rating__lte=float(max_rating))
        
        return queryset
    
    def _apply_rate_filters(self, queryset, min_rate, max_rate):
        """Filter by hourly rate"""
        if min_rate:
            queryset = queryset.filter(hourly_rate__gte=float(min_rate))
        
        if max_rate:
            queryset = queryset.filter(hourly_rate__lte=float(max_rate))
        
        return queryset
    
    def _apply_experience_filter(self, queryset, experience_level):
        """Filter by experience level"""
        # Map experience levels to years of experience
        experience_mapping = {
            'beginner': (0, 2),
            'intermediate': (2, 5),
            'advanced': (5, 100)
        }
        
        if experience_level.lower() in experience_mapping:
            min_years, max_years = experience_mapping[experience_level.lower()]
            queryset = queryset.filter(
                mentor_skills__years_experience__gte=min_years,
                mentor_skills__years_experience__lt=max_years
            ).distinct()
        
        return queryset
    
    def _apply_availability_filter(self, queryset, availability_filter):
        """Filter by availability"""
        now = timezone.now()
        
        if availability_filter == 'now':
            # Available within the next hour
            end_time = now + timedelta(hours=1)
            available_mentors = AvailabilitySlot.objects.filter(
                start_utc__lte=end_time,
                end_utc__gt=now,
                is_booked=False,
                is_blocked=False
            ).values_list('mentor_id', flat=True)
            
        elif availability_filter == 'today':
            # Available today
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            available_mentors = AvailabilitySlot.objects.filter(
                start_utc__gte=start_of_day,
                start_utc__lt=end_of_day,
                is_booked=False,
                is_blocked=False
            ).values_list('mentor_id', flat=True)
            
        elif availability_filter == 'week':
            # Available this week
            end_of_week = now + timedelta(days=7)
            available_mentors = AvailabilitySlot.objects.filter(
                start_utc__gte=now,
                start_utc__lt=end_of_week,
                is_booked=False,
                is_blocked=False
            ).values_list('mentor_id', flat=True)
        else:
            return queryset
        
        return queryset.filter(id__in=available_mentors)
    
    def _apply_sorting(self, queryset, sort_by, search_query):
        """Apply sorting to queryset"""
        if sort_by == 'relevance' and search_query:
            # Use search rank for relevance
            return queryset.order_by('-rank', '-id')
        
        elif sort_by == 'rating':
            # Sort by average rating (high to low)
            if not hasattr(queryset.model, 'avg_rating'):
                queryset = queryset.annotate(
                    avg_rating=Avg(
                        'mentor_bookings__learner_rating',
                        filter=Q(mentor_bookings__status='completed')
                    )
                )
            return queryset.order_by('-avg_rating', '-id')
        
        elif sort_by == 'rate_low':
            return queryset.order_by('hourly_rate', 'id')
        
        elif sort_by == 'rate_high':
            return queryset.order_by('-hourly_rate', 'id')
        
        elif sort_by == 'sessions':
            # Sort by total completed sessions
            queryset = queryset.annotate(
                total_sessions=Count(
                    'mentor_bookings',
                    filter=Q(mentor_bookings__status='completed')
                )
            )
            return queryset.order_by('-total_sessions', '-id')
        
        elif sort_by == 'newest':
            return queryset.order_by('-created_at', '-id')
        
        elif sort_by == 'availability':
            # Sort by number of available slots
            queryset = queryset.annotate(
                available_slots=Count(
                    'availability_slots',
                    filter=Q(
                        availability_slots__start_utc__gt=timezone.now(),
                        availability_slots__is_booked=False,
                        availability_slots__is_blocked=False
                    )
                )
            )
            return queryset.order_by('-available_slots', '-id')
        
        else:
            # Default sorting
            return queryset.order_by('-created_at', '-id')


class GlobalSearchView(APIView):
    """
    Global search across all content types
    GET /api/search/global/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        search_type = request.GET.get('type', 'all')  # mentors, skills, all
        limit = int(request.GET.get('limit', 10))
        
        if not query:
            return Response({
                'results': {
                    'mentors': [],
                    'skills': [],
                    'categories': []
                },
                'total': 0
            })
        
        results = {}
        total = 0
        
        # Search mentors
        if search_type in ['all', 'mentors']:
            mentors = self._search_mentors(query, limit)
            results['mentors'] = mentors
            total += len(mentors)
        
        # Search skills
        if search_type in ['all', 'skills']:
            skills = self._search_skills(query, limit)
            results['skills'] = skills
            total += len(skills)
        
        # Search categories
        if search_type in ['all', 'categories']:
            categories = self._search_categories(query, limit)
            results['categories'] = categories
            total += len(categories)
        
        return Response({
            'results': results,
            'total': total,
            'query': query
        })
    
    def _search_mentors(self, query, limit):
        """Search mentors by name and bio"""
        mentors = User.objects.filter(
            role='mentor',
            is_mentor_approved=True
        ).filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(mentor_bio__icontains=query) |
            Q(bio__icontains=query)
        )[:limit]
        
        return [{
            'id': mentor.id,
            'name': mentor.full_name,
            'bio': mentor.mentor_bio[:100] + '...' if len(mentor.mentor_bio) > 100 else mentor.mentor_bio,
            'profile_picture': mentor.profile_picture.url if mentor.profile_picture else None,
            'rating': 0,  # Would calculate from bookings
            'type': 'mentor'
        } for mentor in mentors]
    
    def _search_skills(self, query, limit):
        """Search skills by name and description"""
        skills = Skill.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )[:limit]
        
        return [{
            'id': skill.id,
            'name': skill.name,
            'description': skill.description[:100] + '...' if len(skill.description) > 100 else skill.description,
            'category': skill.category.name if skill.category else None,
            'mentor_count': skill.mentor_skills.count(),
            'type': 'skill'
        } for skill in skills]
    
    def _search_categories(self, query, limit):
        """Search skill categories"""
        categories = SkillCategory.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )[:limit]
        
        return [{
            'id': category.id,
            'name': category.name,
            'description': category.description[:100] + '...' if len(category.description) > 100 else category.description,
            'skill_count': category.skills.count(),
            'type': 'category'
        } for category in categories]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_suggestions(request):
    """
    Get search suggestions/autocomplete
    GET /api/search/suggestions/?q=python
    """
    query = request.GET.get('q', '').strip()
    suggestion_type = request.GET.get('type', 'all')
    limit = int(request.GET.get('limit', 10))
    
    if not query or len(query) < 2:
        return Response({'suggestions': []})
    
    suggestions = []
    
    # Skill suggestions
    if suggestion_type in ['all', 'skills']:
        skills = Skill.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:limit//2]
        
        for skill in skills:
            suggestions.append({
                'text': skill,
                'type': 'skill',
                'category': 'Skills'
            })
    
    # Mentor name suggestions
    if suggestion_type in ['all', 'mentors']:
        mentors = User.objects.filter(
            role='mentor',
            is_mentor_approved=True
        ).filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).values_list('first_name', 'last_name')[:limit//2]
        
        for first_name, last_name in mentors:
            full_name = f"{first_name} {last_name}".strip()
            suggestions.append({
                'text': full_name,
                'type': 'mentor',
                'category': 'Mentors'
            })
    
    # Category suggestions
    if suggestion_type in ['all', 'categories']:
        categories = SkillCategory.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:limit//3]
        
        for category in categories:
            suggestions.append({
                'text': category,
                'type': 'category',
                'category': 'Categories'
            })
    
    return Response({
        'suggestions': suggestions[:limit],
        'query': query
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_filters(request):
    """
    Get available search filters and their options
    GET /api/search/filters/
    """
    return Response({
        'skills': [{
            'id': skill.id,
            'name': skill.name,
            'category': skill.category.name if skill.category else None
        } for skill in Skill.objects.select_related('category').all()],
        
        'categories': [{
            'id': category.id,
            'name': category.name,
            'skill_count': category.skills.count()
        } for category in SkillCategory.objects.annotate(
            skill_count=Count('skills')
        ).all()],
        
        'countries': list(
            User.objects.filter(
                role='mentor',
                is_mentor_approved=True,
                country__isnull=False
            ).exclude(country='').values_list('country', flat=True).distinct()
        ),
        
        'timezones': list(
            User.objects.filter(
                role='mentor',
                is_mentor_approved=True
            ).values_list('timezone', flat=True).distinct()
        ),
        
        'rating_ranges': [
            {'label': '4+ stars', 'min': 4, 'max': 5},
            {'label': '3+ stars', 'min': 3, 'max': 5},
            {'label': '2+ stars', 'min': 2, 'max': 5},
            {'label': 'Any rating', 'min': 0, 'max': 5}
        ],
        
        'rate_ranges': [
            {'label': 'Under $25/hr', 'min': 0, 'max': 25},
            {'label': '$25-50/hr', 'min': 25, 'max': 50},
            {'label': '$50-100/hr', 'min': 50, 'max': 100},
            {'label': '$100+/hr', 'min': 100, 'max': 1000}
        ],
        
        'experience_levels': [
            {'value': 'beginner', 'label': 'Beginner (0-2 years)'},
            {'value': 'intermediate', 'label': 'Intermediate (2-5 years)'},
            {'value': 'advanced', 'label': 'Advanced (5+ years)'}
        ],
        
        'availability_options': [
            {'value': 'now', 'label': 'Available now'},
            {'value': 'today', 'label': 'Available today'},
            {'value': 'week', 'label': 'Available this week'}
        ],
        
        'sort_options': [
            {'value': 'relevance', 'label': 'Most relevant'},
            {'value': 'rating', 'label': 'Highest rated'},
            {'value': 'rate_low', 'label': 'Price: Low to High'},
            {'value': 'rate_high', 'label': 'Price: High to Low'},
            {'value': 'sessions', 'label': 'Most experienced'},
            {'value': 'newest', 'label': 'Newest mentors'},
            {'value': 'availability', 'label': 'Most available'}
        ]
    })
