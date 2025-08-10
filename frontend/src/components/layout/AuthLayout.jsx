import { Outlet } from 'react-router-dom';
import { useTheme } from '../../contexts/ThemeContext';
import './AuthLayout.css';

const AuthLayout = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="auth-layout">
      <div className="auth-container">
        <div className="auth-header">
          <h1 className="auth-logo">
            <span className="text-gradient">SkillSphere</span>
          </h1>
          <button 
            onClick={toggleTheme}
            className="theme-toggle"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </div>
        
        <div className="auth-content">
          <Outlet />
        </div>
        
        <div className="auth-footer">
          <p>&copy; 2024 SkillSphere. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
