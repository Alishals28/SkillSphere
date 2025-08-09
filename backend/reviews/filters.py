from django.db.models import Q
from .models import Review, ReviewTag


class ReviewFilter:
    """
    Simple filter for reviews without django_filters dependency
    """
    
    @staticmethod
    def filter_queryset(request, queryset):
        """Apply filters based on query parameters"""
        
        # Rating filters
        min_rating = request.GET.get('min_rating')
        if min_rating:
            try:
                queryset = queryset.filter(overall_rating__gte=int(min_rating))
            except ValueError:
                pass
        
        max_rating = request.GET.get('max_rating')
        if max_rating:
            try:
                queryset = queryset.filter(overall_rating__lte=int(max_rating))
            except ValueError:
                pass
        
        rating = request.GET.get('rating')
        if rating:
            try:
                queryset = queryset.filter(overall_rating=int(rating))
            except ValueError:
                pass
        
        # User filters
        reviewer = request.GET.get('reviewer')
        if reviewer:
            try:
                queryset = queryset.filter(reviewer__id=int(reviewer))
            except ValueError:
                pass
        
        reviewee = request.GET.get('reviewee')
        if reviewee:
            try:
                queryset = queryset.filter(reviewee__id=int(reviewee))
            except ValueError:
                pass
        
        # Type filters
        review_type = request.GET.get('review_type')
        if review_type:
            queryset = queryset.filter(review_type=review_type)
        
        # Boolean filters
        has_response = request.GET.get('has_response')
        if has_response:
            if has_response.lower() == 'true':
                queryset = queryset.filter(response__isnull=False)
            elif has_response.lower() == 'false':
                queryset = queryset.filter(response__isnull=True)
        
        is_featured = request.GET.get('is_featured')
        if is_featured:
            queryset = queryset.filter(is_featured=is_featured.lower() == 'true')
        
        would_recommend = request.GET.get('would_recommend')
        if would_recommend:
            queryset = queryset.filter(would_recommend=would_recommend.lower() == 'true')
        
        # Skill filter (from booking)
        skill = request.GET.get('skill')
        if skill:
            try:
                queryset = queryset.filter(booking__primary_skill__id=int(skill))
            except ValueError:
                pass
        
        # Text search
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(review_text__icontains=search) |
                Q(pros__icontains=search) |
                Q(cons__icontains=search)
            )
        
        return queryset
