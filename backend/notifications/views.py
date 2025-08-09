from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Notification, NotificationPreference
from .serializers import (
    NotificationSerializer,
    NotificationCreateSerializer,
    NotificationPreferenceSerializer,
    NotificationBulkActionSerializer
)


class NotificationListView(generics.ListAPIView):
    """
    List user's notifications
    GET /api/notifications/
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user)
        
        # Filter by read status
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        # Filter by type
        notification_type = self.request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(type=notification_type)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Exclude archived unless specifically requested
        include_archived = self.request.query_params.get('include_archived', 'false')
        if include_archived.lower() != 'true':
            queryset = queryset.filter(is_archived=False)
        
        # Exclude expired unless specifically requested
        include_expired = self.request.query_params.get('include_expired', 'false')
        if include_expired.lower() != 'true':
            queryset = queryset.filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
            )
        
        return queryset.order_by('-created_at')


class NotificationDetailView(generics.RetrieveUpdateAPIView):
    """
    Get or update a specific notification
    GET/PATCH /api/notifications/{id}/
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """Mark notification as read when viewed"""
        notification = self.get_object()
        if not notification.is_read:
            notification.mark_as_read()
        return super().retrieve(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """
    Mark a specific notification as read
    POST /api/notifications/{id}/mark-read/
    """
    notification = get_object_or_404(
        Notification, 
        id=notification_id, 
        user=request.user
    )
    
    notification.mark_as_read()
    
    return Response({
        'message': 'Notification marked as read'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """
    Mark all notifications as read for current user
    POST /api/notifications/mark-all-read/
    """
    updated_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True, read_at=timezone.now())
    
    return Response({
        'message': f'{updated_count} notifications marked as read'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_notification_action(request):
    """
    Perform bulk actions on notifications
    POST /api/notifications/bulk-action/
    """
    serializer = NotificationBulkActionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    notification_ids = serializer.validated_data['notification_ids']
    action = serializer.validated_data['action']
    
    # Get notifications belonging to current user
    notifications = Notification.objects.filter(
        id__in=notification_ids,
        user=request.user
    )
    
    if action == 'mark_read':
        updated_count = notifications.update(is_read=True, read_at=timezone.now())
    elif action == 'mark_unread':
        updated_count = notifications.update(is_read=False, read_at=None)
    elif action == 'archive':
        updated_count = notifications.update(is_archived=True)
    elif action == 'delete':
        updated_count = notifications.count()
        notifications.delete()
    
    return Response({
        'message': f'{updated_count} notifications {action}ed successfully'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_stats(request):
    """
    Get notification statistics for current user
    GET /api/notifications/stats/
    """
    user = request.user
    
    total = Notification.objects.filter(user=user).count()
    unread = Notification.objects.filter(user=user, is_read=False).count()
    urgent = Notification.objects.filter(
        user=user, 
        priority__in=['high', 'urgent'],
        is_read=False
    ).count()
    
    # Count by type
    by_type = {}
    for notification_type, _ in Notification.TYPE_CHOICES:
        count = Notification.objects.filter(
            user=user,
            type=notification_type,
            is_read=False
        ).count()
        if count > 0:
            by_type[notification_type] = count
    
    return Response({
        'total': total,
        'unread': unread,
        'urgent': urgent,
        'by_type': by_type
    })


class NotificationPreferenceView(APIView):
    """
    Get or update notification preferences
    GET/PATCH /api/notifications/preferences/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        preferences, created = NotificationPreference.objects.get_or_create(
            user=request.user
        )
        serializer = NotificationPreferenceSerializer(preferences)
        return Response(serializer.data)
    
    def patch(self, request):
        preferences, created = NotificationPreference.objects.get_or_create(
            user=request.user
        )
        serializer = NotificationPreferenceSerializer(
            preferences, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Admin notification creation view
class CreateNotificationView(generics.CreateAPIView):
    """
    Create a notification (Admin only)
    POST /api/admin/notifications/
    """
    serializer_class = NotificationCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def perform_create(self, serializer):
        # For admin-created notifications, can specify user in payload
        user_id = self.request.data.get('user_id')
        if user_id:
            from users.models import User
            user = get_object_or_404(User, id=user_id)
            serializer.save(user=user)
        else:
            serializer.save(user=self.request.user)
