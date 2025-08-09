from django.db import models
from django.conf import settings
from django.utils import timezone


class ChatRoom(models.Model):
    """Chat room for mentoring sessions"""
    ROOM_TYPE_CHOICES = (
        ('session', 'Session Chat'),
        ('general', 'General Chat'),
        ('support', 'Support Chat'),
    )
    
    name = models.CharField(max_length=200, blank=True, default='Chat Room')
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default='session')
    is_active = models.BooleanField(default=True)
    
    # Participants
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ChatRoomParticipant',
        related_name='chat_rooms'
    )
    
    # Related objects
    session = models.OneToOneField(
        'mentoring_sessions.Session',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='chat_room'
    )
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='chat_room'
    )
    
    # Settings
    allow_file_uploads = models.BooleanField(default=True)
    auto_delete_after_days = models.PositiveIntegerField(default=90)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['room_type', 'is_active']),
            models.Index(fields=['session']),
            models.Index(fields=['booking']),
        ]

    def __str__(self):
        return f"{self.name} ({self.room_type})"
    
    @property
    def last_message(self):
        """Get the last message in this room"""
        return self.messages.order_by('-created_at').first()
    
    @property
    def unread_count_for_user(self, user):
        """Get unread message count for a specific user"""
        participant = self.participants_info.filter(user=user).first()
        if not participant:
            return 0
        
        return self.messages.filter(
            created_at__gt=participant.last_read_at or participant.joined_at
        ).exclude(sender=user).count()


class ChatRoomParticipant(models.Model):
    """Participant information for chat rooms"""
    ROLE_CHOICES = (
        ('member', 'Member'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    )
    
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='participants_info'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_participations'
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(null=True, blank=True)
    is_typing = models.BooleanField(default=False)
    typing_updated_at = models.DateTimeField(null=True, blank=True)
    
    # Notification settings
    notifications_enabled = models.BooleanField(default=True)
    sound_enabled = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['chat_room', 'user']
        indexes = [
            models.Index(fields=['chat_room', 'user']),
            models.Index(fields=['user', 'joined_at']),
        ]

    def __str__(self):
        return f"{self.user.full_name} in {self.chat_room.name}"
    
    def mark_as_read(self):
        """Mark all messages as read for this participant"""
        self.last_read_at = timezone.now()
        self.save(update_fields=['last_read_at'])


class Message(models.Model):
    """Chat message model"""
    MESSAGE_TYPE_CHOICES = (
        ('text', 'Text Message'),
        ('file', 'File Upload'),
        ('image', 'Image'),
        ('system', 'System Message'),
        ('code', 'Code Snippet'),
        ('link', 'Link Share'),
    )
    
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    
    # Message content
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField(blank=True, default='')
    
    # File uploads
    file_upload = models.FileField(upload_to='chat_files/', null=True, blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    file_mime_type = models.CharField(max_length=100, blank=True)
    
    # Message metadata
    edited_at = models.DateTimeField(null=True, blank=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Reactions and replies
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    # System message data
    system_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chat_room', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['message_type']),
            models.Index(fields=['is_deleted']),
        ]

    def __str__(self):
        if self.is_deleted:
            return f"[Deleted message] in {self.chat_room.name}"
        return f"{self.sender.full_name}: {self.content[:50]}..."
    
    def soft_delete(self):
        """Soft delete the message"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])


class MessageReaction(models.Model):
    """Message reactions (emojis)"""
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='message_reactions'
    )
    
    emoji = models.CharField(max_length=10, default='👍')  # Unicode emoji
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['message', 'user', 'emoji']
        indexes = [
            models.Index(fields=['message', 'emoji']),
        ]

    def __str__(self):
        return f"{self.user.full_name} reacted {self.emoji} to message"


class MessageReadStatus(models.Model):
    """Track read status of messages per user"""
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='read_statuses'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='message_read_statuses'
    )
    
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['message', 'user']
        indexes = [
            models.Index(fields=['message', 'user']),
            models.Index(fields=['user', 'read_at']),
        ]

    def __str__(self):
        return f"{self.user.full_name} read message at {self.read_at}"


class ChatSettings(models.Model):
    """Global chat settings"""
    max_file_size_mb = models.PositiveIntegerField(default=10)
    allowed_file_types = models.JSONField(
        default=list,
        help_text="List of allowed file extensions"
    )
    message_retention_days = models.PositiveIntegerField(default=365)
    enable_message_editing = models.BooleanField(default=True)
    enable_message_deletion = models.BooleanField(default=True)
    enable_file_uploads = models.BooleanField(default=True)
    enable_emoji_reactions = models.BooleanField(default=True)
    
    # Rate limiting
    max_messages_per_minute = models.PositiveIntegerField(default=30)
    max_messages_per_hour = models.PositiveIntegerField(default=500)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chat Settings"
        verbose_name_plural = "Chat Settings"

    def __str__(self):
        return "Chat Settings"

    @classmethod
    def get_settings(cls):
        """Get or create chat settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
