import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import ChatRoom, ChatRoomParticipant, Message, MessageReadStatus
from .serializers import MessageSerializer

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.chat_room_id = self.scope['url_route']['kwargs']['chat_room_id']
        self.room_group_name = f'chat_{self.chat_room_id}'
        self.user = self.scope.get('user')
        
        # Check if user is authenticated and has access to chat room
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Verify user has access to this chat room
        has_access = await self.check_chat_room_access()
        if not has_access:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Notify others that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user.id,
                'user_name': self.user.full_name,
            }
        )
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            # Update typing status to false
            await self.update_typing_status(False)
            
            # Notify others that user left
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'user_id': self.user.id,
                    'user_name': self.user.full_name,
                }
            )
            
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle received WebSocket message"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'typing':
                await self.handle_typing_indicator(data)
            elif message_type == 'mark_read':
                await self.handle_mark_read(data)
            elif message_type == 'edit_message':
                await self.handle_edit_message(data)
            elif message_type == 'delete_message':
                await self.handle_delete_message(data)
            elif message_type == 'react_message':
                await self.handle_message_reaction(data)
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def handle_chat_message(self, data):
        """Handle new chat message"""
        content = data.get('content', '').strip()
        message_type = data.get('message_type', 'text')
        parent_message_id = data.get('parent_message_id')
        
        if not content and message_type == 'text':
            return
        
        # Create message in database
        message = await self.create_message(content, message_type, parent_message_id)
        if not message:
            return
        
        # Get serialized message data
        message_data = await self.serialize_message(message)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_data
            }
        )
    
    async def handle_typing_indicator(self, data):
        """Handle typing indicator"""
        is_typing = data.get('is_typing', False)
        
        # Update typing status in database
        await self.update_typing_status(is_typing)
        
        # Send typing indicator to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': self.user.id,
                'user_name': self.user.full_name,
                'is_typing': is_typing
            }
        )
    
    async def handle_mark_read(self, data):
        """Handle mark messages as read"""
        message_ids = data.get('message_ids', [])
        
        # Mark messages as read in database
        await self.mark_messages_read(message_ids)
        
        # Send read receipt to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'messages_read',
                'user_id': self.user.id,
                'message_ids': message_ids
            }
        )
    
    async def handle_edit_message(self, data):
        """Handle message editing"""
        message_id = data.get('message_id')
        new_content = data.get('content', '').strip()
        
        if not new_content:
            return
        
        # Update message in database
        success = await self.edit_message(message_id, new_content)
        if not success:
            return
        
        # Send updated message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message_edited',
                'message_id': message_id,
                'content': new_content,
                'edited_by': self.user.id
            }
        )
    
    async def handle_delete_message(self, data):
        """Handle message deletion"""
        message_id = data.get('message_id')
        
        # Delete message in database
        success = await self.delete_message(message_id)
        if not success:
            return
        
        # Send deletion notification to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message_deleted',
                'message_id': message_id,
                'deleted_by': self.user.id
            }
        )
    
    async def handle_message_reaction(self, data):
        """Handle message reactions"""
        message_id = data.get('message_id')
        emoji = data.get('emoji')
        action = data.get('action')  # 'add' or 'remove'
        
        # Update reaction in database
        success = await self.update_message_reaction(message_id, emoji, action)
        if not success:
            return
        
        # Send reaction update to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message_reaction',
                'message_id': message_id,
                'emoji': emoji,
                'action': action,
                'user_id': self.user.id
            }
        )
    
    # WebSocket message handlers
    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))
    
    async def typing_indicator(self, event):
        """Send typing indicator to WebSocket"""
        # Don't send typing indicator to the user who is typing
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'user_id': event['user_id'],
                'user_name': event['user_name'],
                'is_typing': event['is_typing']
            }))
    
    async def messages_read(self, event):
        """Send read receipt to WebSocket"""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'messages_read',
                'user_id': event['user_id'],
                'message_ids': event['message_ids']
            }))
    
    async def message_edited(self, event):
        """Send message edit to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message_edited',
            'message_id': event['message_id'],
            'content': event['content'],
            'edited_by': event['edited_by']
        }))
    
    async def message_deleted(self, event):
        """Send message deletion to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id'],
            'deleted_by': event['deleted_by']
        }))
    
    async def message_reaction(self, event):
        """Send message reaction to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message_reaction',
            'message_id': event['message_id'],
            'emoji': event['emoji'],
            'action': event['action'],
            'user_id': event['user_id']
        }))
    
    async def user_joined(self, event):
        """Send user joined notification to WebSocket"""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'user_id': event['user_id'],
                'user_name': event['user_name']
            }))
    
    async def user_left(self, event):
        """Send user left notification to WebSocket"""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_left',
                'user_id': event['user_id'],
                'user_name': event['user_name']
            }))
    
    # Database operations
    @database_sync_to_async
    def check_chat_room_access(self):
        """Check if user has access to chat room"""
        try:
            return ChatRoom.objects.filter(
                id=self.chat_room_id,
                participants=self.user
            ).exists()
        except:
            return False
    
    @database_sync_to_async
    def create_message(self, content, message_type, parent_message_id=None):
        """Create new message in database"""
        try:
            chat_room = ChatRoom.objects.get(
                id=self.chat_room_id,
                participants=self.user
            )
            
            parent_message = None
            if parent_message_id:
                try:
                    parent_message = Message.objects.get(
                        id=parent_message_id,
                        chat_room=chat_room
                    )
                except Message.DoesNotExist:
                    pass
            
            message = Message.objects.create(
                chat_room=chat_room,
                sender=self.user,
                content=content,
                message_type=message_type,
                parent_message=parent_message
            )
            
            # Update chat room timestamp
            chat_room.updated_at = timezone.now()
            chat_room.save(update_fields=['updated_at'])
            
            # Mark message as read for sender
            MessageReadStatus.objects.get_or_create(
                message=message,
                user=self.user
            )
            
            return message
        except:
            return None
    
    @database_sync_to_async
    def serialize_message(self, message):
        """Serialize message for JSON response"""
        from django.http import HttpRequest
        
        # Create a fake request for serializer context
        request = HttpRequest()
        request.user = self.user
        
        serializer = MessageSerializer(message, context={'request': request})
        return serializer.data
    
    @database_sync_to_async
    def update_typing_status(self, is_typing):
        """Update user's typing status"""
        try:
            participant = ChatRoomParticipant.objects.get(
                chat_room_id=self.chat_room_id,
                user=self.user
            )
            participant.is_typing = is_typing
            participant.typing_updated_at = timezone.now()
            participant.save(update_fields=['is_typing', 'typing_updated_at'])
            return True
        except:
            return False
    
    @database_sync_to_async
    def mark_messages_read(self, message_ids):
        """Mark specified messages as read"""
        try:
            messages = Message.objects.filter(
                id__in=message_ids,
                chat_room_id=self.chat_room_id,
                chat_room__participants=self.user
            ).exclude(sender=self.user)
            
            for message in messages:
                MessageReadStatus.objects.get_or_create(
                    message=message,
                    user=self.user
                )
            
            # Update participant's last read time
            participant = ChatRoomParticipant.objects.get(
                chat_room_id=self.chat_room_id,
                user=self.user
            )
            participant.last_read_at = timezone.now()
            participant.save(update_fields=['last_read_at'])
            
            return True
        except:
            return False
    
    @database_sync_to_async
    def edit_message(self, message_id, new_content):
        """Edit a message"""
        try:
            message = Message.objects.get(
                id=message_id,
                sender=self.user,
                chat_room_id=self.chat_room_id
            )
            message.content = new_content
            message.is_edited = True
            message.edited_at = timezone.now()
            message.save(update_fields=['content', 'is_edited', 'edited_at'])
            return True
        except:
            return False
    
    @database_sync_to_async
    def delete_message(self, message_id):
        """Delete a message"""
        try:
            message = Message.objects.get(
                id=message_id,
                chat_room_id=self.chat_room_id
            )
            
            # Check if user can delete (sender or admin)
            is_sender = message.sender == self.user
            is_admin = ChatRoomParticipant.objects.filter(
                chat_room_id=self.chat_room_id,
                user=self.user,
                role__in=['admin', 'moderator']
            ).exists()
            
            if not (is_sender or is_admin):
                return False
            
            message.is_deleted = True
            message.deleted_at = timezone.now()
            message.save(update_fields=['is_deleted', 'deleted_at'])
            return True
        except:
            return False
    
    @database_sync_to_async
    def update_message_reaction(self, message_id, emoji, action):
        """Add or remove message reaction"""
        try:
            from .models import MessageReaction
            
            message = Message.objects.get(
                id=message_id,
                chat_room_id=self.chat_room_id,
                chat_room__participants=self.user
            )
            
            if action == 'add':
                reaction, created = MessageReaction.objects.get_or_create(
                    message=message,
                    user=self.user,
                    defaults={'emoji': emoji}
                )
                if not created and reaction.emoji != emoji:
                    reaction.emoji = emoji
                    reaction.save()
            elif action == 'remove':
                MessageReaction.objects.filter(
                    message=message,
                    user=self.user
                ).delete()
            
            return True
        except:
            return False
