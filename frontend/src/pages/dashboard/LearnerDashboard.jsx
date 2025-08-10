import { useAuth } from '../../contexts/AuthContext';
import './LearnerDashboard.css';

const LearnerDashboard = () => {
  const { user } = useAuth();

  return (
    <div className="learner-dashboard">
      <div className="dashboard-header">
        <h1>Welcome back, {user?.first_name || 'Learner'}!</h1>
        <p>Ready to continue your learning journey?</p>
      </div>

      <div className="dashboard-grid">
        <div className="card dashboard-card">
          <div className="card-header">
            <h3 className="card-title">Upcoming Sessions</h3>
          </div>
          <div className="card-content">
            <p>You have no upcoming sessions.</p>
            <button className="btn btn-primary">Book a Session</button>
          </div>
        </div>

        <div className="card dashboard-card">
          <div className="card-header">
            <h3 className="card-title">Recommended Mentors</h3>
          </div>
          <div className="card-content">
            <p>Discover mentors that match your interests.</p>
            <button className="btn btn-outline">Browse Mentors</button>
          </div>
        </div>

        <div className="card dashboard-card">
          <div className="card-header">
            <h3 className="card-title">Your Progress</h3>
          </div>
          <div className="card-content">
            <p>Track your learning achievements and badges.</p>
            <div className="progress-stats">
              <div className="stat">
                <span className="stat-number">0</span>
                <span className="stat-label">Sessions Completed</span>
              </div>
              <div className="stat">
                <span className="stat-number">0</span>
                <span className="stat-label">Badges Earned</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LearnerDashboard;
