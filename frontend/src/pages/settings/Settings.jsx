import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Settings, 
  Bell, 
  Shield, 
  Palette, 
  Globe, 
  Clock, 
  Save, 
  AlertCircle,
  CheckCircle,
  Moon,
  Sun,
  Monitor,
  Mail,
  Smartphone,
  Volume2,
  VolumeX,
  Eye,
  EyeOff,
  Lock,
  Key,
  Database,
  Download,
  Trash2
} from 'lucide-react';
import './Settings.css';

const SettingsPage = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('general');
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  
  // Settings state
  const [settings, setSettings] = useState({
    // General Settings
    language: 'en',
    timezone: 'UTC',
    dateFormat: 'MM/DD/YYYY',
    theme: 'system',
    
    // Notification Settings
    emailNotifications: {
      newMessages: true,
      sessionReminders: true,
      weeklyDigest: true,
      marketingEmails: false,
    },
    pushNotifications: {
      enabled: true,
      sessionReminders: true,
      newMatches: true,
      messages: true,
    },
    notificationSound: true,
    
    // Privacy Settings
    profileVisibility: 'public',
    showOnlineStatus: true,
    allowMessageFromStrangers: false,
    showEmail: false,
    showPhone: false,
    
    // Security Settings
    twoFactorEnabled: false,
    sessionTimeout: 30,
    loginAlerts: true,
  });

  // Load settings on component mount
  useEffect(() => {
    // In a real app, fetch settings from API
    // For now, use default settings
  }, []);

  const handleSettingChange = (category, setting, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [setting]: value
      }
    }));
  };

  const handleGeneralChange = (setting, value) => {
    setSettings(prev => ({
      ...prev,
      [setting]: value
    }));
  };

  const saveSettings = async () => {
    try {
      setSaving(true);
      setError('');
      
      // In a real app, save to API
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      
      setSuccess('Settings saved successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to save settings. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const tabs = [
    { id: 'general', label: 'General', icon: Settings },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'privacy', label: 'Privacy', icon: Shield },
    { id: 'security', label: 'Security', icon: Lock },
    { id: 'data', label: 'Data & Export', icon: Database },
  ];

  return (
    <div className="settings-page">
      <div className="settings-container">
        {/* Header */}
        <div className="settings-header">
          <h1>Settings & Preferences</h1>
          <p>Customize your SkillSphere experience</p>
        </div>

        {/* Success/Error Messages */}
        {success && (
          <div className="alert alert-success">
            <CheckCircle size={20} />
            {success}
          </div>
        )}
        {error && (
          <div className="alert alert-error">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        <div className="settings-content">
          {/* Sidebar Navigation */}
          <div className="settings-sidebar">
            <nav className="settings-nav">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    className={`nav-item ${activeTab === tab.id ? 'active' : ''}`}
                    onClick={() => setActiveTab(tab.id)}
                  >
                    <Icon size={20} />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Main Content */}
          <div className="settings-main">
            {/* General Settings */}
            {activeTab === 'general' && (
              <div className="settings-section">
                <div className="section-header">
                  <h2>General Settings</h2>
                  <p>Configure your basic preferences</p>
                </div>

                <div className="settings-grid">
                  <div className="setting-group">
                    <label className="setting-label">
                      <Globe size={20} />
                      Language
                    </label>
                    <select
                      value={settings.language}
                      onChange={(e) => handleGeneralChange('language', e.target.value)}
                      className="setting-input"
                    >
                      <option value="en">English</option>
                      <option value="es">Spanish</option>
                      <option value="fr">French</option>
                      <option value="de">German</option>
                      <option value="zh">Chinese</option>
                    </select>
                  </div>

                  <div className="setting-group">
                    <label className="setting-label">
                      <Clock size={20} />
                      Timezone
                    </label>
                    <select
                      value={settings.timezone}
                      onChange={(e) => handleGeneralChange('timezone', e.target.value)}
                      className="setting-input"
                    >
                      <option value="UTC">UTC</option>
                      <option value="America/New_York">Eastern Time</option>
                      <option value="America/Chicago">Central Time</option>
                      <option value="America/Denver">Mountain Time</option>
                      <option value="America/Los_Angeles">Pacific Time</option>
                      <option value="Europe/London">London Time</option>
                      <option value="Europe/Paris">Paris Time</option>
                      <option value="Asia/Tokyo">Tokyo Time</option>
                    </select>
                  </div>

                  <div className="setting-group">
                    <label className="setting-label">
                      <Palette size={20} />
                      Theme
                    </label>
                    <div className="theme-options">
                      <label className="theme-option">
                        <input
                          type="radio"
                          name="theme"
                          value="light"
                          checked={settings.theme === 'light'}
                          onChange={(e) => handleGeneralChange('theme', e.target.value)}
                        />
                        <div className="theme-preview light">
                          <Sun size={16} />
                          Light
                        </div>
                      </label>
                      <label className="theme-option">
                        <input
                          type="radio"
                          name="theme"
                          value="dark"
                          checked={settings.theme === 'dark'}
                          onChange={(e) => handleGeneralChange('theme', e.target.value)}
                        />
                        <div className="theme-preview dark">
                          <Moon size={16} />
                          Dark
                        </div>
                      </label>
                      <label className="theme-option">
                        <input
                          type="radio"
                          name="theme"
                          value="system"
                          checked={settings.theme === 'system'}
                          onChange={(e) => handleGeneralChange('theme', e.target.value)}
                        />
                        <div className="theme-preview system">
                          <Monitor size={16} />
                          System
                        </div>
                      </label>
                    </div>
                  </div>

                  <div className="setting-group">
                    <label className="setting-label">
                      Date Format
                    </label>
                    <select
                      value={settings.dateFormat}
                      onChange={(e) => handleGeneralChange('dateFormat', e.target.value)}
                      className="setting-input"
                    >
                      <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                      <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                      <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {/* Notification Settings */}
            {activeTab === 'notifications' && (
              <div className="settings-section">
                <div className="section-header">
                  <h2>Notification Settings</h2>
                  <p>Manage how and when you receive notifications</p>
                </div>

                <div className="settings-grid">
                  {/* Email Notifications */}
                  <div className="setting-category">
                    <h3>
                      <Mail size={20} />
                      Email Notifications
                    </h3>
                    <div className="setting-toggles">
                      <div className="setting-toggle">
                        <label>
                          <input
                            type="checkbox"
                            checked={settings.emailNotifications.newMessages}
                            onChange={(e) => handleSettingChange('emailNotifications', 'newMessages', e.target.checked)}
                          />
                          <span className="toggle-slider"></span>
                        </label>
                        <div className="toggle-info">
                          <strong>New Messages</strong>
                          <span>Get notified when you receive new messages</span>
                        </div>
                      </div>

                      <div className="setting-toggle">
                        <label>
                          <input
                            type="checkbox"
                            checked={settings.emailNotifications.sessionReminders}
                            onChange={(e) => handleSettingChange('emailNotifications', 'sessionReminders', e.target.checked)}
                          />
                          <span className="toggle-slider"></span>
                        </label>
                        <div className="toggle-info">
                          <strong>Session Reminders</strong>
                          <span>Reminder emails for upcoming sessions</span>
                        </div>
                      </div>

                      <div className="setting-toggle">
                        <label>
                          <input
                            type="checkbox"
                            checked={settings.emailNotifications.weeklyDigest}
                            onChange={(e) => handleSettingChange('emailNotifications', 'weeklyDigest', e.target.checked)}
                          />
                          <span className="toggle-slider"></span>
                        </label>
                        <div className="toggle-info">
                          <strong>Weekly Digest</strong>
                          <span>Weekly summary of your activity</span>
                        </div>
                      </div>

                      <div className="setting-toggle">
                        <label>
                          <input
                            type="checkbox"
                            checked={settings.emailNotifications.marketingEmails}
                            onChange={(e) => handleSettingChange('emailNotifications', 'marketingEmails', e.target.checked)}
                          />
                          <span className="toggle-slider"></span>
                        </label>
                        <div className="toggle-info">
                          <strong>Marketing Emails</strong>
                          <span>Promotional content and feature updates</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Push Notifications */}
                  <div className="setting-category">
                    <h3>
                      <Smartphone size={20} />
                      Push Notifications
                    </h3>
                    <div className="setting-toggles">
                      <div className="setting-toggle">
                        <label>
                          <input
                            type="checkbox"
                            checked={settings.pushNotifications.enabled}
                            onChange={(e) => handleSettingChange('pushNotifications', 'enabled', e.target.checked)}
                          />
                          <span className="toggle-slider"></span>
                        </label>
                        <div className="toggle-info">
                          <strong>Enable Push Notifications</strong>
                          <span>Allow browser notifications</span>
                        </div>
                      </div>

                      <div className="setting-toggle">
                        <label>
                          <input
                            type="checkbox"
                            checked={settings.notificationSound}
                            onChange={(e) => handleGeneralChange('notificationSound', e.target.checked)}
                          />
                          <span className="toggle-slider"></span>
                        </label>
                        <div className="toggle-info">
                          <strong>
                            {settings.notificationSound ? <Volume2 size={16} /> : <VolumeX size={16} />}
                            Notification Sound
                          </strong>
                          <span>Play sound for notifications</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Privacy Settings */}
            {activeTab === 'privacy' && (
              <div className="settings-section">
                <div className="section-header">
                  <h2>Privacy Settings</h2>
                  <p>Control who can see your information</p>
                </div>

                <div className="settings-grid">
                  <div className="setting-group">
                    <label className="setting-label">
                      Profile Visibility
                    </label>
                    <select
                      value={settings.profileVisibility}
                      onChange={(e) => handleGeneralChange('profileVisibility', e.target.value)}
                      className="setting-input"
                    >
                      <option value="public">Public - Anyone can find you</option>
                      <option value="users">SkillSphere Users Only</option>
                      <option value="connections">Connections Only</option>
                      <option value="private">Private - Hidden from search</option>
                    </select>
                  </div>

                  <div className="setting-toggles">
                    <div className="setting-toggle">
                      <label>
                        <input
                          type="checkbox"
                          checked={settings.showOnlineStatus}
                          onChange={(e) => handleGeneralChange('showOnlineStatus', e.target.checked)}
                        />
                        <span className="toggle-slider"></span>
                      </label>
                      <div className="toggle-info">
                        <strong>Show Online Status</strong>
                        <span>Let others see when you're online</span>
                      </div>
                    </div>

                    <div className="setting-toggle">
                      <label>
                        <input
                          type="checkbox"
                          checked={settings.showEmail}
                          onChange={(e) => handleGeneralChange('showEmail', e.target.checked)}
                        />
                        <span className="toggle-slider"></span>
                      </label>
                      <div className="toggle-info">
                        <strong>
                          {settings.showEmail ? <Eye size={16} /> : <EyeOff size={16} />}
                          Show Email Address
                        </strong>
                        <span>Display email on your public profile</span>
                      </div>
                    </div>

                    <div className="setting-toggle">
                      <label>
                        <input
                          type="checkbox"
                          checked={settings.allowMessageFromStrangers}
                          onChange={(e) => handleGeneralChange('allowMessageFromStrangers', e.target.checked)}
                        />
                        <span className="toggle-slider"></span>
                      </label>
                      <div className="toggle-info">
                        <strong>Allow Messages from Anyone</strong>
                        <span>Receive messages from users you haven't connected with</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Security Settings */}
            {activeTab === 'security' && (
              <div className="settings-section">
                <div className="section-header">
                  <h2>Security Settings</h2>
                  <p>Protect your account and data</p>
                </div>

                <div className="settings-grid">
                  <div className="security-actions">
                    <div className="security-item">
                      <div className="security-info">
                        <Key size={24} />
                        <div>
                          <h4>Change Password</h4>
                          <p>Update your account password</p>
                        </div>
                      </div>
                      <button className="btn btn-outline">Change</button>
                    </div>

                    <div className="security-item">
                      <div className="security-info">
                        <Shield size={24} />
                        <div>
                          <h4>Two-Factor Authentication</h4>
                          <p>Add an extra layer of security</p>
                          <span className={`status ${settings.twoFactorEnabled ? 'enabled' : 'disabled'}`}>
                            {settings.twoFactorEnabled ? 'Enabled' : 'Disabled'}
                          </span>
                        </div>
                      </div>
                      <button className="btn btn-outline">
                        {settings.twoFactorEnabled ? 'Disable' : 'Enable'}
                      </button>
                    </div>
                  </div>

                  <div className="setting-group">
                    <label className="setting-label">
                      Session Timeout (minutes)
                    </label>
                    <select
                      value={settings.sessionTimeout}
                      onChange={(e) => handleGeneralChange('sessionTimeout', parseInt(e.target.value))}
                      className="setting-input"
                    >
                      <option value={15}>15 minutes</option>
                      <option value={30}>30 minutes</option>
                      <option value={60}>1 hour</option>
                      <option value={120}>2 hours</option>
                      <option value={0}>Never</option>
                    </select>
                  </div>

                  <div className="setting-toggle">
                    <label>
                      <input
                        type="checkbox"
                        checked={settings.loginAlerts}
                        onChange={(e) => handleGeneralChange('loginAlerts', e.target.checked)}
                      />
                      <span className="toggle-slider"></span>
                    </label>
                    <div className="toggle-info">
                      <strong>Login Alerts</strong>
                      <span>Get notified of new login attempts</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Data & Export */}
            {activeTab === 'data' && (
              <div className="settings-section">
                <div className="section-header">
                  <h2>Data & Export</h2>
                  <p>Manage your data and account</p>
                </div>

                <div className="settings-grid">
                  <div className="data-actions">
                    <div className="data-item">
                      <div className="data-info">
                        <Download size={24} />
                        <div>
                          <h4>Export Data</h4>
                          <p>Download a copy of your data</p>
                        </div>
                      </div>
                      <button className="btn btn-outline">Export</button>
                    </div>

                    <div className="data-item danger">
                      <div className="data-info">
                        <Trash2 size={24} />
                        <div>
                          <h4>Delete Account</h4>
                          <p>Permanently delete your account and all data</p>
                        </div>
                      </div>
                      <button className="btn btn-danger">Delete</button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Save Button */}
            <div className="settings-footer">
              <button
                className="btn btn-primary save-btn"
                onClick={saveSettings}
                disabled={saving}
              >
                {saving ? (
                  <>
                    <div className="spinner" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save size={20} />
                    Save Settings
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
