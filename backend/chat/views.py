from django.shortcuts import render

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from .models import (
    ChatRoom, ChatRoomParticipant, Message, MessageReaction,
    MessageReadStatus, ChatSettings
)
from .serializers import (
    ChatRoomListSerializer, ChatRoomDetailSerializer, ChatRoomCreateSerializer,
    MessageSerializer, MessageCreateSerializer, MessageUpdateSerializer,
    MessageReactionSerializer, ChatSettingsSerializer,
    TypingIndicatorSerializer, MessageReadStatusSerializer,
    ChatRoomParticipantSerializer
)


class MessagePagination(PageNumberPagination):
    """Custom pagination for messages"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class ChatRoomListView(generics.ListCreateAPIView):
    """List and create chat rooms"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ChatRoomCreateSerializer
        return ChatRoomListSerializer
    
    def get_queryset(self):
        """Get chat rooms where user is a participant"""
        return ChatRoom.objects.filter(
            participants=self.request.user,
            is_active=True
        ).select_related().prefetch_related(
            'participants',
            'participants_info__user',
            Prefetch('messages', queryset=Message.objects.select_related('sender').order_by('-created_at')[:1])
        ).order_by('-updated_at')


class ChatRoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a chat room"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatRoomDetailSerializer
    
    def get_queryset(self):
        """Get chat rooms where user is a participant"""
        return ChatRoom.objects.filter(
            participants=self.request.user
        ).select_related().prefetch_related(
            'participants_info__user',
            'messages__sender'
        )
    
    def perform_destroy(self, instance):
        """Soft delete chat room (mark as inactive)"""
        instance.is_active = False
        instance.save()


class ChatRoomMessagesView(generics.ListCreateAPIView):
    """List and create messages in a chat room"""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessagePagination
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MessageCreateSerializer
        return MessageSerializer
    
    def get_queryset(self):
        """Get messages for a specific chat room"""
        chat_room_id = self.kwargs['chat_room_id']
        
        # Verify user has access to this chat room
        chat_room = get_object_or_404(
            ChatRoom,
            id=chat_room_id,
            participants=self.request.user
        )
        
        return Message.objects.filter(
            chat_room=chat_room,
            is_deleted=False
        ).select_related(
            'sender', 'parent_message'
        ).prefetch_related(
            'reactions__user',
            'read_status'
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create message and mark room as updated"""
        message = serializer.save()
        
        # Update chat room timestamp
        message.chat_room.updated_at = timezone.now()
        message.chat_room.save(update_fields=['updated_at'])
        
        # Mark message as read for sender
        MessageReadStatus.objects.get_or_create(
            message=message,
            user=self.request.user
        )


class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific message"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return MessageUpdateSerializer
        return MessageSerializer
    
    def get_queryset(self):
        """Get messages where user has access"""
        return Message.objects.filter(
            chat_room__participants=self.request.user
        ).select_related('sender', 'chat_room').prefetch_related(
            'reactions__user'
        )
    
    def perform_update(self, serializer):
        """Only allow sender to update their own messages"""
        message = self.get_object()
        if message.sender != self.request.user:
            raise PermissionDenied("You can only edit your own messages.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Soft delete message (only sender or room admin)"""
        user = self.request.user
        is_admin = instance.chat_room.participants_info.filter(
            user=user,
            role__in=['admin', 'moderator']
        ).exists()
        
        if instance.sender != user and not is_admin:
            raise PermissionDenied("You can only delete your own messages or you must be an admin.")
        
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['is_deleted', 'deleted_at'])


