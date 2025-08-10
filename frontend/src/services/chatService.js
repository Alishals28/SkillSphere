// Chat API service for real-time messaging
import api from './api';

class ChatService {
  constructor() {
    this.ws = null;
    this.messageHandlers = [];
    this.statusHandlers = [];
  }

  // REST API methods
  async getChatRooms() {
    try {
      const response = await api.get('/chat/rooms/');
      return response.data;
    } catch (error) {
      console.error('Error fetching chat rooms:', error);
      throw error;
    }
  }

  async getChatRoom(roomId) {
    try {
      const response = await api.get(`/chat/rooms/${roomId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching chat room:', error);
      throw error;
    }
  }

  async getMessages(roomId, page = 1) {
    try {
      const response = await api.get(`/chat/rooms/${roomId}/messages/`, {
        params: { page }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching messages:', error);
      throw error;
    }
  }

  async sendMessage(roomId, content, attachments = []) {
    try {
      const formData = new FormData();
      formData.append('content', content);
      
      attachments.forEach((file, index) => {
        formData.append(`attachments`, file);
      });

      const response = await api.post(`/chat/rooms/${roomId}/messages/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  async markAsRead(roomId, messageId) {
    try {
      await api.post(`/chat/rooms/${roomId}/messages/${messageId}/read/`);
    } catch (error) {
      console.error('Error marking message as read:', error);
    }
  }

  // WebSocket methods
  connectToRoom(roomId) {
    if (this.ws) {
      this.ws.close();
    }

    const token = localStorage.getItem('access_token');
    const wsUrl = `${process.env.REACT_APP_WS_URL || 'ws://localhost:8000'}/ws/chat/${roomId}/?token=${token}`;
    
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('Connected to chat room:', roomId);
      this.notifyStatusHandlers('connected');
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleWebSocketMessage(data);
    };

    this.ws.onclose = () => {
      console.log('Disconnected from chat room');
      this.notifyStatusHandlers('disconnected');
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.notifyStatusHandlers('error');
    };
  }

  handleWebSocketMessage(data) {
    switch (data.type) {
      case 'new_message':
        this.notifyMessageHandlers('message', data.message);
        break;
      case 'message_read':
        this.notifyMessageHandlers('read', data);
        break;
      case 'user_typing':
        this.notifyMessageHandlers('typing', data);
        break;
      case 'user_joined':
        this.notifyStatusHandlers('user_joined', data);
        break;
      case 'user_left':
        this.notifyStatusHandlers('user_left', data);
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  }

  sendTypingIndicator(isTyping) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'typing',
        is_typing: isTyping
      }));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  // Event handlers
  onMessage(handler) {
    this.messageHandlers.push(handler);
  }

  onStatus(handler) {
    this.statusHandlers.push(handler);
  }

  offMessage(handler) {
    this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
  }

  offStatus(handler) {
    this.statusHandlers = this.statusHandlers.filter(h => h !== handler);
  }

  notifyMessageHandlers(type, data) {
    this.messageHandlers.forEach(handler => {
      try {
        handler(type, data);
      } catch (error) {
        console.error('Error in message handler:', error);
      }
    });
  }

  notifyStatusHandlers(type, data) {
    this.statusHandlers.forEach(handler => {
      try {
        handler(type, data);
      } catch (error) {
        console.error('Error in status handler:', error);
      }
    });
  }
}

export default new ChatService();
