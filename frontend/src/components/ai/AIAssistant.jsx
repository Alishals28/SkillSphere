import React, { useState, useEffect, useRef } from 'react';
import { 
  MessageSquare, Send, Bot, User, Lightbulb, 
  BookOpen, Target, TrendingUp, Clock, X,
  Minimize2, Maximize2, Volume2, VolumeX
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import './AIAssistant.css';

const AIAssistant = ({ isOpen, onToggle, context = null }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [aiMode, setAiMode] = useState('general');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // AI modes
  const aiModes = [
    { id: 'general', name: 'General Help', icon: Bot, color: '#14b8a6' },
    { id: 'learning', name: 'Learning Coach', icon: BookOpen, color: '#3b82f6' },
    { id: 'goals', name: 'Goal Setting', icon: Target, color: '#8b5cf6' },
    { id: 'analytics', name: 'Progress Analysis', icon: TrendingUp, color: '#f59e0b' },
  ];

  // Initialize with welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      const welcomeMessage = {
        id: Date.now(),
        type: 'ai',
        content: `Hello ${user?.name || 'there'}! I'm your AI learning assistant. I can help you with:
        
• Creating personalized learning paths
• Analyzing your progress and performance
• Suggesting relevant mentors and sessions
• Setting and tracking learning goals
• Providing study tips and resources

What would you like to work on today?`,
        timestamp: new Date().toISOString(),
        suggestions: [
          'Create a learning path',
          'Analyze my progress',
          'Find a mentor',
          'Set learning goals'
        ]
      };
      setMessages([welcomeMessage]);
    }
  }, [isOpen, user, messages.length]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen && !isMinimized) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen, isMinimized]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Simulate AI response based on mode and context
      const aiResponse = await generateAIResponse(input.trim(), aiMode, context);
      
      setTimeout(() => {
        setMessages(prev => [...prev, aiResponse]);
        setIsLoading(false);
      }, 1500 + Math.random() * 1000); // Simulate processing time

    } catch (error) {
      console.error('AI Assistant Error:', error);
      const errorMessage = {
        id: Date.now(),
        type: 'ai',
        content: 'Sorry, I encountered an error. Please try again or contact support if the issue persists.',
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  const generateAIResponse = async (userInput, mode, context) => {
    // This would typically call your backend AI service
    // For now, we'll simulate intelligent responses
    
    const responses = {
      general: {
        'learning path': {
          content: `Based on your profile, I recommend a personalized learning path for ${context?.skill || 'web development'}:

**Phase 1: Foundations (2-3 weeks)**
• HTML/CSS fundamentals
• JavaScript basics
• Version control with Git

**Phase 2: Frontend Development (4-5 weeks)**
• React.js fundamentals
• State management
• Component lifecycle

**Phase 3: Backend Integration (3-4 weeks)**
• REST APIs
• Database basics
• Authentication

Would you like me to create this learning path and suggest mentors for each phase?`,
          suggestions: ['Create learning path', 'Find mentors', 'Set timeline']
        },
        'progress': {
          content: `Here's your learning progress analysis:

**Overall Progress: 73%**
• Completed Sessions: 12/15
• Active Learning Streak: 8 days
• Average Session Rating: 4.7/5

**Strengths:**
• Consistent attendance
• High engagement in React sessions
• Good progress in practical projects

**Areas for Improvement:**
• Backend concepts need more focus
• Consider more practice sessions
• Database fundamentals require attention

**Recommendations:**
• Book 2 more backend sessions this week
• Practice with coding challenges
• Join the SQL study group`,
          suggestions: ['Book backend session', 'Join study group', 'View detailed analytics']
        }
      },
      learning: {
        default: {
          content: `As your learning coach, I suggest focusing on active learning techniques:

**Study Strategy:**
• Use the Pomodoro Technique (25-min focused sessions)
• Practice spaced repetition for concepts
• Apply concepts immediately in projects

**This Week's Goals:**
• Complete 3 coding exercises
• Attend 2 mentoring sessions  
• Review and practice yesterday's concepts

**Recommended Resources:**
• Interactive coding platforms
• Project-based tutorials
• Peer programming sessions

What specific topic would you like to focus on?`,
          suggestions: ['Set study schedule', 'Find practice exercises', 'Book mentoring session']
        }
      },
      goals: {
        default: {
          content: `Let's set some SMART learning goals:

**Suggested Goals for This Month:**
1. **Technical Goal:** Master React hooks and context API
2. **Project Goal:** Build and deploy a full-stack application
3. **Networking Goal:** Connect with 3 industry professionals
4. **Learning Goal:** Complete 8 mentoring sessions

**Goal Tracking:**
• Weekly progress check-ins
• Milestone celebrations
• Adaptive goal adjustments

Which goal would you like to start with?`,
          suggestions: ['Set technical goal', 'Plan project', 'Schedule check-ins']
        }
      },
      analytics: {
        default: {
          content: `Here's your detailed learning analytics:

**Learning Velocity:** +15% this month
**Knowledge Retention:** 89% (Excellent!)
**Session Effectiveness:** 4.8/5 average rating

**Top Performing Areas:**
1. Frontend Development (95% mastery)
2. Problem Solving (88% mastery)  
3. Code Review (82% mastery)

**Growth Opportunities:**
1. Backend APIs (45% mastery)
2. Database Design (38% mastery)
3. DevOps Practices (25% mastery)

**Predictions:**
• At current pace, you'll master React in 2 weeks
• Backend proficiency expected in 6-8 weeks
• Full-stack competency target: 3 months

Would you like a detailed breakdown of any specific area?`,
          suggestions: ['Focus on backend', 'Detailed frontend analysis', 'Set learning targets']
        }
      }
    };

    // Simple keyword matching for demo
    const lowerInput = userInput.toLowerCase();
    const modeResponses = responses[mode] || responses.general;
    
    let response;
    if (lowerInput.includes('path') || lowerInput.includes('plan')) {
      response = modeResponses['learning path'] || modeResponses.default;
    } else if (lowerInput.includes('progress') || lowerInput.includes('analysis')) {
      response = modeResponses['progress'] || modeResponses.default;
    } else {
      response = modeResponses.default || modeResponses[Object.keys(modeResponses)[0]];
    }

    return {
      id: Date.now(),
      type: 'ai',
      content: response.content,
      timestamp: new Date().toISOString(),
      suggestions: response.suggestions || []
    };
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
    inputRef.current?.focus();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <div className={`ai-assistant ${isMinimized ? 'minimized' : ''}`}>
      {/* Header */}
      <div className="ai-header">
        <div className="ai-title">
          <Bot className="ai-icon" size={20} />
          <span>AI Learning Assistant</span>
          <div className="ai-status">
            <div className="status-dot online"></div>
            <span>Online</span>
          </div>
        </div>
        
        <div className="ai-controls">
          <select 
            value={aiMode} 
            onChange={(e) => setAiMode(e.target.value)}
            className="ai-mode-selector"
          >
            {aiModes.map(mode => (
              <option key={mode.id} value={mode.id}>
                {mode.name}
              </option>
            ))}
          </select>
          
          <button 
            onClick={() => setVoiceEnabled(!voiceEnabled)}
            className={`control-btn ${voiceEnabled ? 'active' : ''}`}
            title="Voice responses"
          >
            {voiceEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
          </button>
          
          <button 
            onClick={() => setIsMinimized(!isMinimized)}
            className="control-btn"
            title={isMinimized ? "Expand" : "Minimize"}
          >
            {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
          </button>
          
          <button 
            onClick={onToggle}
            className="control-btn close-btn"
            title="Close"
          >
            <X size={16} />
          </button>
        </div>
      </div>

      {/* Messages */}
      {!isMinimized && (
        <>
          <div className="ai-messages">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.type}`}>
                <div className="message-avatar">
                  {message.type === 'ai' ? (
                    <Bot size={16} />
                  ) : (
                    <User size={16} />
                  )}
                </div>
                
                <div className="message-content">
                  <div className={`message-bubble ${message.isError ? 'error' : ''}`}>
                    <pre className="message-text">{message.content}</pre>
                    <div className="message-time">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                  
                  {message.suggestions && message.suggestions.length > 0 && (
                    <div className="message-suggestions">
                      {message.suggestions.map((suggestion, index) => (
                        <button
                          key={index}
                          onClick={() => handleSuggestionClick(suggestion)}
                          className="suggestion-btn"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="message ai">
                <div className="message-avatar">
                  <Bot size={16} />
                </div>
                <div className="message-content">
                  <div className="message-bubble loading">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="ai-input">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your learning journey..."
              className="input-field"
              rows="1"
              disabled={isLoading}
            />
            <button 
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className="send-btn"
            >
              <Send size={18} />
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default AIAssistant;
