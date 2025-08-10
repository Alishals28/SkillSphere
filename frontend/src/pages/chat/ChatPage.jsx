import React, { useState, useEffect, useRef } from 'react';
import { Send, Paperclip, User, Users, MessageSquare, Search, Phone, Video, Loader } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import './ChatPage.css';

// Mock data outside component to prevent re-renders
const mockConversations = [
  {
    id: 1,
    name: 'Dr. Sarah Martinez',
    avatar: null,
    lastMessage: 'Looking forward to our React session!',
    lastMessageTime: '10:30 AM',
    unreadCount: 2,
    online: true,
    type: 'mentor'
  },
  {
    id: 2,
    name: 'Prof. Michael Chen',
    avatar: null,
    lastMessage: 'Thanks for the Python help',
    lastMessageTime: 'Yesterday',
    unreadCount: 0,
    online: false,
    type: 'mentor'
  },
  {
    id: 3,
    name: 'Study Group - React Beginners',
    avatar: null,
    lastMessage: 'Anyone available for practice?',
    lastMessageTime: '2 hours ago',
    unreadCount: 5,
    online: true,
    type: 'group'
  }
];

// Mock messages for different conversations
const mockMessagesData = {
  1: [ // Dr. Sarah Martinez
    {
      id: 1,
      sender: { id: 2, name: 'Dr. Sarah Martinez', isCurrentUser: false },
      text: 'Hi! Ready for your React session today?',
      timestamp: '2024-01-10T09:00:00Z'
    },
    {
      id: 2,
      sender: { id: 1, name: 'You', isCurrentUser: true },
      text: 'Yes! I have a few questions about hooks and state management.',
      timestamp: '2024-01-10T09:01:00Z'
    },
    {
      id: 3,
      sender: { id: 2, name: 'Dr. Sarah Martinez', isCurrentUser: false },
      text: 'Perfect! Send them over and we can discuss them in detail.',
      timestamp: '2024-01-10T09:02:00Z'
    },
    {
      id: 4,
      sender: { id: 2, name: 'Dr. Sarah Martinez', isCurrentUser: false },
      text: 'Looking forward to our React session!',
      timestamp: '2024-01-10T10:30:00Z'
    }
  ],
  2: [ // Prof. Michael Chen
    {
      id: 1,
      sender: { id: 3, name: 'Prof. Michael Chen', isCurrentUser: false },
      text: 'How did the Python assignment go?',
      timestamp: '2024-01-09T14:00:00Z'
    },
    {
      id: 2,
      sender: { id: 1, name: 'You', isCurrentUser: true },
      text: 'It went well! The data structures exercise was challenging but I managed to solve it.',
      timestamp: '2024-01-09T14:15:00Z'
    },
    {
      id: 3,
      sender: { id: 1, name: 'You', isCurrentUser: true },
      text: 'Thanks for the Python help',
      timestamp: '2024-01-09T14:16:00Z'
    }
  ],
  3: [ // Study Group
    {
      id: 1,
      sender: { id: 4, name: 'Alex', isCurrentUser: false },
      text: 'Hey everyone! How are you doing with the React components?',
      timestamp: '2024-01-10T08:00:00Z'
    },
    {
      id: 2,
      sender: { id: 5, name: 'Emma', isCurrentUser: false },
      text: 'Still struggling with useEffect dependencies',
      timestamp: '2024-01-10T08:15:00Z'
    },
    {
      id: 3,
      sender: { id: 1, name: 'You', isCurrentUser: true },
      text: 'I can help with that! Let me share some resources',
      timestamp: '2024-01-10T08:30:00Z'
    },
    {
      id: 4,
      sender: { id: 4, name: 'Alex', isCurrentUser: false },
      text: 'Anyone available for practice?',
      timestamp: '2024-01-10T10:00:00Z'
    }
  ]
};

