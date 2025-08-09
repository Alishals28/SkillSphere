"""
Simple Badge Views

Simple API endpoints for badge functionality.
"""

from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Badge, UserBadge
from .serializers import BadgeSerializer, UserBadgeSerializer
from .services import BadgeService


class UserBadgesView(generics.ListAPIView):
    """List badges earned by the authenticated user"""
    serializer_class = UserBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user).select_related('badge')


class BadgeListView(generics.ListAPIView):
    """List all available badges"""
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Badge.objects.filter(is_active=True)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def check_badges(request):
    """Check and award any new badges for the user"""
    newly_awarded = BadgeService.check_and_award_badges(request.user)
    
    return Response({
        'message': f'{len(newly_awarded)} new badges awarded',
        'new_badges': UserBadgeSerializer(newly_awarded, many=True).data
    })
