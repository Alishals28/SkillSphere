from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q, Avg, Count, Case, When, IntegerField
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
    Review, ReviewTag, ReviewHelpful, ReviewReport,
    ReviewResponse, MentorRating, SkillRating, ReviewTemplate
)
from .serializers import (
    ReviewSerializer, ReviewCreateSerializer, ReviewListSerializer,
    MentorRatingSerializer, ReviewTagSerializer, ReviewReportSerializer,
    ReviewResponseSerializer, ReviewTemplateSerializer, ReviewStatsSerializer,
    BulkReviewActionSerializer
)
from bookings.models import Booking
from .filters import ReviewFilter
from .permissions import CanReviewPermission, CanRespondToReviewPermission

User = get_user_model()


class ReviewViewSet(ModelViewSet):
    """
    ViewSet for managing reviews
    """
    queryset = Review.objects.filter(is_approved=True)
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['review_text', 'pros', 'cons']
    ordering_fields = ['created_at', 'overall_rating', 'helpful_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ReviewCreateSerializer
        elif self.action == 'list':
            return ReviewListSerializer
        return ReviewSerializer
    
    def get_queryset(self):
        """Filter queryset based on user and action"""
        queryset = self.queryset
        
        # Apply custom filters
        queryset = ReviewFilter.filter_queryset(self.request, queryset)
        
        if self.action == 'list':
            # Filter by reviewee if specified
            reviewee_id = self.request.query_params.get('reviewee')
            if reviewee_id:
                try:
                    queryset = queryset.filter(reviewee_id=int(reviewee_id))
                except ValueError:
                    pass
            
            # Filter by reviewer if specified (for user's own reviews)
            reviewer_id = self.request.query_params.get('reviewer')
            if reviewer_id:
                try:
                    queryset = queryset.filter(reviewer_id=int(reviewer_id))
                except ValueError:
                    pass
        
        return queryset
    
    def perform_create(self, serializer):
        """Create review with additional processing"""
        review = serializer.save()
        
        # Update mentor rating if this is a mentor review
        if review.review_type == 'mentor_review':
            mentor_rating, created = MentorRating.objects.get_or_create(
                mentor=review.reviewee
            )
            mentor_rating.update_ratings()
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_helpful(self, request, pk=None):
        """Mark a review as helpful"""
        review = self.get_object()
        user = request.user
        
        helpful_vote, created = ReviewHelpful.objects.get_or_create(
            review=review,
            user=user
        )
        
        if not created:
            # Toggle helpful vote
            helpful_vote.delete()
            review.helpful_count = max(0, review.helpful_count - 1)
            action = 'removed'
        else:
            review.helpful_count += 1
            action = 'added'
        
        review.save()
        
        return Response({
            'action': action,
            'helpful_count': review.helpful_count
        })
    
    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        """Report a review"""
        review = self.get_object()
        
        serializer = ReviewReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                review=review,
                reporter=request.user
            )
            
            # Increment report count
            review.reported_count += 1
            review.save()
            
            return Response({'message': 'Review reported successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[CanRespondToReviewPermission])
    def respond(self, request, pk=None):
        """Respond to a review"""
        review = self.get_object()
        
        # Check if response already exists
        if hasattr(review, 'response'):
            return Response(
                {'error': 'Response already exists for this review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReviewResponseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                review=review,
                responder=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MentorReviewsView(generics.ListAPIView):
    """
    Get reviews for a specific mentor
    GET /api/reviews/mentor/<mentor_id>/
    """
    serializer_class = ReviewListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'overall_rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        mentor_id = self.kwargs['mentor_id']
        return Review.objects.filter(
            reviewee_id=mentor_id,
            review_type='mentor_review',
            is_approved=True
        )


class MentorRatingView(generics.RetrieveAPIView):
    """
    Get aggregated rating for a mentor
    GET /api/reviews/mentor/<mentor_id>/rating/
    """
    serializer_class = MentorRatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_object(self):
        mentor_id = self.kwargs['mentor_id']
        mentor = get_object_or_404(User, id=mentor_id, role='mentor')
        rating, created = MentorRating.objects.get_or_create(mentor=mentor)
        if created:
            rating.update_ratings()
        return rating


class UserReviewsView(generics.ListAPIView):
    """
    Get reviews given or received by current user
    GET /api/reviews/my-reviews/?type=given|received
    """
    serializer_class = ReviewListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        review_type = self.request.query_params.get('type', 'received')
        
        if review_type == 'given':
            return Review.objects.filter(reviewer=user)
        else:
            return Review.objects.filter(reviewee=user, is_approved=True)


class ReviewableBookingsView(generics.ListAPIView):
    """
    Get bookings that can be reviewed by current user
    GET /api/reviews/reviewable-bookings/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get completed bookings where user hasn't reviewed yet
        if user.role == 'learner':
            bookings = Booking.objects.filter(
                learner=user,
                status='completed'
            ).exclude(
                reviews__reviewer=user,
                reviews__review_type='mentor_review'
            )
            review_type = 'mentor_review'
        elif user.role == 'mentor':
            bookings = Booking.objects.filter(
                mentor=user,
                status='completed'
            ).exclude(
                reviews__reviewer=user,
                reviews__review_type='learner_review'
            )
            review_type = 'learner_review'
        else:
            bookings = Booking.objects.none()
            review_type = None
        
        booking_data = []
        for booking in bookings:
            other_user = booking.mentor if user.role == 'learner' else booking.learner
            booking_data.append({
                'id': booking.id,
                'subject': booking.subject,
                'other_user': {
                    'id': other_user.id,
                    'name': other_user.full_name,
                    'profile_picture': other_user.profile_picture.url if other_user.profile_picture else None
                },
                'session_date': booking.confirmed_start_utc,
                'duration': booking.duration_minutes,
                'review_type': review_type
            })
        
        return Response({
            'reviewable_bookings': booking_data,
            'count': len(booking_data)
        })


class ReviewTagsView(generics.ListAPIView):
    """
    Get available review tags
    GET /api/reviews/tags/
    """
    queryset = ReviewTag.objects.filter(is_active=True)
    serializer_class = ReviewTagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ReviewTemplatesView(generics.ListAPIView):
    """
    Get review templates
    GET /api/reviews/templates/?review_type=mentor_review
    """
    queryset = ReviewTemplate.objects.filter(is_active=True)
    serializer_class = ReviewTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        review_type = self.request.query_params.get('review_type')
        if review_type:
            queryset = queryset.filter(review_type=review_type)
        return queryset


class ReviewStatsView(APIView):
    """
    Get review statistics for a user
    GET /api/reviews/stats/?user_id=123
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get reviews received by this user
        reviews = Review.objects.filter(
            reviewee=user,
            is_approved=True
        )
        
        if not reviews.exists():
            return Response({
                'total_reviews': 0,
                'average_rating': 0,
                'rating_distribution': {
                    '5': 0, '4': 0, '3': 0, '2': 0, '1': 0
                },
                'recent_reviews_count': 0,
                'recommendation_rate': 0
            })
        
        # Calculate statistics
        stats = reviews.aggregate(
            total_reviews=Count('id'),
            average_rating=Avg('overall_rating'),
            five_stars=Count(Case(When(overall_rating=5, then=1), output_field=IntegerField())),
            four_stars=Count(Case(When(overall_rating=4, then=1), output_field=IntegerField())),
            three_stars=Count(Case(When(overall_rating=3, then=1), output_field=IntegerField())),
            two_stars=Count(Case(When(overall_rating=2, then=1), output_field=IntegerField())),
            one_star=Count(Case(When(overall_rating=1, then=1), output_field=IntegerField())),
            recommendations=Count(Case(When(would_recommend=True, then=1), output_field=IntegerField()))
        )
        
        # Recent reviews (last 30 days)
        from django.utils import timezone
        from datetime import timedelta
        recent_count = reviews.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        return Response({
            'total_reviews': stats['total_reviews'],
            'average_rating': round(stats['average_rating'], 2) if stats['average_rating'] else 0,
            'rating_distribution': {
                '5': stats['five_stars'],
                '4': stats['four_stars'],
                '3': stats['three_stars'],
                '2': stats['two_stars'],
                '1': stats['one_star']
            },
            'recent_reviews_count': recent_count,
            'recommendation_rate': round(
                (stats['recommendations'] / stats['total_reviews']) * 100, 1
            ) if stats['total_reviews'] > 0 else 0
        })


# Admin views for review management
class AdminReviewListView(generics.ListAPIView):
    """
    Admin view for managing all reviews
    GET /api/reviews/admin/reviews/
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['review_text', 'reviewer__email', 'reviewee__email']
    ordering_fields = ['created_at', 'overall_rating', 'reported_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Apply custom filters"""
        queryset = super().get_queryset()
        return ReviewFilter.filter_queryset(self.request, queryset)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def bulk_review_action(request):
    """
    Bulk actions on reviews
    POST /api/reviews/admin/bulk-action/
    """
    serializer = BulkReviewActionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    review_ids = serializer.validated_data['review_ids']
    action = serializer.validated_data['action']
    notes = serializer.validated_data.get('notes', '')
    
    reviews = Review.objects.filter(id__in=review_ids)
    
    if action == 'approve':
        reviews.update(is_approved=True, moderation_notes=notes)
    elif action == 'reject':
        reviews.update(is_approved=False, moderation_notes=notes)
    elif action == 'feature':
        reviews.update(is_featured=True)
    elif action == 'unfeature':
        reviews.update(is_featured=False)
    elif action == 'delete':
        reviews.delete()
        return Response({'message': f'Deleted {len(review_ids)} reviews'})
    
    return Response({'message': f'Applied {action} to {reviews.count()} reviews'})


class ReviewReportsView(generics.ListAPIView):
    """
    View reported reviews
    GET /api/reviews/admin/reports/
    """
    queryset = ReviewReport.objects.filter(is_resolved=False)
    serializer_class = ReviewReportSerializer
    permission_classes = [permissions.IsAdminUser]
    ordering = ['-created_at']


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def resolve_review_report(request, report_id):
    """
    Resolve a review report
    POST /api/reviews/admin/reports/<report_id>/resolve/
    """
    try:
        report = ReviewReport.objects.get(id=report_id)
    except ReviewReport.DoesNotExist:
        return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
    
    resolution_notes = request.data.get('resolution_notes', '')
    
    report.is_resolved = True
    report.resolution_notes = resolution_notes
    report.resolved_by = request.user
    report.resolved_at = timezone.now()
    report.save()
    
    return Response({'message': 'Report resolved successfully'})
