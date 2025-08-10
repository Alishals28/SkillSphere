import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Send, 
  Paperclip, 
  Image, 
  File, 
  Smile,
  Phone,
  Video,
  MoreVertical,
  Search,
  ArrowLeft,
  Check,
  CheckCheck,
  Clock,
  Download,
  X,
  Plus,
  Mic,
  MicOff
} from 'lucide-react';
import './Chat.css';

const Chat = () => {
  const { user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [attachments, setAttachments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);

  // Mock conversations data
  useEffect(() => {
    const mockConversations = [
      {
        id: 1,
        participantId: 2,
        participantName: user?.role === 'learner' ? 'Dr. Sarah Martinez' : 'Alex Johnson',
        participantRole: user?.role === 'learner' ? 'mentor' : 'learner',
        participantAvatar: null,
        lastMessage: 'Looking forward to our React session tomorrow!',
        lastMessageTime: new Date(Date.now() - 1000 * 60 * 30),
        unreadCount: 2,
        isOnline: true,
        sessionId: 101
      },
      {
        id: 2,
        participantId: 3,
        participantName: user?.role === 'learner' ? 'Prof. Michael Chen' : 'Sarah Wilson',
        participantRole: user?.role === 'learner' ? 'mentor' : 'learner',
        participantAvatar: null,
        lastMessage: 'Here are the Python resources I mentioned',
        lastMessageTime: new Date(Date.now() - 1000 * 60 * 60 * 2),
        unreadCount: 0,
        isOnline: false,
        sessionId: 102
      },
      {
        id: 3,
        participantId: 4,
        participantName: user?.role === 'learner' ? 'Dr. Emily Rodriguez' : 'Mike Chen',
        participantRole: user?.role === 'learner' ? 'mentor' : 'learner',
        participantAvatar: null,
        lastMessage: 'Great progress on your project!',
        lastMessageTime: new Date(Date.now() - 1000 * 60 * 60 * 24),
        unreadCount: 1,
        isOnline: true,
        sessionId: 103
      }
    ];
    setConversations(mockConversations);
    setIsLoading(false);
  }, [user]);

  // Mock messages for selected conversation
  useEffect(() => {
    if (selectedConversation) {
      const mockMessages = [
        {
          id: 1,
          senderId: selectedConversation.participantId,
          senderName: selectedConversation.participantName,
          content: "Hi! I've reviewed your code and have some suggestions for improvement.",
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2),
          type: 'text',
          status: 'read'
        },
        {
          id: 2,
          senderId: user?.id,
          senderName: user?.name,
          content: "That would be great! I'm particularly struggling with state management.",
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 1.5),
          type: 'text',
          status: 'read'
        },
        {
          id: 3,
          senderId: selectedConversation.participantId,
          senderName: selectedConversation.participantName,
          content: "Here's a comprehensive guide on React hooks and state management best practices.",
          timestamp: new Date(Date.now() - 1000 * 60 * 60),
          type: 'file',
          fileUrl: '/docs/react-state-management.pdf',
          fileName: 'React State Management Guide.pdf',
          fileSize: '2.4 MB',
          status: 'read'
        },
        {
          id: 4,
          senderId: user?.id,
          senderName: user?.name,
          content: "Thank you so much! This is exactly what I needed.",
          timestamp: new Date(Date.now() - 1000 * 60 * 30),
          type: 'text',
          status: 'delivered'
        },
        {
          id: 5,
          senderId: selectedConversation.participantId,
          senderName: selectedConversation.participantName,
          content: "Looking forward to our React session tomorrow!",
          timestamp: new Date(Date.now() - 1000 * 60 * 15),
          type: 'text',
          status: 'read'
        }
      ];
      setMessages(mockMessages);
    }
  }, [selectedConversation, user]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = () => {
    if (newMessage.trim() || attachments.length > 0) {
      const message = {
        id: Date.now(),
        senderId: user?.id,
        senderName: user?.name,
        content: newMessage.trim(),
        timestamp: new Date(),
        type: attachments.length > 0 ? 'file' : 'text',
        attachments: attachments,
        status: 'sending'
      };

      setMessages(prev => [...prev, message]);
      setNewMessage('');
      setAttachments([]);

      // Simulate message delivery
      setTimeout(() => {
        setMessages(prev => prev.map(msg => 
          msg.id === message.id ? { ...msg, status: 'delivered' } : msg
        ));
      }, 1000);

      // Simulate read receipt
      setTimeout(() => {
        setMessages(prev => prev.map(msg => 
          msg.id === message.id ? { ...msg, status: 'read' } : msg
        ));
      }, 3000);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    const newAttachments = files.map(file => ({
      id: Date.now() + Math.random(),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      url: URL.createObjectURL(file)
    }));
    setAttachments(prev => [...prev, ...newAttachments]);
  };

  const removeAttachment = (attachmentId) => {
    setAttachments(prev => prev.filter(att => att.id !== attachmentId));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (date) => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString();
    }
  };

  const getMessageStatus = (status) => {
    switch (status) {
      case 'sending':
        return <Clock size={12} className="status-icon sending" />;
      case 'delivered':
        return <Check size={12} className="status-icon delivered" />;
      case 'read':
        return <CheckCheck size={12} className="status-icon read" />;
      default:
        return null;
    }
  };

  const filteredConversations = conversations.filter(conv =>
    conv.participantName.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (isLoading) {
    return (
      <div className="chat-page">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading conversations...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-page">
      {/* Conversations Sidebar */}
      <div className="conversations-sidebar">
        <div className="sidebar-header">
          <h2>Messages</h2>
          <button className="new-chat-btn">
            <Plus size={20} />
          </button>
        </div>

        <div className="search-section">
          <div className="search-input">
            <Search size={16} />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="conversations-list">
          {filteredConversations.map(conversation => (
            <div
              key={conversation.id}
              className={`conversation-item ${selectedConversation?.id === conversation.id ? 'active' : ''}`}
              onClick={() => setSelectedConversation(conversation)}
            >
              <div className="conversation-avatar">
                {conversation.participantAvatar ? (
                  <img src={conversation.participantAvatar} alt={conversation.participantName} />
                ) : (
                  <div className="avatar-placeholder">
                    {conversation.participantName.charAt(0)}
                  </div>
                )}
                {conversation.isOnline && <div className="online-indicator"></div>}
              </div>
              
              <div className="conversation-info">
                <div className="conversation-header">
                  <span className="participant-name">{conversation.participantName}</span>
                  <span className="conversation-time">
                    {formatTime(conversation.lastMessageTime)}
                  </span>
                </div>
                <div className="conversation-preview">
                  <span className="last-message">{conversation.lastMessage}</span>
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
        {selectedConversation ? (
          <>
            {/* Chat Header */}
            <div className="chat-header">
              <div className="chat-participant">
                <button className="back-btn">
                  <ArrowLeft size={20} />
                </button>
                <div className="participant-avatar">
                  {selectedConversation.participantAvatar ? (
                    <img src={selectedConversation.participantAvatar} alt={selectedConversation.participantName} />
                  ) : (
                    <div className="avatar-placeholder">
                      {selectedConversation.participantName.charAt(0)}
                    </div>
                  )}
                  {selectedConversation.isOnline && <div className="online-indicator"></div>}
                </div>
                <div className="participant-info">
                  <h3>{selectedConversation.participantName}</h3>
                  <span className="participant-status">
                    {selectedConversation.isOnline ? 'Online' : 'Last seen recently'}
                  </span>
                </div>
              </div>

              <div className="chat-actions">
                <button className="action-btn">
                  <Phone size={20} />
                </button>
                <button className="action-btn">
                  <Video size={20} />
                </button>
                <button className="action-btn">
                  <MoreVertical size={20} />
                </button>
              </div>
            </div>

            {/* Messages Area */}
            <div className="messages-area">
              <div className="messages-container">
                {messages.map((message, index) => {
                  const showDate = index === 0 || 
                    formatDate(message.timestamp) !== formatDate(messages[index - 1].timestamp);
                  const isOwnMessage = message.senderId === user?.id;

                  return (
                    <React.Fragment key={message.id}>
                      {showDate && (
                        <div className="date-divider">
                          <span>{formatDate(message.timestamp)}</span>
                        </div>
                      )}
                      
                      <div className={`message ${isOwnMessage ? 'own-message' : 'other-message'}`}>
                        <div className="message-content">
                          {message.type === 'text' && (
                            <div className="text-message">
                              {message.content}
                            </div>
                          )}
                          
                          {message.type === 'file' && (
                            <div className="file-message">
                              <div className="file-info">
                                <File size={24} />
                                <div className="file-details">
                                  <span className="file-name">{message.fileName}</span>
                                  <span className="file-size">{message.fileSize}</span>
                                </div>
                                <button className="download-btn">
                                  <Download size={16} />
                                </button>
                              </div>
                              {message.content && (
                                <div className="file-caption">{message.content}</div>
                              )}
                            </div>
                          )}

                          {message.attachments && message.attachments.map(attachment => (
                            <div key={attachment.id} className="attachment-preview">
                              {attachment.type.startsWith('image/') ? (
                                <img src={attachment.url} alt={attachment.name} />
                              ) : (
                                <div className="file-attachment">
                                  <File size={24} />
                                  <span>{attachment.name}</span>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                        
                        <div className="message-meta">
                          <span className="message-time">{formatTime(message.timestamp)}</span>
                          {isOwnMessage && getMessageStatus(message.status)}
                        </div>
                      </div>
                    </React.Fragment>
                  );
                })}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Typing Indicator */}
            {isTyping && (
              <div className="typing-indicator">
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span>{selectedConversation.participantName} is typing...</span>
              </div>
            )}

            {/* Attachments Preview */}
            {attachments.length > 0 && (
              <div className="attachments-preview">
                {attachments.map(attachment => (
                  <div key={attachment.id} className="attachment-item">
                    {attachment.type.startsWith('image/') ? (
                      <img src={attachment.url} alt={attachment.name} />
                    ) : (
                      <div className="file-preview">
                        <File size={24} />
                        <span>{attachment.name}</span>
                      </div>
                    )}
                    <button 
                      className="remove-attachment"
                      onClick={() => removeAttachment(attachment.id)}
                    >
                      <X size={16} />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Message Input */}
            <div className="message-input-area">
              <div className="input-container">
                <button 
                  className="attachment-btn"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Paperclip size={20} />
                </button>
                
                <div className="text-input-container">
                  <textarea
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type a message..."
                    rows={1}
                  />
                </div>

                <button className="emoji-btn">
                  <Smile size={20} />
                </button>

                <button 
                  className={`send-btn ${newMessage.trim() || attachments.length > 0 ? 'active' : ''}`}
                  onClick={handleSendMessage}
                  disabled={!newMessage.trim() && attachments.length === 0}
                >
                  <Send size={20} />
                </button>

                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  multiple
                  hidden
                  accept="image/*,application/pdf,.doc,.docx,.txt"
                />
              </div>
            </div>
          </>
        ) : (
          <div className="no-conversation-selected">
            <div className="empty-state">
              <div className="empty-icon">
                <Send size={48} />
              </div>
              <h3>Select a conversation</h3>
              <p>Choose a conversation from the sidebar to start messaging</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat;