const ChatPage = () => {
  const { user } = useAuth(); // Will be used for real user data later
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [attachments, setAttachments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    console.log('ChatPage mounted, setting up chat data immediately...');
    // Set up data immediately for testing
    setConversations(mockConversations);
    setActiveConversation(mockConversations[0]);
    // Load messages for the first conversation
    setMessages(mockMessagesData[mockConversations[0].id] || []);
    setLoading(false);
    console.log('Chat page loaded successfully');
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (input.trim() === '') return;
    
    const newMessage = {
      id: messages.length + 1,
      sender: { id: 1, name: 'You', isCurrentUser: true },
      text: input,
      timestamp: new Date().toISOString()
    };

    setMessages([...messages, newMessage]);
    setInput('');
    setAttachments([]);
  };

  const handleAttachment = (e) => {
    const files = Array.from(e.target.files);
    setAttachments([...attachments, ...files]);
  };

  const selectConversation = (conversation) => {
    setActiveConversation(conversation);
    
    // Load messages for this specific conversation
    const conversationMessages = mockMessagesData[conversation.id] || [];
    setMessages(conversationMessages);
    
    // Clear unread count for this conversation
    const updatedConversations = conversations.map(conv => 
      conv.id === conversation.id 
        ? { ...conv, unreadCount: 0 }
        : conv
    );
    setConversations(updatedConversations);
  };

  const filteredConversations = conversations.filter(conv =>
    conv.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    console.log('Rendering loading state...');
    return (
      <div className="chat-page">
        <div className="chat-loading">
          <Loader className="loading-spinner" size={32} />
          <h3>Loading your conversations...</h3>
          <p>Connecting to chat service</p>
        </div>
      </div>
    );
  }

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chat-page">
      {/* Conversations Sidebar */}
      <div className="conversations-sidebar">
        <div className="sidebar-header">
          <h2>Messages</h2>
          <MessageSquare size={20} />
        </div>
        
        <div className="search-container">
          <Search size={16} />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="conversations-list">
          {filteredConversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`conversation-item ${activeConversation?.id === conversation.id ? 'active' : ''}`}
              onClick={() => selectConversation(conversation)}
            >
              <div className="conversation-avatar">
                {conversation.type === 'group' ? (
                  <Users size={20} />
                ) : (
                  <User size={20} />
                )}
                {conversation.online && <div className="online-indicator" />}
              </div>
              
              <div className="conversation-info">
                <div className="conversation-header">
                  <h4>{conversation.name}</h4>
                  <span className="time">{conversation.lastMessageTime}</span>
                </div>
                <div className="conversation-preview">
                  <p>{conversation.lastMessage}</p>
                  {conversation.unreadCount > 0 && (
                    <span className="unread-badge">{conversation.unreadCount}</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="chat-area">
        {activeConversation ? (
          <>
            {/* Chat Header */}
            <div className="chat-header">
              <div className="chat-info">
                <div className="chat-avatar">
                  {activeConversation.type === 'group' ? (
                    <Users size={24} />
                  ) : (
                    <User size={24} />
                  )}
                  {activeConversation.online && <div className="online-indicator" />}
                </div>
                <div>
                  <h3>{activeConversation.name}</h3>
                  <p className="status">
                    {activeConversation.online ? 'Active now' : 'Last seen yesterday'}
                  </p>
                </div>
              </div>
              
              <div className="chat-actions">
                <button className="action-btn">
                  <Phone size={20} />
                </button>
                <button className="action-btn">
                  <Video size={20} />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="messages-container">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`message ${message.sender.isCurrentUser ? 'sent' : 'received'}`}
                >
                  {!message.sender.isCurrentUser && (
                    <div className="message-avatar">
                      <User size={16} />
                    </div>
                  )}
                  <div className="message-content">
                    <div className="message-bubble">
                      <p>{message.text}</p>
                    </div>
                    <span className="message-time">
                      {formatTime(message.timestamp)}
                    </span>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="input-area">
              {attachments.length > 0 && (
                <div className="attachments-preview">
                  {attachments.map((file, index) => (
                    <div key={index} className="attachment-item">
                      <span>{file.name}</span>
                      <button onClick={() => setAttachments(attachments.filter((_, i) => i !== index))}>
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}
              
              <div className="input-controls">
                <input
                  type="file"
                  id="file-input"
                  multiple
                  onChange={handleAttachment}
                  style={{ display: 'none' }}
                />
                <label htmlFor="file-input" className="attachment-btn">
                  <Paperclip size={20} />
                </label>
                
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Type your message..."
                  className="message-input"
                />
                
                <button onClick={handleSend} className="send-btn">
                  <Send size={20} />
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="no-conversation">
            <MessageSquare size={64} />
            <h3>Select a conversation</h3>
            <p>Choose a conversation from the sidebar to start messaging</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatPage;
