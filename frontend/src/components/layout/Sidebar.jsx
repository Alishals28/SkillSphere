import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './Sidebar.css';

const Sidebar = () => {
  const { user } = useAuth();
  const location = useLocation();

  // Don't show sidebar on auth pages
  if (location.pathname.startsWith('/auth')) {
    return null;
  }

  const menuItems = {
    learner: [
      { path: '/dashboard', label: 'Dashboard', icon: '📊' },
      { path: '/mentors', label: 'Find Mentors', icon: '👥' },
      { path: '/sessions', label: 'My Sessions', icon: '📅' },
      { path: '/profile', label: 'Profile', icon: '👤' },
    ],
    mentor: [
      { path: '/dashboard', label: 'Dashboard', icon: '📊' },
      { path: '/sessions', label: 'Sessions', icon: '📅' },
      { path: '/students', label: 'Students', icon: '🎓' },
      { path: '/analytics', label: 'Analytics', icon: '📈' },
      { path: '/profile', label: 'Profile', icon: '👤' },
    ],
    admin: [
      { path: '/dashboard', label: 'Dashboard', icon: '📊' },
      { path: '/admin/mentors', label: 'Manage Mentors', icon: '👥' },
      { path: '/admin/analytics', label: 'Analytics', icon: '📈' },
      { path: '/admin/reports', label: 'Reports', icon: '📋' },
    ],
  };

  const currentMenuItems = menuItems[user?.role] || menuItems.learner;

  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        <ul className="sidebar-menu">
          {currentMenuItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`sidebar-link ${location.pathname === item.path ? 'active' : ''}`}
              >
                <span className="sidebar-icon">{item.icon}</span>
                <span className="sidebar-label">{item.label}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
