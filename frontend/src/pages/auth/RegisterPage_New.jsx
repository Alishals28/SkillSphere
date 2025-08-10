import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Button from '../../components/ui/Button';
import { 
  Mail, Lock, Eye, EyeOff, User, Phone, Globe, 
  Calendar, Briefcase, Target, Clock,
  Upload, Sparkles
} from 'lucide-react';

const RegisterPage = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    // Basic Info
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    role: '',
    
    // Contact & Profile
    phone: '',
    country: '',
    dateOfBirth: '',
    bio: '',
    timezone: 'UTC',
    profilePicture: null,
    
    // Role-specific fields
    learningGoals: '',
    experienceLevel: '',
    preferredSessionDuration: 60,
    
    // Mentor fields
    mentorBio: '',
    teachingExperience: '',
    hourlyRate: '',
    portfolioUrl: '',
    linkedinUrl: '',
    githubUrl: '',
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  
  const { register } = useAuth();

  const handleChange = (e) => {
    const { name, value, type, files } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'file' ? files[0] : value,
    }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  const validateEmail = (email) => {
    return email.includes('@') && email.includes('.');
  };

  const validatePassword = (password) => {
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    const hasAlphaNumeric = /^(?=.*[a-zA-Z])(?=.*\d)/.test(password);
    return password.length >= 8 && hasSpecialChar && hasAlphaNumeric;
  };

  const validateStep = (step) => {
    switch (step) {
      case 1:
        if (!formData.email || !validateEmail(formData.email)) {
          setError('Please enter a valid email address');
          return false;
        }
        if (!formData.password || !validatePassword(formData.password)) {
          setError('Password must be 8+ characters with letters, numbers, and special characters');
          return false;
        }
        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match');
          return false;
        }
        if (!formData.firstName || !formData.lastName) {
          setError('First and last names are required');
          return false;
        }
        if (!formData.role) {
          setError('Please select your role');
          return false;
        }
        break;
      case 2:
        if (!formData.bio.trim()) {
          setError('Bio is required');
          return false;
        }
        if (formData.role === 'mentor' && !formData.mentorBio.trim()) {
          setError('Detailed mentor bio is required');
          return false;
        }
        if (formData.role === 'mentor' && !formData.teachingExperience.trim()) {
          setError('Teaching experience is required for mentors');
          return false;
        }
        break;
      default:
        break;
    }
    return true;
  };

  const nextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const prevStep = () => {
    setCurrentStep(prev => prev - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateStep(currentStep)) return;
    
    setLoading(true);
    setError('');

    try {
      await register(formData);
      
      // Show approval modal for mentors
      if (formData.role === 'mentor') {
        setShowApprovalModal(true);
      }
      // Learners can proceed normally
    } catch (err) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const renderStep1 = () => (
    <div className="form-step">
      <div className="step-header">
        <h3>Basic Information</h3>
        <p>Let's start with the essentials</p>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="firstName">First Name</label>
          <div className="input-wrapper">
            <User size={20} className="input-icon" />
            <input
              type="text"
              id="firstName"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              required
              placeholder="Your first name"
              className="form-input"
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="lastName">Last Name</label>
          <div className="input-wrapper">
            <User size={20} className="input-icon" />
            <input
              type="text"
              id="lastName"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
              required
              placeholder="Your last name"
              className="form-input"
            />
          </div>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="email">Email Address</label>
        <div className="input-wrapper">
          <Mail size={20} className="input-icon" />
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            placeholder="Enter your email"
            className="form-input"
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <div className="input-wrapper">
            <Lock size={20} className="input-icon" />
            <input
              type={showPassword ? 'text' : 'password'}
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Create a password"
              className="form-input"
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password</label>
          <div className="input-wrapper">
            <Lock size={20} className="input-icon" />
            <input
              type={showConfirmPassword ? 'text' : 'password'}
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              placeholder="Confirm your password"
              className="form-input"
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            >
              {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          </div>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="role">I want to...</label>
        <div className="role-selection">
          <label className={`role-option ${formData.role === 'learner' ? 'selected' : ''}`}>
            <input
              type="radio"
              name="role"
              value="learner"
              checked={formData.role === 'learner'}
              onChange={handleChange}
            />
            <div className="role-content">
              <div className="role-icon">🎓</div>
              <div className="role-text">
                <h4>Learn Skills</h4>
                <p>Find mentors and improve my abilities</p>
              </div>
            </div>
          </label>

          <label className={`role-option ${formData.role === 'mentor' ? 'selected' : ''}`}>
            <input
              type="radio"
              name="role"
              value="mentor"
              checked={formData.role === 'mentor'}
              onChange={handleChange}
            />
            <div className="role-content">
              <div className="role-icon">👨‍🏫</div>
              <div className="role-text">
                <h4>Mentor Others</h4>
                <p>Share knowledge and guide learners</p>
              </div>
            </div>
          </label>
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="form-step">
      <div className="step-header">
        <h3>Profile Details</h3>
        <p>Tell us more about yourself</p>
      </div>

      <div className="form-group">
        <label htmlFor="bio">Bio</label>
        <textarea
          id="bio"
          name="bio"
          value={formData.bio}
          onChange={handleChange}
          required
          placeholder="Tell us about yourself, your interests, and what you hope to achieve..."
          className="form-textarea"
          rows="4"
        />
      </div>

      {formData.role === 'learner' && (
        <>
          <div className="form-group">
            <label htmlFor="learningGoals">Learning Goals</label>
            <textarea
              id="learningGoals"
              name="learningGoals"
              value={formData.learningGoals}
              onChange={handleChange}
              placeholder="What specific skills or knowledge do you want to gain?"
              className="form-textarea"
              rows="3"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="experienceLevel">Experience Level</label>
              <div className="input-wrapper">
                <Target size={20} className="input-icon" />
                <select
                  id="experienceLevel"
                  name="experienceLevel"
                  value={formData.experienceLevel}
                  onChange={handleChange}
                  className="form-input"
                >
                  <option value="">Select level</option>
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="preferredSessionDuration">Preferred Session Duration</label>
              <div className="input-wrapper">
                <Clock size={20} className="input-icon" />
                <select
                  id="preferredSessionDuration"
                  name="preferredSessionDuration"
                  value={formData.preferredSessionDuration}
                  onChange={handleChange}
                  className="form-input"
                >
                  <option value="30">30 minutes</option>
                  <option value="60">60 minutes</option>
                  <option value="90">90 minutes</option>
                  <option value="120">120 minutes</option>
                </select>
              </div>
            </div>
          </div>
        </>
      )}

      {formData.role === 'mentor' && (
        <>
          <div className="form-group">
            <label htmlFor="mentorBio">Detailed Mentor Bio</label>
            <textarea
              id="mentorBio"
              name="mentorBio"
              value={formData.mentorBio}
              onChange={handleChange}
              required
              placeholder="Describe your expertise, teaching style, and what makes you a great mentor..."
              className="form-textarea"
              rows="4"
            />
          </div>

          <div className="form-group">
            <label htmlFor="teachingExperience">Teaching Experience</label>
            <textarea
              id="teachingExperience"
              name="teachingExperience"
              value={formData.teachingExperience}
              onChange={handleChange}
              required
              placeholder="Describe your teaching background, certifications, and relevant experience..."
              className="form-textarea"
              rows="3"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="hourlyRate">Hourly Rate (USD)</label>
              <div className="input-wrapper">
                <span className="input-prefix">$</span>
                <input
                  type="number"
                  id="hourlyRate"
                  name="hourlyRate"
                  value={formData.hourlyRate}
                  onChange={handleChange}
                  placeholder="50"
                  min="10"
                  max="500"
                  className="form-input"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="portfolioUrl">Portfolio URL (Optional)</label>
              <div className="input-wrapper">
                <Globe size={20} className="input-icon" />
                <input
                  type="url"
                  id="portfolioUrl"
                  name="portfolioUrl"
                  value={formData.portfolioUrl}
                  onChange={handleChange}
                  placeholder="https://yourportfolio.com"
                  className="form-input"
                />
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );

  const renderApprovalModal = () => (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <div className="modal-icon">
            <Clock size={48} className="pending-icon" />
          </div>
          <h2>Application Under Review</h2>
        </div>
        <div className="modal-body">
          <p>
            Thank you for applying to become a mentor! Your application is being 
            reviewed by our admin team. This process typically takes 1-2 business days.
          </p>
          <p>
            In the meantime, you can explore the platform and access a limited 
            dashboard. You'll receive an email notification once your application 
            is approved.
          </p>
        </div>
        <div className="modal-footer">
          <Button 
            variant="primary" 
            onClick={() => setShowApprovalModal(false)}
          >
            Continue to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="auth-page">
      <div className="auth-container">
        {/* Left Side - Branding */}
        <div className="auth-branding">
          <div className="brand-content">
            <div className="brand-logo">
              <Sparkles size={48} className="logo-icon" />
              <h1 className="brand-title">SkillSphere</h1>
            </div>
            <h2 className="brand-subtitle">Join our community!</h2>
            <p className="brand-description">
              Connect with expert mentors or share your knowledge. 
              Start your journey towards skill mastery today.
            </p>
            
            {/* Progress Indicator */}
            <div className="progress-indicator">
              <div className="progress-steps">
                <div className={`progress-step ${currentStep >= 1 ? 'active' : ''}`}>
                  <div className="step-number">1</div>
                  <span>Basic Info</span>
                </div>
                <div className={`progress-step ${currentStep >= 2 ? 'active' : ''}`}>
                  <div className="step-number">2</div>
                  <span>Profile Details</span>
                </div>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${(currentStep / 2) * 100}%` }}
                ></div>
              </div>
            </div>

            <div className="brand-features">
              <div className="feature-item">
                <div className="feature-icon">🎯</div>
                <span>Personalized Learning</span>
              </div>
              <div className="feature-item">
                <div className="feature-icon">👥</div>
                <span>Expert Mentors</span>
              </div>
              <div className="feature-item">
                <div className="feature-icon">🚀</div>
                <span>Real Progress</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Registration Form */}
        <div className="auth-form-section">
          <div className="auth-form-container">
            <div className="form-header">
              <h2>Create Account</h2>
              <p>Join SkillSphere and start your learning journey</p>
            </div>
            
            {error && (
              <div className="error-message animate-slideDown">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="auth-form multi-step-form">
              {currentStep === 1 && renderStep1()}
              {currentStep === 2 && renderStep2()}

              <div className="form-actions">
                {currentStep > 1 && (
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={prevStep}
                    className="back-button"
                  >
                    Back
                  </Button>
                )}
                
                {currentStep < 2 ? (
                  <Button 
                    type="button" 
                    variant="primary" 
                    onClick={nextStep}
                    className="next-button"
                  >
                    Next Step
                  </Button>
                ) : (
                  <Button 
                    type="submit" 
                    variant="primary" 
                    disabled={loading}
                    className="submit-button"
                  >
                    {loading ? 'Creating Account...' : 'Create Account'}
                  </Button>
                )}
              </div>
            </form>

            <div className="auth-links">
              <p>
                Already have an account? {' '}
                <Link to="/login" className="auth-link">
                  Sign in here
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>

      {showApprovalModal && renderApprovalModal()}
    </div>
  );
};

export default RegisterPage;
