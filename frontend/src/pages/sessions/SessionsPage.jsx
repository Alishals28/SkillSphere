import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { 
  ArrowLeft,
  Calendar,
  Clock,
  User,
  Video,
  MessageSquare,
  FileText,
  Star,
  Download,
  Share2,
  Edit3,
  Trash2,
  CheckCircle,
  XCircle,
  AlertCircle,
  Play,
  Camera,
  Mic,
  Monitor,
  Settings
} from 'lucide-react';
import './SessionsPage.css';

const SessionsPage = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [rating, setRating] = useState(0);
  const [review, setReview] = useState('');
  const [showReviewModal, setShowReviewModal] = useState(false);

  // Mock session data
  useEffect(() => {
    setTimeout(() => {
      setSession({
        id: sessionId || 1,
        title: 'React Hooks Deep Dive',
        description: 'Comprehensive session covering useState, useEffect, useContext, and custom hooks with practical examples.',
        mentorName: 'Dr. Sarah Martinez',
        studentName: 'Alice Johnson',
        mentorAvatar: null,
        studentAvatar: null,
        date: new Date(2024, 11, 20, 14, 0),
        duration: 60,
        type: '1-on-1 Mentoring',
        status: 'confirmed',
        price: 45,
        meetingLink: 'https://meet.google.com/abc-def-ghi',
        recordingLink: null,
        materials: [
          { name: 'React Hooks Cheatsheet', type: 'pdf', url: '#' },
          { name: 'Practice Exercises', type: 'zip', url: '#' },
          { name: 'Code Examples', type: 'github', url: '#' }
        ],
        agenda: [
          'Introduction to React Hooks',
          'useState and useEffect basics',
          'useContext for state management',
          'Building custom hooks',
          'Best practices and common pitfalls',
          'Q&A and code review'
        ],
        notes: 'Please prepare by reviewing the pre-session materials. Come with specific questions about your current project.',
        chatHistory: [
          {
            id: 1,
            sender: 'Dr. Sarah Martinez',
            message: 'Hi Alice! Looking forward to our session today. Did you get a chance to review the materials I sent?',
            timestamp: new Date(2024, 11, 19, 15, 30),
            isMe: user?.role === 'mentor'
          },
          {
            id: 2,
            sender: 'Alice Johnson',
            message: 'Yes, I went through the cheatsheet. I have some questions about useEffect cleanup functions.',
            timestamp: new Date(2024, 11, 19, 16, 15),
            isMe: user?.role === 'learner'
          },
          {
            id: 3,
            sender: 'Dr. Sarah Martinez',
            message: 'Perfect! That\'s exactly what we\'ll cover. I\'ll prepare some examples to demonstrate different cleanup scenarios.',
            timestamp: new Date(2024, 11, 19, 16, 20),
            isMe: user?.role === 'mentor'
          }
        ],
        rating: 4.8,
        reviews: [
          {
            id: 1,
            reviewer: 'Alice Johnson',
            rating: 5,
            comment: 'Excellent session! Sarah explained hooks concepts very clearly with practical examples.',
            date: new Date(2024, 11, 20, 16, 0)
          }
        ]
      });
      setLoading(false);
    }, 1000);
  }, [sessionId, user]);

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', { 
      weekday: 'long',
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed': return '#10b981';
      case 'pending': return '#f59e0b';
      case 'cancelled': return '#ef4444';
      case 'completed': return '#6366f1';
      case 'in-progress': return '#14b8a6';
      default: return '#6b7280';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'confirmed': return <CheckCircle size={20} />;
      case 'pending': return <AlertCircle size={20} />;
      case 'cancelled': return <XCircle size={20} />;
      case 'completed': return <CheckCircle size={20} />;
      case 'in-progress': return <Play size={20} />;
      default: return <Clock size={20} />;
    }
  };

  const joinSession = () => {
    if (session.meetingLink) {
      window.open(session.meetingLink, '_blank');
    } else {
      alert('Meeting link not available yet');
    }
  };

  const downloadMaterial = (material) => {
    alert(`Downloading ${material.name}...`);
  };

  const shareSession = () => {
    navigator.clipboard.writeText(window.location.href);
    alert('Session link copied to clipboard!');
  };

  const submitReview = () => {
    if (rating === 0) {
      alert('Please select a rating');
      return;
    }

    const newReview = {
      id: session.reviews.length + 1,
      reviewer: user?.name || 'Anonymous',
      rating: rating,
      comment: review,
      date: new Date()
    };

    setSession(prev => ({
      ...prev,
      reviews: [...prev.reviews, newReview]
    }));

    setShowReviewModal(false);
    setRating(0);
    setReview('');
    alert('Review submitted successfully!');
  };

  if (loading) {
    return (
      <div className="sessions-page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading session...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="sessions-page">
        <div className="error-container">
          <h2>Session not found</h2>
          <p>The session you're looking for doesn't exist or has been removed.</p>
          <button onClick={() => navigate('/schedule')}>
            <ArrowLeft size={16} />
            Back to Schedule
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="sessions-page">
      <div className="sessions-container">
        {/* Header */}
        <div className="page-header">
          <div className="header-nav">
            <button 
              className="back-btn"
              onClick={() => navigate('/schedule')}
            >
              <ArrowLeft size={20} />
              Back to Schedule
            </button>
            
            <div className="header-actions">
              <button className="share-btn" onClick={shareSession}>
                <Share2 size={16} />
                Share
              </button>
              
              {user?.role === 'mentor' && session.status !== 'completed' && (
                <button className="edit-btn">
                  <Edit3 size={16} />
                  Edit
                </button>
              )}
            </div>
          </div>

          <div className="session-header">
            <div className="session-info">
              <h1>{session.title}</h1>
              <p className="session-description">{session.description}</p>
              
              <div className="session-meta">
                <div className="meta-item">
                  <Calendar size={18} />
                  <span>{formatDate(session.date)}</span>
                </div>
                <div className="meta-item">
                  <Clock size={18} />
                  <span>{formatTime(session.date)} ({session.duration} min)</span>
                </div>
                <div className="meta-item">
                  <User size={18} />
                  <span>{session.type}</span>
                </div>
              </div>
            </div>

            <div className="session-status-card">
              <div 
                className="status-indicator"
                style={{ color: getStatusColor(session.status) }}
              >
                {getStatusIcon(session.status)}
                <span>{session.status.replace('-', ' ')}</span>
              </div>
              
              <div className="session-price">
                ${session.price}
              </div>

              {session.status === 'confirmed' && (
                <button 
                  className="join-session-btn"
                  onClick={joinSession}
                >
                  <Video size={20} />
                  Join Session
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Participant Info */}
        <div className="participants-section">
          <div className="participant-card">
            <div className="participant-avatar">
              {session.mentorAvatar ? (
                <img src={session.mentorAvatar} alt={session.mentorName} />
              ) : (
                <div className="avatar-placeholder">
                  {session.mentorName.charAt(0)}
                </div>
              )}
              <div className="role-badge mentor">Mentor</div>
            </div>
            <div className="participant-info">
              <h3>{session.mentorName}</h3>
              <p>Senior Frontend Developer</p>
              <div className="participant-stats">
                <span>⭐ 4.9 (127 reviews)</span>
                <span>📚 245 sessions</span>
              </div>
            </div>
            <button className="message-participant-btn">
              <MessageSquare size={16} />
              Message
            </button>
          </div>

          <div className="participant-card">
            <div className="participant-avatar">
              {session.studentAvatar ? (
                <img src={session.studentAvatar} alt={session.studentName} />
              ) : (
                <div className="avatar-placeholder">
                  {session.studentName.charAt(0)}
                </div>
              )}
              <div className="role-badge learner">Learner</div>
            </div>
            <div className="participant-info">
              <h3>{session.studentName}</h3>
              <p>Frontend Developer</p>
              <div className="participant-stats">
                <span>🎯 15 sessions completed</span>
                <span>⏱️ Member since 2024</span>
              </div>
            </div>
            <button className="message-participant-btn">
              <MessageSquare size={16} />
              Message
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button 
            className={activeTab === 'overview' ? 'active' : ''}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={activeTab === 'materials' ? 'active' : ''}
            onClick={() => setActiveTab('materials')}
          >
            Materials
          </button>
          <button 
            className={activeTab === 'chat' ? 'active' : ''}
            onClick={() => setActiveTab('chat')}
          >
            Chat
          </button>
          <button 
            className={activeTab === 'reviews' ? 'active' : ''}
            onClick={() => setActiveTab('reviews')}
          >
            Reviews
          </button>
        </div>

        {/* Tab Content */}
        <div className="tab-content">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="overview-content">
              <div className="overview-grid">
                <div className="agenda-section">
                  <h3>Session Agenda</h3>
                  <ul className="agenda-list">
                    {session.agenda.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </div>

                <div className="notes-section">
                  <h3>Session Notes</h3>
                  <div className="notes-content">
                    <p>{session.notes}</p>
                  </div>
                </div>

                <div className="tech-check-section">
                  <h3>Tech Check</h3>
                  <div className="tech-items">
                    <div className="tech-item">
                      <Camera size={20} />
                      <span>Camera</span>
                      <div className="status-dot green"></div>
                    </div>
                    <div className="tech-item">
                      <Mic size={20} />
                      <span>Microphone</span>
                      <div className="status-dot green"></div>
                    </div>
                    <div className="tech-item">
                      <Monitor size={20} />
                      <span>Screen Share</span>
                      <div className="status-dot green"></div>
                    </div>
                  </div>
                  <button className="test-setup-btn">
                    <Settings size={16} />
                    Test Setup
                  </button>
                </div>

                {session.recordingLink && (
                  <div className="recording-section">
                    <h3>Session Recording</h3>
                    <div className="recording-card">
                      <Play size={24} />
                      <div className="recording-info">
                        <h4>Session Recording</h4>
                        <p>Duration: {session.duration} minutes</p>
                      </div>
                      <button onClick={() => window.open(session.recordingLink, '_blank')}>
                        Watch
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Materials Tab */}
          {activeTab === 'materials' && (
            <div className="materials-content">
              <div className="materials-header">
                <h3>Session Materials</h3>
                <p>Resources and files for this session</p>
              </div>
              
              <div className="materials-grid">
                {session.materials.map((material, index) => (
                  <div key={index} className="material-card">
                    <div className="material-icon">
                      <FileText size={24} />
                    </div>
                    <div className="material-info">
                      <h4>{material.name}</h4>
                      <p>{material.type.toUpperCase()} file</p>
                    </div>
                    <button 
                      className="download-material-btn"
                      onClick={() => downloadMaterial(material)}
                    >
                      <Download size={16} />
                      Download
                    </button>
                  </div>
                ))}
              </div>

              {session.materials.length === 0 && (
                <div className="no-materials">
                  <FileText className="no-materials-icon" />
                  <h3>No materials yet</h3>
                  <p>Materials will be available before the session starts</p>
                </div>
              )}
            </div>
          )}

          {/* Chat Tab */}
          {activeTab === 'chat' && (
            <div className="chat-content">
              <div className="chat-header">
                <h3>Session Chat</h3>
                <p>Communicate with your {user?.role === 'mentor' ? 'student' : 'mentor'}</p>
              </div>
              
              <div className="chat-messages">
                {session.chatHistory.map((message) => (
                  <div 
                    key={message.id} 
                    className={`message ${message.isMe ? 'own-message' : 'other-message'}`}
                  >
                    <div className="message-avatar">
                      {message.sender.charAt(0)}
                    </div>
                    <div className="message-content">
                      <div className="message-header">
                        <span className="sender-name">{message.sender}</span>
                        <span className="message-time">
                          {message.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                      <p>{message.message}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="chat-input">
                <input 
                  type="text" 
                  placeholder="Type your message..."
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      alert('Message sent!');
                      e.target.value = '';
                    }
                  }}
                />
                <button>Send</button>
              </div>
            </div>
          )}

          {/* Reviews Tab */}
          {activeTab === 'reviews' && (
            <div className="reviews-content">
              <div className="reviews-header">
                <h3>Session Reviews</h3>
                {session.status === 'completed' && user?.role === 'learner' && (
                  <button 
                    className="add-review-btn"
                    onClick={() => setShowReviewModal(true)}
                  >
                    <Star size={16} />
                    Add Review
                  </button>
                )}
              </div>

              <div className="reviews-list">
                {session.reviews.map((review) => (
                  <div key={review.id} className="review-card">
                    <div className="review-header">
                      <div className="reviewer-info">
                        <div className="reviewer-avatar">
                          {review.reviewer.charAt(0)}
                        </div>
                        <div>
                          <h4>{review.reviewer}</h4>
                          <div className="review-rating">
                            {[...Array(5)].map((_, i) => (
                              <Star 
                                key={i} 
                                size={16} 
                                fill={i < review.rating ? 'currentColor' : 'none'}
                                className={i < review.rating ? 'filled' : ''}
                              />
                            ))}
                          </div>
                        </div>
                      </div>
                      <span className="review-date">
                        {review.date.toLocaleDateString()}
                      </span>
                    </div>
                    <p className="review-comment">{review.comment}</p>
                  </div>
                ))}
              </div>

              {session.reviews.length === 0 && (
                <div className="no-reviews">
                  <Star className="no-reviews-icon" />
                  <h3>No reviews yet</h3>
                  <p>Reviews will appear after the session is completed</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Review Modal */}
      {showReviewModal && (
        <div className="modal-overlay" onClick={() => setShowReviewModal(false)}>
          <div className="review-modal" onClick={e => e.stopPropagation()}>
            <h3>Rate this session</h3>
            
            <div className="rating-input">
              <span>Rating:</span>
              <div className="stars">
                {[1, 2, 3, 4, 5].map(star => (
                  <Star
                    key={star}
                    size={24}
                    fill={star <= rating ? 'currentColor' : 'none'}
                    className={star <= rating ? 'filled' : ''}
                    onClick={() => setRating(star)}
                  />
                ))}
              </div>
            </div>

            <textarea
              placeholder="Share your experience..."
              value={review}
              onChange={(e) => setReview(e.target.value)}
              rows={4}
            />

            <div className="modal-actions">
              <button 
                className="cancel-btn"
                onClick={() => setShowReviewModal(false)}
              >
                Cancel
              </button>
              <button 
                className="submit-btn"
                onClick={submitReview}
              >
                Submit Review
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SessionsPage;
