import { useAuth } from '../contexts/AuthContext';

const DashboardPage = () => {
  const { user } = useAuth();

  return (
    <div className="dashboard-page">
      <div style={{ padding: '2rem' }}>
        <h1>Dashboard</h1>
        <p>Welcome back, {user?.first_name || 'User'}!</p>
        
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '1.5rem',
          marginTop: '2rem'
        }}>
          <div className="dashboard-card" style={{
            padding: '1.5rem',
            backgroundColor: 'var(--surface)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border)',
            boxShadow: 'var(--shadow-sm)'
          }}>
            <h3>Quick Stats</h3>
            <p>Dashboard content coming soon...</p>
          </div>
          
          <div className="dashboard-card" style={{
            padding: '1.5rem',
            backgroundColor: 'var(--surface)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border)',
            boxShadow: 'var(--shadow-sm)'
          }}>
            <h3>Recent Activity</h3>
            <p>Activity feed coming soon...</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
