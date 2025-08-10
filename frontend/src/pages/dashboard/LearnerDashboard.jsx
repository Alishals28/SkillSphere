import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { dashboardAPI } from '../../services/api';
import { 
  Calendar, 
  Users, 
  Trophy, 
  BookOpen, 
  Clock, 
  Target, 
  Star,
  TrendingUp,
  Play,
  Award,
  MessageCircle,
  MessageSquare,
  ChevronRight,
  Loader,
  User,
  Settings,
  AlertCircle,
  Bell,
  BarChart3
} from 'lucide-react';
import './Dashboard.css';

const LearnerDashboard = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [messagesDropdownOpen, setMessagesDropdownOpen] = useState(false);
  const [notificationDropdownOpen, setNotificationDropdownOpen] = useState(false);

  // Mock messages data for learners (different senders - mentors)
  const mockMessages = [
    {
      id: 1,
      sender: 'Dr. Sarah Martinez',
      avatar: null,
      message: 'Great progress on your React project! I\'ve reviewed your code and left some feedback.',
      time: '5 min ago',
      unread: true
    },
    {
      id: 2,
      sender: 'Prof. Michael Chen',
      avatar: null,
      message: 'Don\'t forget about our Python session tomorrow at 2 PM. Bring your questions!',
      time: '20 min ago',
      unread: true
    },
    {
      id: 3,
      sender: 'Emma Thompson',
      avatar: null,
      message: 'The CSS Grid tutorial I mentioned is now available in your resources.',
      time: '1 hour ago',
      unread: false
    },
    {
      id: 4,
      sender: 'Alex Rodriguez',
      avatar: null,
      message: 'Excellent work on the JavaScript assignment! You\'re really improving.',
      time: '3 hours ago',
      unread: false
    },
    {
      id: 5,
      sender: 'Dr. Lisa Wang',
      avatar: null,
      message: 'I\'ve scheduled our database design session for next Tuesday.',
      time: '5 hours ago',
      unread: false
    },
    {
      id: 6,
      sender: 'James Wilson',
      avatar: null,
      message: 'The Node.js resources you requested are now in your learning path.',
      time: '1 day ago',
      unread: false
    },
    {
      id: 7,
      sender: 'Maria Garcia',
      avatar: null,
      message: 'Keep up the great work! Your dedication is really showing in your progress.',
      time: '2 days ago',
      unread: false
    }
  ];

  // Mock notifications data for learners
  const mockNotifications = [
    {
      id: 1,
      type: 'session',
      title: 'Session Reminder',
      message: 'You have a JavaScript session with Prof. Chen in 30 minutes',
      time: '30 min',
      unread: true,
      icon: Calendar
    },
    {
      id: 2,
      type: 'achievement',
      title: 'New Badge Earned!',
      message: 'Congratulations! You earned the "React Basics" badge',
      time: '2 hours ago',
      unread: true,
      icon: Trophy
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
        const data = await dashboardAPI.getLearnerDashboard();
        setDashboardData(data);
      } catch (err) {
        console.error('Dashboard fetch error:', err);
        setError('Failed to load dashboard data');
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
          <Loader className="loading-spinner" />
          <p>Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-page">
        <div className="error-container">
          <AlertCircle className="error-icon" />
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-btn">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const stats = dashboardData?.stats || {};
  const upcomingSessions = dashboardData?.upcoming_sessions || [];
  const recommendedMentors = dashboardData?.recommended_mentors || [];
  const recentActivity = dashboardData?.recent_activity || [];

  return (
    <div className="dashboard-page">
      {/* Header Section */}
      <div className="dashboard-header">
        <div className="header-content">
          <div className="welcome-section">
            <h1>Welcome back, {user?.first_name || 'Learner'}!</h1>
            <p>Continue your learning journey and achieve your goals</p>
          </div>
          <div className="header-stats">
            <div className="stat-card">
              <div className="stat-icon sessions">
                <Calendar />
              </div>
              <div className="stat-number">{stats.total_sessions || 0}</div>
              <div className="stat-label">Sessions</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon hours">
                <Clock />
              </div>
              <div className="stat-number">{stats.total_hours || 0}</div>
              <div className="stat-label">Hours Learned</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon skills">
                <Target />
              </div>
              <div className="stat-number">{stats.skills_learned || 0}</div>
              <div className="stat-label">Skills</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon progress">
                <TrendingUp />
              </div>
              <div className="stat-number">{stats.progress_score || 0}%</div>
              <div className="stat-label">Progress</div>
            </div>
          </div>

          <div className="header-actions">
            <button 
              className="icon-btn notifications-btn"
              onClick={() => setNotificationDropdownOpen(!notificationDropdownOpen)}
            >
              <Bell size={24} style={{ stroke: 'white', fill: 'none', strokeWidth: 2 }} />
              <span className="notification-badge">2</span>
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

      {/* Quick Actions */}
      <div className="quick-actions">
        <button className="action-btn primary" onClick={() => window.location.href = '/book-session'}>
          <Calendar size={20} />
          Book a Session
        </button>
        <button className="action-btn secondary" onClick={() => window.location.href = '/mentors'}>
          <Users size={20} />
          Browse Mentors
        </button>
        <button className="action-btn secondary" onClick={() => window.location.href = '/notifications'}>
          <Bell size={20} />
          Notifications
        </button>
        <button className="action-btn secondary" onClick={() => window.location.href = '/analytics'}>
          <BarChart3 size={20} />
          Analytics
        </button>
        <button className="action-btn secondary" onClick={() => window.location.href = '/profile'}>
          <User size={20} />
          Profile
        </button>
        <button className="action-btn secondary" onClick={() => window.location.href = '/settings'}>
          <Settings size={20} />
          Settings
        </button>
      </div>

      {/* Main Dashboard Grid */}
      <div className="dashboard-grid">
        {/* Upcoming Sessions */}
        <div className="dashboard-card upcoming-sessions">
          <div className="card-header">
            <h3 className="card-title">
              <div className="card-icon">
                <Calendar size={20} />
              </div>
              Upcoming Sessions
            </h3>
            <ChevronRight size={20} />
          </div>
          <div className="card-content">
            {upcomingSessions.length > 0 ? (
              <div className="sessions-list">
                {upcomingSessions.slice(0, 3).map((session, index) => (
                  <div key={index} className="session-item">
                    <div className="session-info">
                      <h4>{session.topic || 'Session'}</h4>
                      <p>with {session.mentor_name || 'Mentor'}</p>
                      <span className="session-time">
                        {new Date(session.scheduled_time).toLocaleDateString()} at{' '}
                        {new Date(session.scheduled_time).toLocaleTimeString([], { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </span>
                    </div>
                    <button 
                      className="btn btn-sm btn-primary"
                      onClick={() => window.location.href = `/session/${session.id || '1'}/join`}
                    >
                      <Play size={16} />
                      Join
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <Calendar className="empty-icon" />
                <p>No upcoming sessions</p>
                <button 
                  className="btn btn-primary"
                  onClick={() => window.location.href = '/book-session'}
                >
                  Book Your First Session
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Recommended Mentors */}
        <div className="dashboard-card recommended-mentors">
          <div className="card-header">
            <h3 className="card-title">
              <div className="card-icon">
                <Users size={20} />
              </div>
              Recommended Mentors
            </h3>
            <ChevronRight size={20} />
          </div>
          <div className="card-content">
            {recommendedMentors.length > 0 ? (
              <div className="mentors-list">
                {recommendedMentors.slice(0, 3).map((mentor, index) => (
                  <div key={index} className="mentor-item">
                    <div className="mentor-avatar">
                      {mentor.profile_picture ? (
                        <img src={mentor.profile_picture} alt={mentor.name} />
                      ) : (
                        <div className="avatar-placeholder">
                          {mentor.name?.charAt(0) || 'M'}
                        </div>
                      )}
                    </div>
                    <div className="mentor-info">
                      <h4>{mentor.name || 'Mentor'}</h4>
                      <p>{mentor.expertise || 'Programming'}</p>
                      <div className="mentor-rating">
                        <Star size={16} fill="currentColor" />
                        <span>{mentor.rating || 5.0}</span>
                      </div>
                    </div>
                    <button 
                      className="btn btn-sm btn-secondary"
                      onClick={() => window.location.href = `/mentor/${mentor.id || '1'}`}
                    >
                      View Profile
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <Users className="empty-icon" />
                <p>No mentor recommendations yet</p>
                <p className="empty-subtitle">Complete your profile to get personalized recommendations</p>
              </div>
            )}
          </div>
        </div>

        {/* Learning Progress */}
        <div className="dashboard-card progress-section">
          <div className="card-header">
            <h3 className="card-title">
              <div className="card-icon">
                <TrendingUp size={20} />
              </div>
              Learning Progress
            </h3>
          </div>
          <div className="card-content">
            <div className="progress-stats">
              <div className="progress-item">
                <div className="progress-info">
                  <span className="progress-label">Overall Progress</span>
                  <span className="progress-value">{stats.progress_score || 0}%</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${stats.progress_score || 0}%` }}
                  />
                </div>
              </div>
              <div className="progress-item">
                <div className="progress-info">
                  <span className="progress-label">Sessions Completed</span>
                  <span className="progress-value">{stats.completed_sessions || 0}/{stats.total_sessions || 0}</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${((stats.completed_sessions || 0) / (stats.total_sessions || 1)) * 100}%` }}
                  />
                </div>
              </div>
            </div>
            <div className="achievements">
              <h4>Recent Achievements</h4>
              <div className="badges-grid">
                <div className="badge-item">
                  <Trophy className="badge-icon" />
                  <span>First Session</span>
                </div>
                <div className="badge-item">
                  <Award className="badge-icon" />
                  <span>Quick Learner</span>
                </div>
                <div className="badge-item">
                  <Target className="badge-icon" />
                  <span>Goal Setter</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="dashboard-card recent-activity">
          <div className="card-header">
            <h3 className="card-title">
              <div className="card-icon">
                <Clock size={20} />
              </div>
              Recent Activity
            </h3>
          </div>
          <div className="card-content">
            {recentActivity.length > 0 ? (
              <div className="activity-list">
                {recentActivity.slice(0, 5).map((activity, index) => (
                  <div key={index} className="activity-item">
                    <div className="activity-icon">
                      {activity.type === 'session' && <Calendar size={16} />}
                      {activity.type === 'message' && <MessageCircle size={16} />}
                      {activity.type === 'achievement' && <Trophy size={16} />}
                    </div>
                    <div className="activity-info">
                      <p>{activity.description || 'Activity'}</p>
                      <span className="activity-time">
                        {new Date(activity.timestamp).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <Clock className="empty-icon" />
                <p>No recent activity</p>
                <p className="empty-subtitle">Your activity will appear here</p>
              </div>
            )}
          </div>
        </div>

        {/* Learning Goals */}
        <div className="dashboard-card learning-goals">
          <div className="card-header">
            <h3 className="card-title">
              <div className="card-icon">
                <Target size={20} />
              </div>
              Learning Goals
            </h3>
          </div>
          <div className="card-content">
            <div className="goals-list">
              <div className="goal-item">
                <div className="goal-info">
                  <span className="goal-title">Master React.js</span>
                  <span className="goal-progress">75% complete</span>
                </div>
                <div className="goal-bar">
                  <div className="goal-fill" style={{ width: '75%' }} />
                </div>
              </div>
              <div className="goal-item">
                <div className="goal-info">
                  <span className="goal-title">Learn Python</span>
                  <span className="goal-progress">45% complete</span>
                </div>
                <div className="goal-bar">
                  <div className="goal-fill" style={{ width: '45%' }} />
                </div>
              </div>
              <div className="goal-item">
                <div className="goal-info">
                  <span className="goal-title">Complete 10 Sessions</span>
                  <span className="goal-progress">6/10 sessions</span>
                </div>
                <div className="goal-bar">
                  <div className="goal-fill" style={{ width: '60%' }} />
                </div>
              </div>
            </div>
            <button 
              className="btn btn-outline btn-sm"
              onClick={() => window.location.href = '/goals/new'}
            >
              <Target size={16} />
              Set New Goal
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LearnerDashboard;
