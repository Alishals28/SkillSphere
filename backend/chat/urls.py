from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Chat rooms
    path('rooms/', views.ChatRoomListView.as_view(), name='chat-room-list'),
    path('rooms/<int:pk>/', views.ChatRoomDetailView.as_view(), name='chat-room-detail'),
    path('rooms/search/', views.chat_room_search, name='chat-room-search'),
    
    # Chat room participants
    path('rooms/<int:chat_room_id>/participants/', views.ChatRoomParticipantsView.as_view(), name='chat-room-participants'),
    path('rooms/<int:chat_room_id>/participants/<int:participant_id>/remove/', views.remove_participant, name='remove-participant'),
    
    # Messages
    path('rooms/<int:chat_room_id>/messages/', views.ChatRoomMessagesView.as_view(), name='chat-room-messages'),
    path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message-detail'),
    path('messages/<int:message_id>/reactions/', views.MessageReactionView.as_view(), name='message-reactions'),
    path('rooms/<int:chat_room_id>/messages/search/', views.search_messages, name='search-messages'),
    
    # Message actions
    path('rooms/<int:chat_room_id>/mark-read/', views.mark_messages_read, name='mark-messages-read'),
    
    # Typing indicators
    path('typing/', views.typing_indicator, name='typing-indicator'),
    path('rooms/<int:chat_room_id>/typing/', views.typing_users, name='typing-users'),
    
    # Chat settings (admin only)
    path('settings/', views.ChatSettingsView.as_view(), name='chat-settings'),
]