class MessageReactionView(generics.CreateAPIView, generics.DestroyAPIView):
    """Add or remove reactions to messages"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageReactionSerializer
    
    def get_queryset(self):
        return MessageReaction.objects.filter(
            message__chat_room__participants=self.request.user
        )
    
    def create(self, request, *args, **kwargs):
        """Add reaction to message"""
        message_id = kwargs.get('message_id')
        emoji = request.data.get('emoji')
        
        # Verify message exists and user has access
        message = get_object_or_404(
            Message,
            id=message_id,
            chat_room__participants=request.user,
            is_deleted=False
        )
        
        # Create or update reaction
        reaction, created = MessageReaction.objects.get_or_create(
            message=message,
            user=request.user,
            defaults={'emoji': emoji}
        )
        
        if not created:
            if reaction.emoji == emoji:
                # Remove reaction if same emoji
                reaction.delete()
                return Response({'detail': 'Reaction removed'}, status=status.HTTP_204_NO_CONTENT)
            else:
                # Update emoji
                reaction.emoji = emoji
                reaction.save()
        
        serializer = self.get_serializer(reaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, *args, **kwargs):
        """Remove reaction from message"""
        message_id = kwargs.get('message_id')
        
        reaction = get_object_or_404(
            MessageReaction,
            message_id=message_id,
            user=request.user,
            message__chat_room__participants=request.user
        )
        
        reaction.delete()
        return Response({'detail': 'Reaction removed'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_messages_read(request, chat_room_id):
    """Mark all messages in a chat room as read"""
    chat_room = get_object_or_404(
        ChatRoom,
        id=chat_room_id,
        participants=request.user
    )
    
    # Get unread messages
    participant = chat_room.participants_info.get(user=request.user)
    last_read = participant.last_read_at or participant.joined_at
    
    unread_messages = chat_room.messages.filter(
        created_at__gt=last_read
    ).exclude(sender=request.user)
    
    # Create read status for all unread messages
    read_statuses = []
    for message in unread_messages:
        read_status, created = MessageReadStatus.objects.get_or_create(
            message=message,
            user=request.user
        )
        if created:
            read_statuses.append(read_status)
    
    # Update participant's last read time
    participant.last_read_at = timezone.now()
    participant.save(update_fields=['last_read_at'])
    
    return Response({
        'detail': f'Marked {len(read_statuses)} messages as read',
        'marked_count': len(read_statuses)
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def typing_indicator(request):
    """Handle typing indicators"""
    serializer = TypingIndicatorSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    
    chat_room_id = serializer.validated_data['chat_room_id']
    is_typing = serializer.validated_data['is_typing']
    
    # Update participant typing status
    participant = ChatRoomParticipant.objects.get(
        chat_room_id=chat_room_id,
        user=request.user
    )
    
    participant.is_typing = is_typing
    participant.typing_updated_at = timezone.now()
    participant.save(update_fields=['is_typing', 'typing_updated_at'])
    
    return Response({
        'detail': 'Typing status updated',
        'is_typing': is_typing
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def typing_users(request, chat_room_id):
    """Get list of users currently typing in a chat room"""
    chat_room = get_object_or_404(
        ChatRoom,
        id=chat_room_id,
        participants=request.user
    )
    
    # Get users typing in last 10 seconds
    cutoff_time = timezone.now() - timezone.timedelta(seconds=10)
    
    typing_participants = chat_room.participants_info.filter(
        is_typing=True,
        typing_updated_at__gt=cutoff_time
    ).exclude(user=request.user).select_related('user')
    
    typing_users = []
    for participant in typing_participants:
        typing_users.append({
            'id': participant.user.id,
            'full_name': participant.user.full_name,
            'typing_since': participant.typing_updated_at
        })
    
    return Response({'typing_users': typing_users})


class ChatRoomParticipantsView(generics.ListCreateAPIView):
    """List and add participants to a chat room"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatRoomParticipantSerializer
    
    def get_queryset(self):
        chat_room_id = self.kwargs['chat_room_id']
        
        # Verify user has access to this chat room
        get_object_or_404(
            ChatRoom,
            id=chat_room_id,
            participants=self.request.user
        )
        
        return ChatRoomParticipant.objects.filter(
            chat_room_id=chat_room_id
        ).select_related('user').order_by('-role', 'joined_at')
    
    def create(self, request, *args, **kwargs):
        """Add participant to chat room"""
        chat_room_id = kwargs['chat_room_id']
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'member')
        
        # Verify user is admin/moderator of this chat room
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        user_participant = chat_room.participants_info.filter(
            user=request.user,
            role__in=['admin', 'moderator']
        ).first()
        
        if not user_participant:
            raise PermissionDenied("Only admins and moderators can add participants.")
        
        # Add new participant
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            new_user = User.objects.get(id=user_id)
            
            participant, created = ChatRoomParticipant.objects.get_or_create(
                chat_room=chat_room,
                user=new_user,
                defaults={'role': role}
            )
            
            if not created:
                return Response(
                    {'detail': 'User is already a participant'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(participant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_participant(request, chat_room_id, participant_id):
    """Remove participant from chat room"""
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
    
    # Verify user is admin/moderator or removing themselves
    user_participant = chat_room.participants_info.filter(user=request.user).first()
    if not user_participant:
        raise PermissionDenied("You are not a participant in this chat room.")
    
    participant_to_remove = get_object_or_404(
        ChatRoomParticipant,
        id=participant_id,
        chat_room=chat_room
    )
    
    # Check permissions
    is_admin = user_participant.role in ['admin', 'moderator']
    is_self = participant_to_remove.user == request.user
    
    if not (is_admin or is_self):
        raise PermissionDenied("You can only remove yourself or you must be an admin.")
    
    # Don't allow removing the last admin
    if participant_to_remove.role == 'admin':
        admin_count = chat_room.participants_info.filter(role='admin').count()
        if admin_count <= 1:
            return Response(
                {'detail': 'Cannot remove the last admin'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    participant_to_remove.delete()
    return Response({'detail': 'Participant removed'}, status=status.HTTP_204_NO_CONTENT)


class ChatSettingsView(generics.RetrieveUpdateAPIView):
    """Get and update chat settings"""
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ChatSettingsSerializer
    
    def get_object(self):
        """Get or create chat settings"""
        settings, created = ChatSettings.objects.get_or_create(id=1)
        return settings


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_messages(request, chat_room_id):
    """Search messages in a chat room"""
    query = request.GET.get('q', '').strip()
    if not query:
        return Response({'results': []})
    
    # Verify user has access to chat room
    chat_room = get_object_or_404(
        ChatRoom,
        id=chat_room_id,
        participants=request.user
    )
    
    # Search messages
    messages = Message.objects.filter(
        chat_room=chat_room,
        is_deleted=False,
        content__icontains=query
    ).select_related('sender').order_by('-created_at')[:20]
    
    serializer = MessageSerializer(messages, many=True, context={'request': request})
    return Response({'results': serializer.data})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chat_room_search(request):
    """Search for chat rooms"""
    query = request.GET.get('q', '').strip()
    
    queryset = ChatRoom.objects.filter(
        participants=request.user,
        is_active=True
    )
    
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) |
            Q(participants__first_name__icontains=query) |
            Q(participants__last_name__icontains=query)
        ).distinct()
    
    serializer = ChatRoomListSerializer(
        queryset[:10],
        many=True,
        context={'request': request}
    )
    return Response({'results': serializer.data})
