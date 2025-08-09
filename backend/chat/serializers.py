from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    ChatRoom, ChatRoomParticipant, Message, MessageReaction, 
    MessageReadStatus, ChatSettings
)
from users.serializers import UserSerializer

User = get_user_model()


class ChatRoomParticipantSerializer(serializers.ModelSerializer):
    """Serializer for chat room participants"""
    user = UserSerializer(read_only=True)
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoomParticipant
        fields = [
            'id', 'user', 'role', 'joined_at', 'last_read_at',
            'is_typing', 'typing_updated_at', 'notifications_enabled',
            'sound_enabled', 'unread_count'
        ]
        read_only_fields = ['joined_at', 'typing_updated_at']
    
    def get_unread_count(self, obj):
        """Get unread message count for this participant"""
        if not obj.last_read_at:
            return obj.chat_room.messages.exclude(sender=obj.user).count()
        
        return obj.chat_room.messages.filter(
            created_at__gt=obj.last_read_at
        ).exclude(sender=obj.user).count()


class ChatRoomListSerializer(serializers.ModelSerializer):
    """Serializer for chat room list view"""
    participants = ChatRoomParticipantSerializer(source='participants_info', many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'room_type', 'is_active', 'created_at',
            'updated_at', 'participants', 'last_message', 'unread_count',
            'participant_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_last_message(self, obj):
        """Get the last message in the room"""
        last_message = obj.last_message
        if last_message:
            return {
                'id': last_message.id,
                'content': last_message.content[:100] + '...' if len(last_message.content) > 100 else last_message.content,
                'message_type': last_message.message_type,
                'sender': {
                    'id': last_message.sender.id,
                    'full_name': last_message.sender.full_name
                },
                'created_at': last_message.created_at,
                'is_deleted': last_message.is_deleted
            }
        return None
    
    def get_unread_count(self, obj):
        """Get unread count for current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.unread_count_for_user(request.user)
        return 0
    
    def get_participant_count(self, obj):
        """Get total participant count"""
        return obj.participants.count()


class ChatRoomDetailSerializer(ChatRoomListSerializer):
    """Detailed serializer for chat room"""
    session = serializers.SerializerMethodField()
    booking = serializers.SerializerMethodField()
    
    class Meta(ChatRoomListSerializer.Meta):
        fields = ChatRoomListSerializer.Meta.fields + ['session', 'booking']
    
    def get_session(self, obj):
        """Get related session info"""
        if obj.session:
            return {
                'id': obj.session.id,
                'status': obj.session.status,
                'started_at': obj.session.started_at,
                'ended_at': obj.session.ended_at
            }
        return None
    
    def get_booking(self, obj):
        """Get related booking info"""
        if obj.booking:
            return {
                'id': obj.booking.id,
                'subject': obj.booking.subject,
                'status': obj.booking.status,
                'requested_start_utc': obj.booking.requested_start_utc,
                'mentor': {
                    'id': obj.booking.mentor.id,
                    'full_name': obj.booking.mentor.full_name
                },
                'learner': {
                    'id': obj.booking.learner.id,
                    'full_name': obj.booking.learner.full_name
                }
            }
        return None


class MessageReactionSerializer(serializers.ModelSerializer):
    """Serializer for message reactions"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = MessageReaction
        fields = ['id', 'emoji', 'user', 'created_at']
        read_only_fields = ['created_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    sender = UserSerializer(read_only=True)
    reactions = MessageReactionSerializer(many=True, read_only=True)
    reaction_counts = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'chat_room', 'sender', 'message_type', 'content',
            'file_upload', 'file_name', 'file_size', 'file_mime_type',
            'edited_at', 'is_edited', 'is_deleted', 'deleted_at',
            'parent_message', 'reply_count', 'system_data',
            'created_at', 'updated_at', 'reactions', 'reaction_counts',
            'user_reaction', 'is_read'
        ]
        read_only_fields = [
            'sender', 'created_at', 'updated_at', 'edited_at',
            'deleted_at', 'reply_count'
        ]
    
    def get_reaction_counts(self, obj):
        """Get reaction counts grouped by emoji"""
        reactions = obj.reactions.all()
        counts = {}
        for reaction in reactions:
            emoji = reaction.emoji
            if emoji in counts:
                counts[emoji] += 1
            else:
                counts[emoji] = 1
        return counts
    
    def get_user_reaction(self, obj):
        """Get current user's reaction to this message"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            reaction = obj.reactions.filter(user=request.user).first()
            if reaction:
                return reaction.emoji
        return None
    
    def get_is_read(self, obj):
        """Check if current user has read this message"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            read_status = obj.read_status.filter(user=request.user).first()
            return bool(read_status)
        return False
    
    def validate(self, data):
        """Validate message data"""
        message_type = data.get('message_type', 'text')
        content = data.get('content', '')
        file_upload = data.get('file_upload')
        
        if message_type == 'text' and not content.strip():
            raise serializers.ValidationError("Text messages must have content.")
        
        if message_type == 'file' and not file_upload:
            raise serializers.ValidationError("File messages must include a file upload.")
        
        return data


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages"""
    
    class Meta:
        model = Message
        fields = [
            'chat_room', 'message_type', 'content', 'file_upload',
            'parent_message', 'system_data'
        ]
    
    def create(self, validated_data):
        """Create message with sender from request"""
        request = self.context['request']
        validated_data['sender'] = request.user
        
        # Handle file metadata
        file_upload = validated_data.get('file_upload')
        if file_upload:
            validated_data['file_name'] = file_upload.name
            validated_data['file_size'] = file_upload.size
            validated_data['file_mime_type'] = getattr(file_upload, 'content_type', '')
        
        return super().create(validated_data)


class MessageUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating messages"""
    
    class Meta:
        model = Message
        fields = ['content']
    
    def update(self, instance, validated_data):
        """Update message and mark as edited"""
        instance.content = validated_data.get('content', instance.content)
        instance.is_edited = True
        instance.edited_at = timezone.now()
        instance.save()
        return instance


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating chat rooms"""
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ChatRoom
        fields = [
            'name', 'room_type', 'session', 'booking',
            'allow_file_uploads', 'auto_delete_after_days',
            'participant_ids'
        ]
    
    def create(self, validated_data):
        """Create chat room with participants"""
        participant_ids = validated_data.pop('participant_ids', [])
        request = self.context['request']
        
        # Create the chat room
        chat_room = super().create(validated_data)
        
        # Add creator as admin
        ChatRoomParticipant.objects.create(
            chat_room=chat_room,
            user=request.user,
            role='admin'
        )
        
        # Add other participants
        for user_id in participant_ids:
            try:
                user = User.objects.get(id=user_id)
                ChatRoomParticipant.objects.get_or_create(
                    chat_room=chat_room,
                    user=user,
                    defaults={'role': 'member'}
                )
            except User.DoesNotExist:
                continue
        
        return chat_room


class ChatSettingsSerializer(serializers.ModelSerializer):
    """Serializer for chat settings"""
    
    class Meta:
        model = ChatSettings
        fields = [
            'id', 'allowed_file_types', 'max_file_size_mb',
            'blocked_words', 'auto_moderation_enabled',
            'message_retention_days', 'enable_message_editing',
            'enable_message_deletion', 'enable_file_uploads',
            'enable_emoji_reactions', 'rate_limit_enabled',
            'max_messages_per_minute', 'max_messages_per_hour',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class TypingIndicatorSerializer(serializers.Serializer):
    """Serializer for typing indicators"""
    chat_room_id = serializers.IntegerField()
    is_typing = serializers.BooleanField()
    
    def validate_chat_room_id(self, value):
        """Validate chat room exists and user has access"""
        request = self.context['request']
        try:
            chat_room = ChatRoom.objects.get(id=value)
            if not chat_room.participants.filter(id=request.user.id).exists():
                raise serializers.ValidationError("You don't have access to this chat room.")
            return value
        except ChatRoom.DoesNotExist:
            raise serializers.ValidationError("Chat room does not exist.")


class MessageReadStatusSerializer(serializers.ModelSerializer):
    """Serializer for message read status"""
    
    class Meta:
        model = MessageReadStatus
        fields = ['message', 'user', 'read_at']
        read_only_fields = ['read_at']
