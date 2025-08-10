import React, { useState, useEffect } from 'react';
import { 
  Users, 
  BookOpen, 
  MessageSquare, 
  DollarSign, 
  TrendingUp, 
  AlertTriangle,
  Settings,
  Brain,
  Shield,
  Database,
  Activity,
  Clock,
  UserCheck,
  Calendar,
  Star,
  Mail,
  Globe
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import AdminSidebar from '../../components/admin/AdminSidebar';
import StatsCard from '../../components/admin/StatsCard';
import RecentActivity from '../../components/admin/RecentActivity';
import UserManagement from '../../components/admin/UserManagement';
import SessionAnalytics from '../../components/admin/SessionAnalytics';
import AIManagement from '../../components/admin/AIManagement';
import SystemSettings from '../../components/admin/SystemSettings';
import './AdminPanel.css';

const AdminPanel = () => {
  const { user } = useAuth();
  const [activeSection, setActiveSection] = useState('dashboard');
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);

  // Mock admin stats
  useEffect(() => {
    // Simulate loading admin statistics
    setTimeout(() => {
      setStats({
        totalUsers: 1250,
        totalMentors: 89,
        totalStudents: 1161,
        activeSessions: 45,
        totalSessions: 2340,
        monthlyRevenue: 34500,
        aiRequestsToday: 1847,
        systemHealth: 98.5,
        activeConnections: 234,
        storageUsed: 78.2,
        responseTime: 245,
        uptime: 99.9
      });
      setLoading(false);
    }, 1000);
  }, []);

  const menuItems = [
    { 
      id: 'dashboard', 
      label: 'Dashboard', 
      icon: Activity,
      description: 'Overview and statistics'
    },
    { 
      id: 'users', 
      label: 'User Management', 
      icon: Users,
      description: 'Manage users, mentors, and students'
    },
    { 
      id: 'sessions', 
      label: 'Session Analytics', 
      icon: BookOpen,
      description: 'Session data and performance'
    },
    { 
      id: 'ai', 
      label: 'AI Management', 
      icon: Brain,
      description: 'AI services and monitoring'
    },
    { 
      id: 'system', 
      label: 'System Settings', 
      icon: Settings,
      description: 'Platform configuration'
    },
    { 
      id: 'security', 
      label: 'Security', 
      icon: Shield,
      description: 'Security monitoring and logs'
    }
  ];

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return renderDashboard();
      case 'users':
        return <UserManagement />;
      case 'sessions':
        return <SessionAnalytics />;
      case 'ai':
        return <AIManagement />;
      case 'system':
        return <SystemSettings />;
      case 'security':
        return renderSecurity();
      default:
        return renderDashboard();
    }
  };

  const renderDashboard = () => (
    <div className="admin-dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <h1>Admin Dashboard</h1>
          <p>Welcome back, {user?.name}. Here's what's happening on SkillSphere today.</p>
        </div>
        <div className="header-actions">
          <button className="refresh-btn">
            <Activity size={20} />
            Refresh Data
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="stats-grid">
        <StatsCard
          title="Total Users"
          value={stats.totalUsers?.toLocaleString()}
          change="+12.5%"
          changeType="positive"
          icon={Users}
          color="blue"
        />
        <StatsCard
          title="Active Sessions"
          value={stats.activeSessions}
          change="+8.2%"
          changeType="positive"
          icon={BookOpen}
          color="green"
        />
        <StatsCard
          title="Monthly Revenue"
          value={`$${stats.monthlyRevenue?.toLocaleString()}`}
          change="+23.1%"
          changeType="positive"
          icon={DollarSign}
          color="teal"
        />
        <StatsCard
          title="AI Requests"
          value={stats.aiRequestsToday?.toLocaleString()}
          change="+15.7%"
          changeType="positive"
          icon={Brain}
          color="purple"
        />
      </div>

      {/* System Health */}
      <div className="system-health-section">
        <h2>System Health</h2>
        <div className="health-grid">
          <div className="health-card">
            <div className="health-header">
              <Activity className="health-icon" />
              <div>
                <h3>System Health</h3>
                <p className="health-value">{stats.systemHealth}%</p>
              </div>
            </div>
            <div className="health-bar">
              <div 
                className="health-progress" 
                style={{ width: `${stats.systemHealth}%` }}
              ></div>
            </div>
          </div>

          <div className="health-card">
            <div className="health-header">
              <Globe className="health-icon" />
              <div>
                <h3>Active Connections</h3>
                <p className="health-value">{stats.activeConnections}</p>
              </div>
            </div>
            <div className="connection-indicator">
              <div className="pulse-dot"></div>
              Real-time connections
            </div>
          </div>

          <div className="health-card">
            <div className="health-header">
              <Database className="health-icon" />
              <div>
                <h3>Storage Used</h3>
                <p className="health-value">{stats.storageUsed}%</p>
              </div>
            </div>
            <div className="health-bar">
              <div 
                className="health-progress storage" 
                style={{ width: `${stats.storageUsed}%` }}
              ></div>
            </div>
          </div>

          <div className="health-card">
            <div className="health-header">
              <Clock className="health-icon" />
              <div>
                <h3>Response Time</h3>
                <p className="health-value">{stats.responseTime}ms</p>
              </div>
            </div>
            <div className="response-status">
              <span className="status-dot good"></span>
              Excellent
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity and Quick Actions */}
      <div className="dashboard-content">
        <div className="content-grid">
          <RecentActivity />
          
          <div className="quick-actions">
            <h2>Quick Actions</h2>
            <div className="actions-grid">
              <button 
                className="action-card"
                onClick={() => setActiveSection('users')}
              >
                <UserCheck size={24} />
                <div>
                  <h3>Approve Mentors</h3>
                  <p>3 pending applications</p>
                </div>
              </button>

              <button 
                className="action-card"
                onClick={() => setActiveSection('sessions')}
              >
                <Calendar size={24} />
                <div>
                  <h3>Review Sessions</h3>
                  <p>Monitor ongoing sessions</p>
                </div>
              </button>

              <button 
                className="action-card"
                onClick={() => setActiveSection('ai')}
              >
                <Brain size={24} />
                <div>
                  <h3>AI Analytics</h3>
                  <p>Check AI performance</p>
                </div>
              </button>

              <button 
                className="action-card"
                onClick={() => setActiveSection('system')}
              >
                <Settings size={24} />
                <div>
                  <h3>System Config</h3>
                  <p>Update platform settings</p>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSecurity = () => (
    <div className="security-section">
      <h1>Security Monitoring</h1>
      <div className="security-overview">
        <div className="security-card">
          <Shield className="security-icon" />
          <h3>Threat Level: LOW</h3>
          <p>No active security threats detected</p>
        </div>
        <div className="security-card">
          <AlertTriangle className="security-icon warning" />
          <h3>2 Failed Login Attempts</h3>
          <p>Multiple failed attempts from IP: 192.168.1.100</p>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="loading-spinner"></div>
        <h3>Loading Admin Panel...</h3>
        <p>Gathering system statistics...</p>
      </div>
    );
  }

  return (
    <div className="admin-panel">
      <AdminSidebar 
        activeSection={activeSection}
        setActiveSection={setActiveSection}
        menuItems={menuItems}
      />
      
      <div className="admin-content">
        {renderContent()}
      </div>
    </div>
  );
};

export default AdminPanel;
