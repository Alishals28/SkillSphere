import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Bell, 
  MessageSquare, 
  Calendar, 
  Star, 
  Award, 
  TrendingUp,
  X,
  Check,
  CheckCheck,
  Filter,
  Search,
  MoreVertical
} from 'lucide-react';
import './NotificationsCenter.css';

const NotificationsCenter = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  // Mock notifications data - replace with API call
  useEffect(() => {
    const mockNotifications = [
      {
        id: 1,
        type: 'session',
        title: 'New session booked',
        message: user?.role === 'mentor' 
          ? 'Sarah Johnson booked a React.js session for tomorrow at 2:00 PM'
          : 'Your React.js session with John Smith is confirmed for tomorrow at 2:00 PM',
        timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
        isRead: false,
        priority: 'high',
        actionUrl: '/bookings/1'
      },
      {
        id: 2,
        type: 'review',
        title: 'New review received',
        message: 'Alex Chen left a 5-star review for your Python session',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
        isRead: false,
        priority: 'medium',
        actionUrl: '/reviews/2'
      },
      {
        id: 3,
        type: 'message',
        title: 'New message',
        message: 'David Miller sent you a message about the upcoming JavaScript session',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4), // 4 hours ago
        isRead: true,
        priority: 'medium',
        actionUrl: '/chat/3'
      },
      {
        id: 4,
        type: 'achievement',
        title: 'Achievement unlocked!',
        message: 'Congratulations! You\'ve completed 50 mentoring sessions',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
        isRead: true,
        priority: 'low',
        actionUrl: '/achievements'
      },
      {
        id: 5,
        type: 'system',
        title: 'Profile update reminder',
        message: 'Complete your profile to increase booking rates by 40%',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2), // 2 days ago
        isRead: false,
        priority: 'medium',
        actionUrl: '/profile'
      }
    ];

    setTimeout(() => {
      setNotifications(mockNotifications);
      setLoading(false);
    }, 500);
  }, [user?.role]);

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'session':
        return <Calendar className="notification-icon session" />;
      case 'review':
        return <Star className="notification-icon review" />;
      case 'message':
        return <MessageSquare className="notification-icon message" />;
      case 'achievement':
        return <Award className="notification-icon achievement" />;
      case 'system':
        return <Bell className="notification-icon system" />;
      default:
        return <Bell className="notification-icon default" />;
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 60) {
      return `${minutes}m ago`;
    } else if (hours < 24) {
      return `${hours}h ago`;
    } else {
      return `${days}d ago`;
    }
  };

  const markAsRead = (id) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id 
          ? { ...notification, isRead: true }
          : notification
      )
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notification => ({ ...notification, isRead: true }))
    );
  };

  const deleteNotification = (id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  };

  const filteredNotifications = notifications.filter(notification => {
    const matchesFilter = filter === 'all' || 
      (filter === 'unread' && !notification.isRead) ||
      (filter === 'read' && notification.isRead) ||
      notification.type === filter;
    
    const matchesSearch = notification.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      notification.message.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesFilter && matchesSearch;
  });

  const unreadCount = notifications.filter(n => !n.isRead).length;

  if (loading) {
    return (
      <div className="notifications-center">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading notifications...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="notifications-center">
      <div className="notifications-header">
        <div className="header-title">
          <h1>Notifications</h1>
          {unreadCount > 0 && (
            <span className="unread-badge">{unreadCount} unread</span>
          )}
        </div>
        
        <div className="header-actions">
          <button 
            className="mark-all-read-btn"
            onClick={markAllAsRead}
            disabled={unreadCount === 0}
          >
            <CheckCheck size={18} />
            Mark all read
          </button>
        </div>
      </div>

      <div className="notifications-controls">
        <div className="search-box">
          <Search className="search-icon" />
          <input
            type="text"
            placeholder="Search notifications..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-tabs">
          <button 
            className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button 
            className={`filter-tab ${filter === 'unread' ? 'active' : ''}`}
            onClick={() => setFilter('unread')}
          >
            Unread ({unreadCount})
          </button>
          <button 
            className={`filter-tab ${filter === 'session' ? 'active' : ''}`}
            onClick={() => setFilter('session')}
          >
            Sessions
          </button>
          <button 
            className={`filter-tab ${filter === 'message' ? 'active' : ''}`}
            onClick={() => setFilter('message')}
          >
            Messages
          </button>
          <button 
            className={`filter-tab ${filter === 'review' ? 'active' : ''}`}
            onClick={() => setFilter('review')}
          >
            Reviews
          </button>
        </div>
      </div>

      <div className="notifications-list">
        {filteredNotifications.length === 0 ? (
          <div className="empty-state">
            <Bell className="empty-icon" />
            <h3>No notifications found</h3>
            <p>
              {filter === 'all' 
                ? "You're all caught up! No new notifications."
                : `No ${filter === 'unread' ? 'unread' : filter} notifications found.`
              }
            </p>
          </div>
        ) : (
          filteredNotifications.map(notification => (
            <div 
              key={notification.id}
              className={`notification-item ${!notification.isRead ? 'unread' : ''} ${notification.priority}`}
              onClick={() => {
                if (!notification.isRead) {
                  markAsRead(notification.id);
                }
                if (notification.actionUrl) {
                  window.location.href = notification.actionUrl;
                }
              }}
            >
              <div className="notification-content">
                <div className="notification-left">
                  {getNotificationIcon(notification.type)}
                  <div className="notification-text">
                    <h4 className="notification-title">{notification.title}</h4>
                    <p className="notification-message">{notification.message}</p>
                    <span className="notification-time">
                      {formatTimeAgo(notification.timestamp)}
                    </span>
                  </div>
                </div>
                
                <div className="notification-right">
                  {!notification.isRead && (
                    <div className="unread-indicator" />
                  )}
                  <div className="notification-actions">
                    <button
                      className="action-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        markAsRead(notification.id);
                      }}
                      title={notification.isRead ? "Already read" : "Mark as read"}
                      disabled={notification.isRead}
                    >
                      <Check size={16} />
                    </button>
                    <button
                      className="action-btn delete"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteNotification(notification.id);
                      }}
                      title="Delete notification"
                    >
                      <X size={16} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {filteredNotifications.length > 0 && (
        <div className="notifications-footer">
          <p>Showing {filteredNotifications.length} of {notifications.length} notifications</p>
        </div>
      )}
    </div>
  );
};

export default NotificationsCenter;
