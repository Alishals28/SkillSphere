import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Button from '../components/ui/Button';

const HomePage = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="home-page">
      <div className="hero-section" style={{ 
        textAlign: 'center', 
        padding: '4rem 2rem',
        background: 'linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%)',
        color: 'white',
        borderRadius: 'var(--radius-lg)',
        margin: 'var(--space-xl)'
      }}>
        <h1 style={{ fontSize: '3rem', marginBottom: '1rem' }}>
          Welcome to SkillSphere
        </h1>
        <p style={{ fontSize: '1.25rem', marginBottom: '2rem', opacity: 0.9 }}>
          Connect with expert mentors and accelerate your learning journey
        </p>
        
        {isAuthenticated ? (
          <Link to="/dashboard">
            <Button variant="secondary" size="lg">
              Go to Dashboard
            </Button>
          </Link>
        ) : (
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <Link to="/auth/register">
              <Button variant="secondary" size="lg">
                Get Started
              </Button>
            </Link>
            <Link to="/auth/login">
              <Button variant="outline" size="lg" style={{ color: 'white', borderColor: 'white' }}>
                Login
              </Button>
            </Link>
          </div>
        )}
      </div>
      
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <h2>Foundation Review Complete! ✅</h2>
        <p>The theme system, routing, and layout components are working perfectly.</p>
      </div>
    </div>
  );
};

export default HomePage;
