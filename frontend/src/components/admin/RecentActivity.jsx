import React, { useState, useEffect } from 'react';
import { 
  User, 
  BookOpen, 
  MessageSquare, 
  UserPlus, 
  Calendar,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';
import './RecentActivity.css';

const RecentActivity = () => {
  const [activities, setActivities] = useState([]);

  useEffect(() => {
    // Mock recent activities
    const mockActivities = [
      {
        id: 1,
        type: 'user_registration',
        user: 'Sarah Johnson',
        action: 'New student registered',
        timestamp: '2 minutes ago',
        icon: UserPlus,
        color: 'green'
      },
      {
        id: 2,
        type: 'session_completed',
        user: 'Dr. Michael Chen',
        action: 'Completed session with Alex Thompson',
        timestamp: '5 minutes ago',
        icon: CheckCircle,
        color: 'blue'
      },
      {
        id: 3,
        type: 'mentor_application',
        user: 'Emma Rodriguez',
        action: 'Applied to become a mentor',
        timestamp: '10 minutes ago',
        icon: User,
        color: 'purple'
      },
      {
        id: 4,
        type: 'session_booked',
        user: 'John Davis',
        action: 'Booked React session with Dr. Sarah Martinez',
        timestamp: '15 minutes ago',
        icon: Calendar,
        color: 'teal'
      },
      {
        id: 5,
        type: 'chat_message',
        user: 'Study Group #5',
        action: 'New message in group chat',
        timestamp: '20 minutes ago',
        icon: MessageSquare,
        color: 'orange'
      },
      {
        id: 6,
        type: 'system_alert',
        user: 'System',
        action: 'High CPU usage detected',
        timestamp: '25 minutes ago',
        icon: AlertCircle,
        color: 'red'
      },
      {
        id: 7,
        type: 'session_started',
        user: 'Prof. Lisa Wang',
        action: 'Started Python session',
        timestamp: '30 minutes ago',
        icon: BookOpen,
        color: 'green'
      },
      {
        id: 8,
        type: 'user_login',
        user: 'Robert Kim',
        action: 'Logged in from new device',
        timestamp: '35 minutes ago',
        icon: User,
        color: 'blue'
      }
    ];

    setActivities(mockActivities);
  }, []);

  const getActivityIcon = (activity) => {
    const IconComponent = activity.icon;
    return <IconComponent size={20} />;
  };

  return (
    <div className="recent-activity">
      <div className="activity-header">
        <h2>Recent Activity</h2>
        <div className="activity-controls">
          <button className="refresh-activity">
            <Clock size={16} />
            Refresh
          </button>
        </div>
      </div>

      <div className="activity-list">
        {activities.map((activity) => (
          <div key={activity.id} className={`activity-item ${activity.color}`}>
            <div className="activity-icon">
              {getActivityIcon(activity)}
            </div>
            
            <div className="activity-content">
              <div className="activity-text">
                <span className="activity-user">{activity.user}</span>
                <span className="activity-action">{activity.action}</span>
              </div>
              <div className="activity-timestamp">
                {activity.timestamp}
              </div>
            </div>
            
            <div className="activity-status">
              {activity.type === 'system_alert' && (
                <div className="status-indicator alert"></div>
              )}
              {activity.type === 'mentor_application' && (
                <div className="status-indicator pending"></div>
              )}
              {activity.type === 'session_completed' && (
                <div className="status-indicator success"></div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="activity-footer">
        <button className="view-all-btn">
          View All Activity
        </button>
      </div>
    </div>
  );
};

export default RecentActivity;
