import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { userAPI } from '../../services/api';
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Calendar, 
  Edit3, 
  Camera, 
  Save, 
  X, 
  Loader,
  Github,
  Linkedin,
  Globe,
  Star,
  Award,
  BookOpen,
  Users,
  Clock,
  Target,
  AlertCircle
} from 'lucide-react';
import './UserProfile.css';

const UserProfile = () => {
  const { user, updateUser } = useAuth();
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({});

  // Fetch user profile data
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        // For now, use the user data from auth context
        if (user) {
          setProfileData(user);
          setFormData(user);
        }
      } catch (err) {
        console.error('Profile fetch error:', err);
        setError('Failed to load profile data');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [user]);

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle profile picture upload
  const handleProfilePictureChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type and size
    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file');
      return;
    }

    if (file.size > 5 * 1024 * 1024) { // 5MB limit
      setError('Image file size must be less than 5MB');
      return;
    }

    try {
      setSaving(true);
      // For now, just show success message (in real app, would upload to server)
      setSuccess('Profile picture updated successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Upload error:', err);
      setError('Failed to upload profile picture');
    } finally {
      setSaving(false);
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      setError('');
      
      // For now, just update local state (in real app, would call API)
      setProfileData(formData);
      setEditing(false);
      setSuccess('Profile updated successfully!');
      
      // Update auth context with new user data
      if (updateUser) {
        updateUser(formData);
      }
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Update error:', err);
      setError('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  // Cancel editing
  const handleCancel = () => {
    setFormData(profileData);
    setEditing(false);
    setError('');
  };

  if (loading) {
    return (
      <div className="user-profile">
        <div className="profile-container">
          <div className="loading-state">
            <Loader size={40} className="spinner" />
            <p>Loading your profile...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="user-profile">
      <div className="profile-container">
        {/* Header */}
        <div className="profile-header">
          <h1>My Profile</h1>
          <p>Manage your account information and preferences</p>
        </div>

        {/* Success/Error Messages */}
        {success && (
          <div className="alert alert-success">
            {success}
          </div>
        )}
        {error && (
          <div className="alert alert-error">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        <div className="profile-content">
          {/* Profile Card */}
          <div className="profile-card main-profile">
            <div className="profile-card-header">
              <h2>Profile Information</h2>
              {!editing ? (
                <button 
                  className="btn btn-secondary"
                  onClick={() => setEditing(true)}
                >
                  <Edit3 size={16} />
                  Edit Profile
                </button>
              ) : (
                <div className="edit-actions">
                  <button 
                    className="btn btn-outline"
                    onClick={handleCancel}
                    disabled={saving}
                  >
                    <X size={16} />
                    Cancel
                  </button>
                  <button 
                    className="btn btn-primary"
                    onClick={handleSubmit}
                    disabled={saving}
                  >
                    {saving ? (
                      <Loader size={16} className="spinner" />
                    ) : (
                      <Save size={16} />
                    )}
                    {saving ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              )}
            </div>

            <div className="profile-card-content">
              {/* Profile Picture Section */}
              <div className="profile-picture-section">
                <div className="profile-picture-container">
                  <div className="profile-picture">
                    {profileData?.profile_picture ? (
                      <img 
                        src={profileData.profile_picture} 
                        alt="Profile" 
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    <div className="profile-picture-placeholder">
                      <User size={40} />
                    </div>
                  </div>
                  <div className="profile-picture-upload">
                    <label htmlFor="profile-picture-input" className="upload-label">
                      <Camera size={16} />
                      Change Photo
                    </label>
                    <input
                      id="profile-picture-input"
                      type="file"
                      accept="image/*"
                      onChange={handleProfilePictureChange}
                      disabled={saving}
                      style={{ display: 'none' }}
                    />
                  </div>
                </div>
                <div className="profile-picture-info">
                  <h3>{profileData?.full_name || `${profileData?.first_name || ''} ${profileData?.last_name || ''}`.trim() || 'User Name'}</h3>
                  <p>{profileData?.role?.charAt(0).toUpperCase() + profileData?.role?.slice(1) || 'Role'}</p>
                  <div className="profile-badges">
                    {profileData?.is_email_verified && (
                      <span className="badge verified">✓ Verified</span>
                    )}
                    {profileData?.role === 'mentor' && profileData?.is_mentor_approved && (
                      <span className="badge approved">✓ Approved Mentor</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Form Fields */}
              <form onSubmit={handleSubmit} className="profile-form">
                <div className="form-grid">
                  {/* Basic Information */}
                  <div className="form-section">
                    <h4>Basic Information</h4>
                    <div className="form-row">
                      <div className="form-group">
                        <label htmlFor="first_name">First Name</label>
                        <input
                          type="text"
                          id="first_name"
                          name="first_name"
                          value={formData.first_name || ''}
                          onChange={handleInputChange}
                          disabled={!editing}
                          required
                        />
                      </div>
                      <div className="form-group">
                        <label htmlFor="last_name">Last Name</label>
                        <input
                          type="text"
                          id="last_name"
                          name="last_name"
                          value={formData.last_name || ''}
                          onChange={handleInputChange}
                          disabled={!editing}
                          required
                        />
                      </div>
                    </div>
                    
                    <div className="form-group">
                      <label htmlFor="email">Email Address</label>
                      <div className="input-with-icon">
                        <Mail size={20} />
                        <input
                          type="email"
                          id="email"
                          name="email"
                          value={formData.email || ''}
                          onChange={handleInputChange}
                          disabled={!editing}
                          required
                        />
                      </div>
                    </div>

                    <div className="form-row">
                      <div className="form-group">
                        <label htmlFor="phone_number">Phone Number</label>
                        <div className="input-with-icon">
                          <Phone size={20} />
                          <input
                            type="tel"
                            id="phone_number"
                            name="phone_number"
                            value={formData.phone_number || ''}
                            onChange={handleInputChange}
                            disabled={!editing}
                          />
                        </div>
                      </div>
                      <div className="form-group">
                        <label htmlFor="date_of_birth">Date of Birth</label>
                        <div className="input-with-icon">
                          <Calendar size={20} />
                          <input
                            type="date"
                            id="date_of_birth"
                            name="date_of_birth"
                            value={formData.date_of_birth || ''}
                            onChange={handleInputChange}
                            disabled={!editing}
                          />
                        </div>
                      </div>
                    </div>

                    <div className="form-group">
                      <label htmlFor="country">Country</label>
                      <div className="input-with-icon">
                        <MapPin size={20} />
                        <select
                          id="country"
                          name="country"
                          value={formData.country || ''}
                          onChange={handleInputChange}
                          disabled={!editing}
                        >
                          <option value="">Select Country</option>
                          <option value="US">United States</option>
                          <option value="CA">Canada</option>
                          <option value="UK">United Kingdom</option>
                          <option value="AU">Australia</option>
                          <option value="DE">Germany</option>
                          <option value="FR">France</option>
                          <option value="IN">India</option>
                          <option value="JP">Japan</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Professional Information */}
                  <div className="form-section">
                    <h4>Professional Information</h4>
                    
                    <div className="form-group">
                      <label htmlFor="bio">Bio</label>
                      <textarea
                        id="bio"
                        name="bio"
                        value={formData.bio || ''}
                        onChange={handleInputChange}
                        disabled={!editing}
                        rows="4"
                        placeholder="Tell us about yourself, your experience, and interests..."
                      />
                    </div>

                    {profileData?.role === 'mentor' && (
                      <>
                        <div className="form-group">
                          <label htmlFor="mentor_bio">Mentor Bio</label>
                          <textarea
                            id="mentor_bio"
                            name="mentor_bio"
                            value={formData.mentor_bio || ''}
                            onChange={handleInputChange}
                            disabled={!editing}
                            rows="4"
                            placeholder="Describe your mentoring experience and expertise..."
                          />
                        </div>
                        
                        <div className="form-row">
                          <div className="form-group">
                            <label htmlFor="experience_level">Experience Level</label>
                            <select
                              id="experience_level"
                              name="experience_level"
                              value={formData.experience_level || ''}
                              onChange={handleInputChange}
                              disabled={!editing}
                            >
                              <option value="">Select Level</option>
                              <option value="junior">Junior (1-3 years)</option>
                              <option value="mid">Mid-level (3-7 years)</option>
                              <option value="senior">Senior (7-12 years)</option>
                              <option value="expert">Expert (12+ years)</option>
                            </select>
                          </div>
                          <div className="form-group">
                            <label htmlFor="hourly_rate">Hourly Rate ($)</label>
                            <input
                              type="number"
                              id="hourly_rate"
                              name="hourly_rate"
                              value={formData.hourly_rate || ''}
                              onChange={handleInputChange}
                              disabled={!editing}
                              min="0"
                              step="1"
                            />
                          </div>
                        </div>
                      </>
                    )}

                    {profileData?.role === 'learner' && (
                      <div className="form-group">
                        <label htmlFor="learning_goals">Learning Goals</label>
                        <textarea
                          id="learning_goals"
                          name="learning_goals"
                          value={formData.learning_goals || ''}
                          onChange={handleInputChange}
                          disabled={!editing}
                          rows="3"
                          placeholder="What are your learning objectives and goals?"
                        />
                      </div>
                    )}
                  </div>

                  {/* Social Links */}
                  <div className="form-section">
                    <h4>Social Links</h4>
                    
                    <div className="form-group">
                      <label htmlFor="linkedin_url">LinkedIn Profile</label>
                      <div className="input-with-icon">
                        <Linkedin size={20} />
                        <input
                          type="url"
                          id="linkedin_url"
                          name="linkedin_url"
                          value={formData.linkedin_url || ''}
                          onChange={handleInputChange}
                          disabled={!editing}
                          placeholder="https://linkedin.com/in/yourprofile"
                        />
                      </div>
                    </div>

                    <div className="form-group">
                      <label htmlFor="github_url">GitHub Profile</label>
                      <div className="input-with-icon">
                        <Github size={20} />
                        <input
                          type="url"
                          id="github_url"
                          name="github_url"
                          value={formData.github_url || ''}
                          onChange={handleInputChange}
                          disabled={!editing}
                          placeholder="https://github.com/yourusername"
                        />
                      </div>
                    </div>

                    <div className="form-group">
                      <label htmlFor="portfolio_url">Portfolio Website</label>
                      <div className="input-with-icon">
                        <Globe size={20} />
                        <input
                          type="url"
                          id="portfolio_url"
                          name="portfolio_url"
                          value={formData.portfolio_url || ''}
                          onChange={handleInputChange}
                          disabled={!editing}
                          placeholder="https://yourportfolio.com"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </form>
            </div>
          </div>

          {/* Stats Card */}
          <div className="profile-card stats-card">
            <div className="profile-card-header">
              <h2>Profile Stats</h2>
            </div>
            <div className="profile-card-content">
              <div className="stats-grid">
                <div className="stat-item">
                  <div className="stat-icon">
                    <BookOpen size={24} />
                  </div>
                  <div className="stat-info">
                    <span className="stat-value">
                      {profileData?.role === 'learner' ? '12' : '48'}
                    </span>
                    <span className="stat-label">
                      {profileData?.role === 'learner' ? 'Sessions Attended' : 'Sessions Taught'}
                    </span>
                  </div>
                </div>
                
                <div className="stat-item">
                  <div className="stat-icon">
                    <Users size={24} />
                  </div>
                  <div className="stat-info">
                    <span className="stat-value">
                      {profileData?.role === 'learner' ? '8' : '25'}
                    </span>
                    <span className="stat-label">
                      {profileData?.role === 'learner' ? 'Mentors Met' : 'Students Taught'}
                    </span>
                  </div>
                </div>

                <div className="stat-item">
                  <div className="stat-icon">
                    <Clock size={24} />
                  </div>
                  <div className="stat-info">
                    <span className="stat-value">42h</span>
                    <span className="stat-label">Total Hours</span>
                  </div>
                </div>

                <div className="stat-item">
                  <div className="stat-icon">
                    <Star size={24} />
                  </div>
                  <div className="stat-info">
                    <span className="stat-value">
                      {profileData?.role === 'learner' ? '4.8' : '4.9'}
                    </span>
                    <span className="stat-label">
                      {profileData?.role === 'learner' ? 'Avg Rating' : 'Mentor Rating'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="profile-card actions-card">
            <div className="profile-card-header">
              <h2>Quick Actions</h2>
            </div>
            <div className="profile-card-content">
              <div className="quick-actions">
                <button className="action-btn" onClick={() => setEditing(true)}>
                  <Edit3 size={20} />
                  <span>Edit Profile</span>
                </button>
                <button className="action-btn">
                  <Award size={20} />
                  <span>View Badges</span>
                </button>
                <button className="action-btn">
                  <Target size={20} />
                  <span>Set Goals</span>
                </button>
                <button className="action-btn">
                  <BookOpen size={20} />
                  <span>Learning History</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
