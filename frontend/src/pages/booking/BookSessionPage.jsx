import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Calendar, 
  Clock, 
  User, 
  Star, 
  Filter,
  Search,
  ChevronDown,
  ChevronRight,
  Book,
  Video,
  Users,
  ArrowLeft
} from 'lucide-react';
import './BookSessionPage.css';

const BookSessionPage = () => {
  const { user } = useAuth();
  const [step, setStep] = useState(1); // 1: Select Mentor, 2: Choose Session, 3: Schedule, 4: Confirm
  const [selectedMentor, setSelectedMentor] = useState(null);
  const [selectedSession, setSelectedSession] = useState(null);
  const [selectedDateTime, setSelectedDateTime] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');
  const [mentors, setMentors] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Advanced booking options
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurringType, setRecurringType] = useState('weekly'); // weekly, bi-weekly, monthly
  const [recurringCount, setRecurringCount] = useState(4);
  const [isGroupSession, setIsGroupSession] = useState(false);
  const [groupSize, setGroupSize] = useState(2);
  const [sessionNotes, setSessionNotes] = useState('');

  // Mock mentors data
  useEffect(() => {
    setMentors([
      {
        id: 1,
        name: 'Dr. Sarah Martinez',
        expertise: ['React', 'JavaScript', 'Frontend Development'],
        rating: 4.9,
        reviewCount: 127,
        hourlyRate: 45,
        avatar: null,
        bio: 'Senior Frontend Developer with 8+ years experience in React and modern web technologies.',
        availability: 'Available today',
        sessionTypes: [
          { id: 1, name: 'React Fundamentals', duration: 60, price: 45, supportsGroup: true },
          { id: 2, name: 'Advanced React Patterns', duration: 90, price: 65, supportsGroup: true },
          { id: 3, name: 'Code Review Session', duration: 45, price: 35, supportsGroup: false }
        ]
      },
      {
        id: 2,
        name: 'Prof. Michael Chen',
        expertise: ['Python', 'Data Science', 'Machine Learning'],
        rating: 4.8,
        reviewCount: 89,
        hourlyRate: 55,
        avatar: null,
        bio: 'PhD in Computer Science, specialized in ML and data analysis with industry experience.',
        availability: 'Available tomorrow',
        sessionTypes: [
          { id: 4, name: 'Python Basics', duration: 60, price: 55, supportsGroup: true },
          { id: 5, name: 'Data Analysis with Pandas', duration: 90, price: 75, supportsGroup: true },
          { id: 6, name: 'ML Model Building', duration: 120, price: 95, supportsGroup: false }
        ]
      },
      {
        id: 3,
        name: 'Emma Thompson',
        expertise: ['CSS', 'UI/UX Design', 'Frontend'],
        rating: 4.9,
        reviewCount: 156,
        hourlyRate: 40,
        avatar: null,
        bio: 'Creative frontend developer and UI/UX designer with passion for beautiful interfaces.',
        availability: 'Available this week',
        sessionTypes: [
          { id: 7, name: 'CSS Grid & Flexbox', duration: 75, price: 40 },
          { id: 8, name: 'UI/UX Design Principles', duration: 90, price: 50 },
          { id: 9, name: 'Responsive Design', duration: 60, price: 35 }
        ]
      }
    ]);
    setLoading(false);
  }, []);

  const subjects = ['All', 'React', 'JavaScript', 'Python', 'CSS', 'UI/UX', 'Data Science', 'Machine Learning'];

  const filteredMentors = mentors.filter(mentor => {
    const matchesSearch = mentor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         mentor.expertise.some(skill => skill.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesSubject = selectedSubject === '' || selectedSubject === 'All' ||
                          mentor.expertise.some(skill => skill.toLowerCase().includes(selectedSubject.toLowerCase()));
    return matchesSearch && matchesSubject;
  });

  const handleMentorSelect = (mentor) => {
    setSelectedMentor(mentor);
    setStep(2);
  };

  const handleSessionSelect = (sessionType) => {
    setSelectedSession(sessionType);
    setStep(3);
  };

  const handleDateTimeSelect = (dateTime) => {
    setSelectedDateTime(dateTime);
    setStep(4);
  };

  const handleBackStep = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const goToMentors = () => {
    window.location.href = '/mentors';
  };

  if (loading) {
    return (
      <div className="book-session-page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading mentors...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="book-session-page">
      <div className="booking-container">
        {/* Header */}
        <div className="booking-header">
          <div className="header-content">
            {step > 1 && (
              <button className="back-btn" onClick={handleBackStep}>
                <ArrowLeft size={20} />
                Back
              </button>
            )}
            <div className="header-text">
              <h1>Book a Session</h1>
              <p>Find the perfect mentor and schedule your learning session</p>
            </div>
          </div>

          {/* Progress Steps */}
          <div className="progress-steps">
            <div className={`step ${step >= 1 ? 'active' : ''}`}>
              <div className="step-number">1</div>
              <span>Select Mentor</span>
            </div>
            <div className={`step ${step >= 2 ? 'active' : ''}`}>
              <div className="step-number">2</div>
              <span>Choose Session</span>
            </div>
            <div className={`step ${step >= 3 ? 'active' : ''}`}>
              <div className="step-number">3</div>
              <span>Schedule</span>
            </div>
            <div className={`step ${step >= 4 ? 'active' : ''}`}>
              <div className="step-number">4</div>
              <span>Confirm</span>
            </div>
          </div>
        </div>

        {/* Step Content */}
        <div className="step-content">
          {step === 1 && (
            <div className="mentor-selection">
              <div className="search-filters">
                <div className="search-bar">
                  <Search size={20} />
                  <input
                    type="text"
                    placeholder="Search mentors by name or skill..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <div className="subject-filter">
                  <select 
                    value={selectedSubject} 
                    onChange={(e) => setSelectedSubject(e.target.value)}
                  >
                    {subjects.map(subject => (
                      <option key={subject} value={subject}>{subject}</option>
                    ))}
                  </select>
                  <ChevronDown size={16} />
                </div>
                <button className="browse-all-btn" onClick={goToMentors}>
                  <Users size={16} />
                  Browse All Mentors
                </button>
              </div>

              <div className="mentors-grid">
                {filteredMentors.map(mentor => (
                  <div key={mentor.id} className="mentor-card" onClick={() => handleMentorSelect(mentor)}>
                    <div className="mentor-avatar">
                      {mentor.avatar ? (
                        <img src={mentor.avatar} alt={mentor.name} />
                      ) : (
                        <div className="avatar-placeholder">
                          {mentor.name.charAt(0)}
                        </div>
                      )}
                      <div className="availability-indicator">
                        <div className="status-dot"></div>
                        {mentor.availability}
                      </div>
                    </div>
                    
                    <div className="mentor-info">
                      <h3>{mentor.name}</h3>
                      <div className="mentor-rating">
                        <Star size={14} fill="currentColor" />
                        <span>{mentor.rating}</span>
                        <span className="review-count">({mentor.reviewCount} reviews)</span>
                      </div>
                      <div className="mentor-expertise">
                        {mentor.expertise.slice(0, 3).map(skill => (
                          <span key={skill} className="skill-tag">{skill}</span>
                        ))}
                      </div>
                      <p className="mentor-bio">{mentor.bio}</p>
                      <div className="mentor-rate">
                        <span className="rate">${mentor.hourlyRate}/hour</span>
                      </div>
                    </div>
                    
                    <div className="select-mentor-btn">
                      <span>Select Mentor</span>
                      <ChevronRight size={16} />
                    </div>
                  </div>
                ))}
              </div>

              {filteredMentors.length === 0 && (
                <div className="no-results">
                  <Users className="no-results-icon" />
                  <h3>No mentors found</h3>
                  <p>Try adjusting your search criteria or browse all mentors</p>
                  <button className="browse-all-btn" onClick={goToMentors}>
                    Browse All Mentors
                  </button>
                </div>
              )}
            </div>
          )}

          {step === 2 && selectedMentor && (
            <div className="session-selection">
              <div className="selected-mentor-info">
                <div className="mentor-summary">
                  <div className="mentor-avatar-small">
                    {selectedMentor.avatar ? (
                      <img src={selectedMentor.avatar} alt={selectedMentor.name} />
                    ) : (
                      <div className="avatar-placeholder">
                        {selectedMentor.name.charAt(0)}
                      </div>
                    )}
                  </div>
                  <div>
                    <h3>{selectedMentor.name}</h3>
                    <div className="mentor-rating">
                      <Star size={14} fill="currentColor" />
                      <span>{selectedMentor.rating}</span>
                      <span className="review-count">({selectedMentor.reviewCount} reviews)</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="session-types">
                <h3>Choose a Session Type</h3>
                <div className="session-grid">
                  {selectedMentor.sessionTypes.map(sessionType => (
                    <div 
                      key={sessionType.id} 
                      className="session-card"
                      onClick={() => handleSessionSelect(sessionType)}
                    >
                      <div className="session-icon">
                        <Video size={24} />
                      </div>
                      <div className="session-details">
                        <h4>{sessionType.name}</h4>
                        <div className="session-meta">
                          <span className="duration">
                            <Clock size={14} />
                            {sessionType.duration} minutes
                          </span>
                          <span className="price">${sessionType.price}</span>
                        </div>
                      </div>
                      <div className="select-session-btn">
                        <ChevronRight size={16} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {step === 3 && selectedMentor && selectedSession && (
            <div className="schedule-selection">
              <div className="session-summary">
                <h3>Configure Your Session</h3>
                <div className="summary-card">
                  <div className="summary-info">
                    <span className="session-name">{selectedSession.name}</span>
                    <span className="mentor-name">with {selectedMentor.name}</span>
                    <span className="session-duration">{selectedSession.duration} minutes • ${selectedSession.price}</span>
                  </div>
                </div>
              </div>

              {/* Advanced Booking Options */}
              <div className="booking-options">
                <div className="option-group">
                  <h4>Session Type</h4>
                  
                  {/* Group Session Option */}
                  <div className="option-card">
                    <div className="option-header">
                      <div className="checkbox-wrapper">
                        <input
                          type="checkbox"
                          id="group-session"
                          checked={isGroupSession}
                          onChange={(e) => setIsGroupSession(e.target.checked)}
                          disabled={!selectedSession?.supportsGroup}
                        />
                        <label htmlFor="group-session">
                          <Users size={20} />
                          Group Session
                          {!selectedSession?.supportsGroup && (
                            <span className="not-available">(Not available for this session)</span>
                          )}
                        </label>
                      </div>
                      {selectedSession?.supportsGroup && (
                        <span className="option-badge">Popular</span>
                      )}
                    </div>
                    <p>
                      {selectedSession?.supportsGroup 
                        ? 'Learn together with other students (additional discount applies)'
                        : 'This session type requires individual attention and cannot be conducted in groups'
                      }
                    </p>
                    
                    {isGroupSession && (
                      <div className="group-config">
                        <label>Group Size (including you):</label>
                        <select 
                          value={groupSize} 
                          onChange={(e) => setGroupSize(parseInt(e.target.value))}
                        >
                          <option value={2}>2 participants</option>
                          <option value={3}>3 participants</option>
                          <option value={4}>4 participants</option>
                          <option value={5}>5 participants</option>
                        </select>
                        <div className="price-info">
                          <span className="original-price">${selectedSession.price}</span>
                          <span className="group-price">${Math.round(selectedSession.price * 0.8)} per person</span>
                          <span className="savings">Save 20%!</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Recurring Session Option */}
                  <div className="option-card">
                    <div className="option-header">
                      <div className="checkbox-wrapper">
                        <input
                          type="checkbox"
                          id="recurring-session"
                          checked={isRecurring}
                          onChange={(e) => setIsRecurring(e.target.checked)}
                        />
                        <label htmlFor="recurring-session">
                          <Calendar size={20} />
                          Recurring Sessions
                        </label>
                      </div>
                      <span className="option-badge recommended">Recommended</span>
                    </div>
                    <p>Book multiple sessions at once for consistent learning progress</p>
                    
                    {isRecurring && (
                      <div className="recurring-config">
                        <div className="config-row">
                          <label>Frequency:</label>
                          <select 
                            value={recurringType} 
                            onChange={(e) => setRecurringType(e.target.value)}
                          >
                            <option value="weekly">Weekly</option>
                            <option value="bi-weekly">Bi-weekly</option>
                            <option value="monthly">Monthly</option>
                          </select>
                        </div>
                        <div className="config-row">
                          <label>Number of sessions:</label>
                          <select 
                            value={recurringCount} 
                            onChange={(e) => setRecurringCount(parseInt(e.target.value))}
                          >
                            <option value={4}>4 sessions</option>
                            <option value={6}>6 sessions</option>
                            <option value={8}>8 sessions</option>
                            <option value={12}>12 sessions</option>
                          </select>
                        </div>
                        <div className="price-info">
                          <span className="total-price">
                            Total: ${Math.round(selectedSession.price * recurringCount * 0.9)} 
                          </span>
                          <span className="savings">Save 10% on package!</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Session Notes */}
                <div className="option-group">
                  <h4>Additional Information</h4>
                  <div className="notes-section">
                    <label htmlFor="session-notes">
                      Special requests or learning goals:
                    </label>
                    <textarea
                      id="session-notes"
                      value={sessionNotes}
                      onChange={(e) => setSessionNotes(e.target.value)}
                      placeholder="Tell your mentor what you'd like to focus on, any specific topics, or preparation you've done..."
                      rows={4}
                    />
                  </div>
                </div>
              </div>

              <div className="calendar-section">
                <div className="calendar-placeholder">
                  <Calendar size={48} />
                  <h4>Select Date & Time</h4>
                  <p>Calendar integration coming soon</p>
                  <button 
                    className="proceed-btn"
                    onClick={() => handleDateTimeSelect('Tomorrow at 2:00 PM')}
                  >
                    Continue with Default Time
                  </button>
                </div>
              </div>
            </div>
          )}

          {step === 4 && selectedMentor && selectedSession && selectedDateTime && (
            <div className="booking-confirmation">
              <div className="confirmation-header">
                <div className="success-icon">
                  <Book size={32} />
                </div>
                <h2>Review Your Booking</h2>
                <p>Please review the details before confirming your session</p>
              </div>

              <div className="booking-summary">
                <div className="summary-section">
                  <h4>Mentor</h4>
                  <div className="mentor-summary">
                    <div className="mentor-avatar-small">
                      {selectedMentor.avatar ? (
                        <img src={selectedMentor.avatar} alt={selectedMentor.name} />
                      ) : (
                        <div className="avatar-placeholder">
                          {selectedMentor.name.charAt(0)}
                        </div>
                      )}
                    </div>
                    <div>
                      <span className="mentor-name">{selectedMentor.name}</span>
                      <div className="mentor-rating">
                        <Star size={12} fill="currentColor" />
                        <span>{selectedMentor.rating}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="summary-section">
                  <h4>Session Details</h4>
                  <div className="session-summary">
                    <span className="session-name">{selectedSession.name}</span>
                    <span className="session-duration">{selectedSession.duration} minutes</span>
                    <span className="session-time">{selectedDateTime}</span>
                    
                    {isGroupSession && (
                      <div className="booking-feature">
                        <Users size={16} />
                        <span>Group session ({groupSize} participants)</span>
                      </div>
                    )}
                    
                    {isRecurring && (
                      <div className="booking-feature">
                        <Calendar size={16} />
                        <span>Recurring {recurringType} ({recurringCount} sessions)</span>
                      </div>
                    )}
                    
                    {sessionNotes && (
                      <div className="session-notes-summary">
                        <h5>Your Notes:</h5>
                        <p>"{sessionNotes}"</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="summary-section">
                  <h4>Payment</h4>
                  <div className="payment-summary">
                    <div className="payment-line">
                      <span>
                        Session fee
                        {isRecurring && ` (${recurringCount} sessions)`}
                        {isGroupSession && ` (${groupSize} participants)`}
                      </span>
                      <span>${
                        isRecurring 
                          ? Math.round(selectedSession.price * recurringCount * 0.9)
                          : isGroupSession 
                            ? Math.round(selectedSession.price * 0.8) 
                            : selectedSession.price
                      }</span>
                    </div>
                    
                    {(isRecurring || isGroupSession) && (
                      <div className="payment-line discount">
                        <span>
                          {isRecurring ? 'Package discount (10%)' : 'Group discount (20%)'}
                        </span>
                        <span>-${
                          isRecurring 
                            ? Math.round(selectedSession.price * recurringCount * 0.1)
                            : isGroupSession 
                              ? Math.round(selectedSession.price * 0.2)
                              : 0
                        }</span>
                      </div>
                    )}
                    
                    <div className="payment-line">
                      <span>Platform fee</span>
                      <span>$2</span>
                    </div>
                    <div className="payment-line total">
                      <span>Total</span>
                      <span>${
                        (isRecurring 
                          ? Math.round(selectedSession.price * recurringCount * 0.9)
                          : isGroupSession 
                            ? Math.round(selectedSession.price * 0.8) 
                            : selectedSession.price) + 2
                      }</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="confirmation-actions">
                <button className="confirm-btn">
                  Confirm & Pay ${
                    (isRecurring 
                      ? Math.round(selectedSession.price * recurringCount * 0.9)
                      : isGroupSession 
                        ? Math.round(selectedSession.price * 0.8) 
                        : selectedSession.price) + 2
                  }
                </button>
                <p className="terms-text">
                  By confirming, you agree to our Terms of Service and Payment Policy
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BookSessionPage;
