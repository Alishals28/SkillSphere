import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { dashboardAPI } from '../../services/api';
import { 
  Calendar, 
  Users, 
  Star, 
  DollarSign, 
  Clock, 
  MessageSquare,
  TrendingUp,
  Award,
  ChevronRight,
  User,
  BookOpen,
  AlertCircle,
  Settings,
  Bell,
  BarChart3
} from 'lucide-react';
import './Dashboard.css';

const MentorDashboard = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [messagesDropdownOpen, setMessagesDropdownOpen] = useState(false);
  const [notificationDropdownOpen, setNotificationDropdownOpen] = useState(false);

  // Mock messages data
  const mockMessages = [
    {
      id: 1,
      sender: 'Sarah Johnson',
      avatar: null,
      message: 'Hi! I have a question about the React hooks we discussed yesterday...',
      time: '2 min ago',
      unread: true
    },
    {
      id: 2,
      sender: 'Mike Chen',
      avatar: null,
      message: 'Thank you for the Python session! The examples were really helpful.',
      time: '15 min ago',
      unread: true
    },
    {
      id: 3,
      sender: 'Emma Davis',
      avatar: null,
      message: 'Can we reschedule tomorrow\'s session to 3 PM instead?',
      time: '1 hour ago',
      unread: false
    },
    {
      id: 4,
      sender: 'Alex Wilson',
      avatar: null,
      message: 'The JavaScript debugging techniques you showed me worked perfectly!',
      time: '2 hours ago',
      unread: false
    },
    {
      id: 5,
      sender: 'Lisa Brown',
      avatar: null,
      message: 'Could you recommend some advanced CSS resources?',
      time: '4 hours ago',
      unread: false
    },
    {
      id: 6,
      sender: 'Tom Garcia',
      avatar: null,
      message: 'Looking forward to our Node.js session next week!',
      time: '1 day ago',
      unread: false
    },
    {
      id: 7,
      sender: 'Nina Patel',
      avatar: null,
      message: 'The database design concepts are finally clicking. Thanks!',
      time: '2 days ago',
      unread: false
    }
  ];

  // Mock notifications data for mentors
  const mockNotifications = [
    {
      id: 1,
      type: 'booking',
      title: 'New Session Booked',
      message: 'Sarah Johnson booked a React session for tomorrow at 3 PM',
      time: '10 min ago',
      unread: true,
      icon: Calendar
    },
    {
      id: 2,
      type: 'review',
      title: 'New Review Received',
      message: 'Mike Chen left you a 5-star review for your Python session',
      time: '1 hour ago',
      unread: true,
      icon: Star
    }
  ];

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (messagesDropdownOpen && !event.target.closest('.messages-dropdown') && !event.target.closest('.messages-btn')) {
        setMessagesDropdownOpen(false);
      }
      if (notificationDropdownOpen && !event.target.closest('.notification-dropdown') && !event.target.closest('.notifications-btn')) {
        setNotificationDropdownOpen(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [messagesDropdownOpen, notificationDropdownOpen]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const data = await dashboardAPI.getMentorDashboard();
        setDashboardData(data);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data');
        // Set mock data for development
        setDashboardData({
          stats: {
            total_sessions: 127,
            total_students: 45,
            average_rating: 4.8,
            total_earnings: 3850
          },
          upcoming_sessions: [
            {
              id: 1,
              student_name: 'Sarah Johnson',
              subject: 'React.js Fundamentals',
              date: '2024-12-15',
              time: '14:00',
              duration: 60,
              meeting_link: 'https://meet.google.com/abc-def-ghi'
            },
            {
              id: 2,
              student_name: 'Mike Wilson',
              subject: 'Python for Data Science',
              date: '2024-12-15',
              time: '16:30',
              duration: 90,
              meeting_link: 'https://meet.google.com/xyz-123-456'
            }
          ],
          recent_reviews: [
            {
              id: 1,
              student_name: 'Alex Chen',
              rating: 5,
              comment: 'Excellent explanation of React concepts!',
              date: '2024-12-10',
              subject: 'React.js'
            },
            {
              id: 2,
              student_name: 'Emma Davis',
              rating: 5,
              comment: 'Very helpful and patient mentor.',
              date: '2024-12-08',
              subject: 'JavaScript'
            }
          ]
        });
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-page">
        <div className="error-container">
          <AlertCircle size={48} />
          <h2>Something went wrong</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const stats = dashboardData?.stats || {};
  const upcomingSessions = dashboardData?.upcoming_sessions || [];
  const recentReviews = dashboardData?.recent_reviews || [];

  return (
    <div className="dashboard-page">
      {/* Header Section */}
      <div className="dashboard-header">
        <div className="header-content">
          <div className="welcome-section">
            <h1>Welcome back, {user?.first_name || 'Mentor'}!</h1>
            <p>Here's what's happening with your mentoring today</p>
          </div>
          <div className="header-actions">
            <button 
              className="icon-btn notifications-btn"
              onClick={() => setNotificationDropdownOpen(!notificationDropdownOpen)}
            >
              <Bell size={24} style={{ stroke: 'white', fill: 'none', strokeWidth: 2 }} />
              <span className="notification-badge">{mockNotifications.filter(notif => notif.unread).length}</span>
            </button>
            <button 
              className="icon-btn messages-btn"
              onClick={() => setMessagesDropdownOpen(!messagesDropdownOpen)}
            >
              <MessageSquare size={24} style={{ stroke: 'white', fill: 'none', strokeWidth: 2 }} />
              <span className="notification-badge">{mockMessages.filter(msg => msg.unread).length}</span>
            </button>
            <button className="icon-btn profile-btn" onClick={() => window.location.href = '/profile'}>
              <User size={24} style={{ stroke: 'white', fill: 'none', strokeWidth: 2 }} />
            </button>
          </div>

          {/* Messages Dropdown */}
          {messagesDropdownOpen && (
            <div className="messages-dropdown">
              <div className="dropdown-header">
                <h3>Messages</h3>
                <span className="unread-count">{mockMessages.filter(msg => msg.unread).length} unread</span>
              </div>
              <div className="messages-list">
                {mockMessages.map((message) => (
                  <div key={message.id} className={`message-item ${message.unread ? 'unread' : ''}`}>
                    <div className="message-avatar">
                      <User size={16} />
                    </div>
                    <div className="message-content">
                      <div className="message-header">
                        <span className="sender-name">{message.sender}</span>
                        <span className="message-time">{message.time}</span>
                      </div>
                      <p className="message-preview">{message.message}</p>
                    </div>
                    {message.unread && <div className="unread-indicator"></div>}
                  </div>
                ))}
              </div>
              <div className="dropdown-footer">
                <button className="view-all-btn" onClick={() => window.location.href = '/messages'}>View All Messages</button>
              </div>
            </div>
          )}

          {/* Notifications Dropdown */}
          {notificationDropdownOpen && (
            <div className="notifications-dropdown">
              <div className="dropdown-header">
                <h3>Notifications</h3>
                <span className="unread-count">{mockNotifications.filter(notif => notif.unread).length} unread</span>
              </div>
              <div className="notifications-list">
                {mockNotifications.map((notification) => (
                  <div key={notification.id} className={`notification-item ${notification.unread ? 'unread' : ''}`}>
                    <div className="notification-icon">
                      <notification.icon size={16} />
                    </div>
                    <div className="notification-content">
                      <div className="notification-header">
                        <span className="notification-title">{notification.title}</span>
                        <span className="notification-time">{notification.time}</span>
                      </div>
                      <p className="notification-message">{notification.message}</p>
                    </div>
                    {notification.unread && <div className="unread-indicator"></div>}
                  </div>
                ))}
              </div>
              <div className="dropdown-footer">
                <button className="view-all-btn" onClick={() => window.location.href = '/notifications'}>View All Notifications</button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions Bar */}
      <div className="quick-actions">
        <button 
          className="action-btn primary"
          onClick={() => window.location.href = '/schedule'}
        >
          <Calendar size={20} />
          View Schedule
        </button>
        
        <button 
          className="action-btn secondary"
          onClick={() => window.location.href = '/students'}
        >
          <Users size={20} />
          My Students
        </button>
        
        <button 
          className="action-btn secondary"
          onClick={() => window.location.href = '/reviews'}
        >
          <Star size={20} />
          All Reviews
        </button>
        
        <button 
          className="action-btn secondary"
          onClick={() => window.location.href = '/analytics'}
        >
          <BarChart3 size={20} />
          Analytics
        </button>
        
        <button 
          className="action-btn secondary"
          onClick={() => window.location.href = '/profile'}
        >
          <User size={20} />
          Profile
        </button>
        
        <button 
          className="action-btn secondary"
          onClick={() => window.location.href = '/settings'}
        >
          <Settings size={20} />
          Settings
        </button>
      </div>

      {/* Stats Grid */}
      <div className="stats-section">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon sessions">
              <Calendar size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-number">{stats.total_sessions || 0}</div>
              <div className="stat-label">Total Sessions</div>
              <div className="stat-change positive">+12% this month</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon students">
              <Users size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-number">{stats.total_students || 0}</div>
              <div className="stat-label">Students Taught</div>
              <div className="stat-change positive">+8% this month</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon rating">
              <Star size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-number">{stats.average_rating || 0}</div>
              <div className="stat-label">Average Rating</div>
              <div className="stat-change positive">+0.2 this month</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon earnings">
              <DollarSign size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-number">${stats.total_earnings || 0}</div>
              <div className="stat-label">Total Earnings</div>
              <div className="stat-change positive">+25% this month</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="main-content">
        <div className="content-left">
          {/* Upcoming Sessions */}
          <div className="dashboard-card">
            <div className="card-header">
              <h3 className="card-title">
                <Calendar size={20} />
                Upcoming Sessions
              </h3>
              <button 
                className="card-action"
                onClick={() => window.location.href = '/schedule'}
              >
                View All <ChevronRight size={16} />
              </button>
            </div>
            <div className="card-content">
              {upcomingSessions && upcomingSessions.length > 0 ? (
                <div className="sessions-list">
                  {upcomingSessions.map(session => (
                    <div key={session.id} className="session-item">
                      <div className="session-time">
                        <div className="session-date">{new Date(session.date).toLocaleDateString()}</div>
                        <div className="session-hour">{session.time}</div>
                      </div>
                      <div className="session-details">
                        <h4 className="session-title">{session.subject}</h4>
                        <p className="session-student">with {session.student_name}</p>
                        <span className="session-duration">
                          <Clock size={14} />
                          {session.duration} minutes
                        </span>
                      </div>
                      <div className="session-actions">
                        <button 
                          className="btn-join"
                          onClick={() => window.location.href = `/session/${session.id || '1'}/join`}
                        >
                          Join Session
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <Calendar size={48} />
                  <h4>No upcoming sessions</h4>
                  <p>Your next sessions will appear here</p>
                </div>
              )}
            </div>
          </div>

          {/* Recent Reviews */}
          <div className="dashboard-card">
            <div className="card-header">
              <h3 className="card-title">
                <Star size={20} />
                Recent Reviews
              </h3>
              <button 
                className="card-action"
                onClick={() => window.location.href = '/reviews'}
              >
                View All <ChevronRight size={16} />
              </button>
            </div>
            <div className="card-content">
              {recentReviews && recentReviews.length > 0 ? (
                <div className="reviews-list">
                  {recentReviews.map(review => (
                    <div key={review.id} className="review-item">
                      <div className="review-header">
                        <div className="review-student">{review.student_name}</div>
                        <div className="review-rating">
                          {[...Array(5)].map((_, i) => (
                            <Star 
                              key={i} 
                              size={16} 
                              fill={i < review.rating ? '#fbbf24' : 'none'}
                              color={i < review.rating ? '#fbbf24' : '#d1d5db'}
                            />
                          ))}
                        </div>
                      </div>
                      <p className="review-comment">"{review.comment}"</p>
                      <div className="review-meta">
                        <span className="review-subject">{review.subject}</span>
                        <span className="review-date">{new Date(review.date).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <Star size={48} />
                  <h4>No reviews yet</h4>
                  <p>Reviews from your students will appear here</p>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="content-right">
          {/* Performance Insights */}
          <div className="dashboard-card">
            <div className="card-header">
              <h3 className="card-title">
                <TrendingUp size={20} />
                Performance Insights
              </h3>
            </div>
            <div className="card-content">
              <div className="insights-list">
                <div className="insight-item">
                  <div className="insight-icon success">
                    <TrendingUp size={16} />
                  </div>
                  <div className="insight-content">
                    <h4>Great Progress!</h4>
                    <p>Your rating increased by 0.2 points this month</p>
                  </div>
                </div>
                
                <div className="insight-item">
                  <div className="insight-icon info">
                    <Users size={16} />
                  </div>
                  <div className="insight-content">
                    <h4>New Students</h4>
                    <p>You gained 3 new students this week</p>
                  </div>
                </div>
                
                <div className="insight-item">
                  <div className="insight-icon warning">
                    <Clock size={16} />
                  </div>
                  <div className="insight-content">
                    <h4>Peak Hours</h4>
                    <p>Most bookings are between 2-6 PM</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Messages */}
          <div className="dashboard-card">
            <div className="card-header">
              <h3 className="card-title">
                <MessageSquare size={20} />
                Recent Messages
              </h3>
              <button 
                className="card-action"
                onClick={() => window.location.href = '/messages'}
              >
                View All <ChevronRight size={16} />
              </button>
            </div>
            <div className="card-content">
              <div className="messages-list">
                <div className="message-item">
                  <div className="message-avatar">SJ</div>
                  <div className="message-content">
                    <div className="message-sender">Sarah Johnson</div>
                    <div className="message-text">Thank you for the great session!</div>
                    <div className="message-time">2 hours ago</div>
                  </div>
                </div>
                
                <div className="message-item">
                  <div className="message-avatar">MW</div>
                  <div className="message-content">
                    <div className="message-sender">Mike Wilson</div>
                    <div className="message-text">Can we reschedule tomorrow's session?</div>
                    <div className="message-time">4 hours ago</div>
                  </div>
                </div>
                
                <div className="message-item">
                  <div className="message-avatar">ED</div>
                  <div className="message-content">
                    <div className="message-sender">Emma Davis</div>
                    <div className="message-text">Looking forward to our next session</div>
                    <div className="message-time">1 day ago</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MentorDashboard;
