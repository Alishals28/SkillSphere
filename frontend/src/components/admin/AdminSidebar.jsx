import React from 'react';
import { LogOut, User } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import './AdminSidebar.css';

const AdminSidebar = ({ activeSection, setActiveSection, menuItems }) => {
  const { user, logout } = useAuth();

  return (
    <div className="admin-sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="brand-logo">
          <div className="logo-icon">SS</div>
          <span>SkillSphere Admin</span>
        </div>
      </div>

      {/* User Info */}
      <div className="admin-user-info">
        <div className="user-avatar">
          {user?.avatar ? (
            <img src={user.avatar} alt={user.name} />
          ) : (
            <User size={20} />
          )}
        </div>
        <div className="user-details">
          <h4>{user?.name}</h4>
          <p>Administrator</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <ul className="nav-list">
          {menuItems.map((item) => (
            <li key={item.id}>
              <button
                className={`nav-item ${activeSection === item.id ? 'active' : ''}`}
                onClick={() => setActiveSection(item.id)}
              >
                <item.icon size={20} />
                <div className="nav-content">
                  <span className="nav-label">{item.label}</span>
                  <span className="nav-description">{item.description}</span>
                </div>
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* System Status */}
      <div className="system-status">
        <div className="status-indicator">
          <div className="status-dot online"></div>
          <div className="status-info">
            <span>System Online</span>
            <p>All services operational</p>
          </div>
        </div>
      </div>

      {/* Logout */}
      <div className="sidebar-footer">
        <button className="logout-btn" onClick={logout}>
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
};

export default AdminSidebar;
