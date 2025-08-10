import { useAuth } from '../../contexts/AuthContext';
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
  ChevronRight
} from 'lucide-react';
import './LearnerDashboard.css';

const LearnerDashboard = () => {
  const { user } = useAuth();

  // Sample data - in real app, this would come from API
  const stats = [
    { icon: '📚', label: 'Sessions Completed', value: '0', color: 'sessions' },
    { icon: '🏆', label: 'Badges Earned', value: '0', color: 'badges' },
    { icon: '⏱️', label: 'Hours Learned', value: '0', color: 'hours' },
    { icon: '🔥', label: 'Day Streak', value: '0', color: 'streak' },
  ];

  const upcomingSessions = [
    // Empty for now - will be populated from API
  ];

  const recommendedMentors = [
    {
      id: 1,
      name: 'Alex Rodriguez',
      specialty: 'Full Stack Development',
      rating: 4.9,
      sessions: 150,
      avatar: 'AR',
    },
    {
      id: 2,
      name: 'Emily Davis',
      specialty: 'UI/UX Design',
      rating: 4.8,
      sessions: 120,
      avatar: 'ED',
    },
    {
      id: 3,
      name: 'David Kim',
      specialty: 'Data Science',
      rating: 4.9,
      sessions: 200,
      avatar: 'DK',
    },
  ];

  const recentActivity = [
    { type: 'session', icon: '📚', text: 'Completed session with Sarah Chen', time: '2 hours ago' },
    { type: 'badge', icon: '🏆', text: 'Earned "React Master" badge', time: '1 day ago' },
    { type: 'review', icon: '⭐', text: 'Left review for Mike Johnson', time: '2 days ago' },
    { type: 'session', icon: '📚', text: 'Booked session with Alex Rodriguez', time: '3 days ago' },
  ];

  return (
    <div className="learner-dashboard">
      <div className="dashboard-container">
        {/* Header */}
        <div className="dashboard-header">
          <h1>Welcome back, {user?.first_name || 'Learner'}! 👋</h1>
          <p>Ready to continue your learning journey and unlock new skills?</p>
        </div>

        {/* Quick Stats */}
        <div className="quick-stats">
          {stats.map((stat, index) => (
            <div key={index} className="stat-card">
              <div className={`stat-icon ${stat.color}`}>
                {stat.icon}
              </div>
              <div className="stat-number">{stat.value}</div>
              <div className="stat-label">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Main Dashboard Grid */}
        <div className="dashboard-grid">
          {/* Main Content */}
          <div className="main-content">
            {/* Upcoming Sessions */}
            <div className="dashboard-card upcoming-sessions">
              <div className="card-header">
                <h3 className="card-title">
                  <div className="card-icon">
                    <Calendar size={20} />
                  </div>
                  Upcoming Sessions
                </h3>
                <ChevronRight size={20} color="var(--text-secondary)" />
              </div>
              <div className="card-content">
                {upcomingSessions.length > 0 ? (
                  <div className="sessions-list">
                    {upcomingSessions.map((session) => (
                      <div key={session.id} className="session-item">
                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
                          <div className="mentor-avatar">
                            {session.avatar}
                          </div>
                          <div style={{ flex: 1 }}>
                            <h4 style={{ margin: 0, marginBottom: 'var(--space-xs)', color: 'var(--text-primary)' }}>
                              {session.topic}
                            </h4>
                            <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                              with {session.mentorName} • {session.time}
                            </p>
                          </div>
                          <button className="btn btn-primary">
                            <Play size={16} />
                            Join
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">
                    <div className="empty-state-icon">📅</div>
                    <p>No upcoming sessions scheduled</p>
                  </div>
                )}
                <div className="action-buttons">
                  <button className="btn btn-primary">
                    <Calendar size={16} />
                    Book a Session
                  </button>
                  <button className="btn btn-outline">
                    View All Sessions
                  </button>
                </div>
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
                <ChevronRight size={20} color="var(--text-secondary)" />
              </div>
              <div className="card-content">
                <p style={{ marginBottom: 'var(--space-lg)', color: 'var(--text-secondary)' }}>
                  Discover mentors that match your learning goals and interests
                </p>
                <div className="mentors-list">
                  {recommendedMentors.map((mentor) => (
                    <div key={mentor.id} className="mentor-card">
                      <div className="mentor-avatar">
                        {mentor.avatar}
                      </div>
                      <div className="mentor-info">
                        <h4>{mentor.name}</h4>
                        <p>{mentor.specialty}</p>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', marginTop: 'var(--space-xs)' }}>
                          <Star size={14} fill="var(--accent-secondary)" color="var(--accent-secondary)" />
                          <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                            {mentor.rating} • {mentor.sessions} sessions
                          </span>
                        </div>
                      </div>
                      <button className="btn btn-secondary">
                        View Profile
                      </button>
                    </div>
                  ))}
                </div>
                <div className="action-buttons">
                  <button className="btn btn-secondary">
                    <Users size={16} />
                    Browse All Mentors
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="sidebar-content">
            {/* Progress Section */}
            <div className="dashboard-card progress-section">
              <div className="card-header">
                <h3 className="card-title">
                  <div className="card-icon">
                    <TrendingUp size={20} />
                  </div>
                  Your Progress
                </h3>
              </div>
              <div className="card-content">
                <p style={{ marginBottom: 'var(--space-lg)', color: 'var(--text-secondary)' }}>
                  Track your learning achievements and milestones
                </p>
                <div className="progress-rings">
                  <div className="progress-ring">
                    <div className="ring">
                      <span className="ring-text">75%</span>
                    </div>
                    <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                      Monthly Goal
                    </span>
                  </div>
                  <div className="progress-ring">
                    <div className="ring">
                      <span className="ring-text">5</span>
                    </div>
                    <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                      Badges
                    </span>
                  </div>
                </div>
                <div className="action-buttons">
                  <button className="btn btn-outline">
                    <Trophy size={16} />
                    View Badges
                  </button>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="dashboard-card">
              <div className="card-header">
                <h3 className="card-title">
                  <div className="card-icon">
                    <Clock size={20} />
                  </div>
                  Recent Activity
                </h3>
              </div>
              <div className="card-content">
                <div className="recent-activity">
                  {recentActivity.map((activity, index) => (
                    <div key={index} className="activity-item">
                      <div className={`activity-icon ${activity.type}`}>
                        {activity.icon}
                      </div>
                      <div style={{ flex: 1 }}>
                        <p style={{ margin: 0, marginBottom: 'var(--space-xs)', fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                          {activity.text}
                        </p>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                          {activity.time}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LearnerDashboard;


