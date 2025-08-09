from rest_framework import permissions
from .models import Review


class CanReviewPermission(permissions.BasePermission):
    """
    Permission to check if user can create a review
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if view.action != 'create':
            return True
        
        # Check if user is involved in the booking
        booking_id = request.data.get('booking')
        if booking_id:
            try:
                from bookings.models import Booking
                booking = Booking.objects.get(id=booking_id)
                return request.user in [booking.learner, booking.mentor]
            except Booking.DoesNotExist:
                return False
        
        return True


class CanRespondToReviewPermission(permissions.BasePermission):
    """
    Permission to check if user can respond to a review
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Only the reviewee can respond to their review
        return request.user == obj.reviewee


class CanEditReviewPermission(permissions.BasePermission):
    """
    Permission to check if user can edit a review
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Only the reviewer can edit their review
        if request.user == obj.reviewer:
            return True
        
        # Admins can edit any review
        if request.user.is_staff:
            return True
        
        return False


class CanDeleteReviewPermission(permissions.BasePermission):
    """
    Permission to check if user can delete a review
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Only the reviewer can delete their review (within time limit)
        if request.user == obj.reviewer:
            from django.utils import timezone
            from datetime import timedelta
            
            # Allow deletion within 24 hours of creation
            time_limit = timezone.now() - timedelta(hours=24)
            return obj.created_at > time_limit
        
        # Admins can delete any review
        if request.user.is_staff:
            return True
        
        return False
