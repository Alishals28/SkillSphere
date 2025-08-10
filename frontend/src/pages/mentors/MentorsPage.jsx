import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Search, 
  Filter, 
  Star, 
  Clock, 
  Users, 
  MapPin,
  Calendar,
  ChevronDown,
  SlidersHorizontal,
  Award,
  Bookmark,
  BookmarkCheck,
  MessageSquare,
  Video
} from 'lucide-react';
import './MentorsPage.css';

const MentorsPage = () => {
  const { user } = useAuth();
  const [mentors, setMentors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');
  const [selectedRating, setSelectedRating] = useState('');
  const [selectedPrice, setSelectedPrice] = useState('');
  const [sortBy, setSortBy] = useState('rating');
  const [showFilters, setShowFilters] = useState(false);
  const [savedMentors, setSavedMentors] = useState(new Set());

  // Mock mentors data
  useEffect(() => {
    setTimeout(() => {
      setMentors([
        {
          id: 1,
          name: 'Dr. Sarah Martinez',
          title: 'Senior Frontend Developer',
          avatar: null,
          rating: 4.9,
          reviewCount: 127,
          hourlyRate: 45,
          location: 'San Francisco, CA',
          expertise: ['React', 'JavaScript', 'TypeScript', 'Next.js', 'CSS'],
          bio: 'Senior Frontend Developer with 8+ years experience. Specialized in React ecosystem and modern web technologies. I help developers build scalable applications.',
          languages: ['English', 'Spanish'],
          availability: 'Available this week',
          sessionTypes: ['1-on-1 Mentoring', 'Code Review', 'Project Help'],
          totalSessions: 245,
          responseTime: '< 1 hour',
          badges: ['Top Mentor', 'Quick Responder'],
          specialties: ['Career Guidance', 'Technical Interview Prep']
        },
        {
          id: 2,
          name: 'Prof. Michael Chen',
          title: 'ML Research Scientist',
          avatar: null,
          rating: 4.8,
          reviewCount: 89,
          hourlyRate: 55,
          location: 'Boston, MA',
          expertise: ['Python', 'Machine Learning', 'Data Science', 'TensorFlow', 'PyTorch'],
          bio: 'PhD in Computer Science with focus on ML and AI. Currently researching at MIT. I mentor students and professionals in data science careers.',
          languages: ['English', 'Mandarin'],
          availability: 'Available tomorrow',
          sessionTypes: ['Research Guidance', 'Career Mentoring', 'Technical Deep Dive'],
          totalSessions: 156,
          responseTime: '< 2 hours',
          badges: ['PhD Mentor', 'Research Expert'],
          specialties: ['PhD Applications', 'Research Papers', 'ML Career Path']
        },
        {
          id: 3,
          name: 'Emma Thompson',
          title: 'UI/UX Design Lead',
          avatar: null,
          rating: 4.9,
          reviewCount: 156,
          hourlyRate: 40,
          location: 'London, UK',
          expertise: ['UI/UX Design', 'Figma', 'Design Systems', 'User Research', 'CSS'],
          bio: 'Creative design lead with 6+ years in product design. I help designers and developers create beautiful, user-centered interfaces.',
          languages: ['English', 'French'],
          availability: 'Available today',
          sessionTypes: ['Design Review', 'Portfolio Help', 'Career Advice'],
          totalSessions: 298,
          responseTime: '< 30 minutes',
          badges: ['Design Expert', 'Top Rated'],
          specialties: ['Portfolio Review', 'Design Systems', 'Career Transition']
        },
        {
          id: 4,
          name: 'Alex Rodriguez',
          title: 'Full Stack Engineer',
          avatar: null,
          rating: 4.7,
          reviewCount: 203,
          hourlyRate: 50,
          location: 'Austin, TX',
          expertise: ['Node.js', 'React', 'PostgreSQL', 'AWS', 'Docker'],
          bio: 'Full-stack engineer with startup experience. I mentor on building scalable web applications and modern development practices.',
          languages: ['English', 'Spanish'],
          availability: 'Available this week',
          sessionTypes: ['Code Review', 'System Design', 'DevOps Guidance'],
          totalSessions: 189,
          responseTime: '< 3 hours',
          badges: ['Startup Expert', 'Full Stack Pro'],
          specialties: ['System Architecture', 'Startup Tech Stack', 'DevOps']
        }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const subjects = [
    'All', 'React', 'JavaScript', 'Python', 'UI/UX Design', 
    'Machine Learning', 'Node.js', 'Data Science', 'CSS', 'AWS'
  ];

  const ratingOptions = [
    { value: '', label: 'All Ratings' },
    { value: '4.5', label: '4.5+ Stars' },
    { value: '4.0', label: '4.0+ Stars' },
    { value: '3.5', label: '3.5+ Stars' }
  ];

  const priceOptions = [
    { value: '', label: 'All Prices' },
    { value: '0-25', label: '$0 - $25' },
    { value: '25-50', label: '$25 - $50' },
    { value: '50-75', label: '$50 - $75' },
    { value: '75+', label: '$75+' }
  ];

  const sortOptions = [
    { value: 'rating', label: 'Highest Rated' },
    { value: 'price-low', label: 'Price: Low to High' },
    { value: 'price-high', label: 'Price: High to Low' },
    { value: 'experience', label: 'Most Experienced' },
    { value: 'availability', label: 'Available Soonest' }
  ];

  const filteredAndSortedMentors = mentors
    .filter(mentor => {
      const matchesSearch = mentor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           mentor.expertise.some(skill => skill.toLowerCase().includes(searchTerm.toLowerCase())) ||
                           mentor.bio.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesSubject = selectedSubject === '' || selectedSubject === 'All' ||
                            mentor.expertise.some(skill => skill.toLowerCase().includes(selectedSubject.toLowerCase()));
      
      const matchesRating = selectedRating === '' || mentor.rating >= parseFloat(selectedRating);
      
      const matchesPrice = selectedPrice === '' || (() => {
        if (selectedPrice === '75+') return mentor.hourlyRate >= 75;
        const [min, max] = selectedPrice.split('-').map(Number);
        return mentor.hourlyRate >= min && mentor.hourlyRate <= max;
      })();

      return matchesSearch && matchesSubject && matchesRating && matchesPrice;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'rating':
          return b.rating - a.rating;
        case 'price-low':
          return a.hourlyRate - b.hourlyRate;
        case 'price-high':
          return b.hourlyRate - a.hourlyRate;
        case 'experience':
          return b.totalSessions - a.totalSessions;
        default:
          return 0;
      }
    });

  const toggleSaveMentor = (mentorId) => {
    const newSaved = new Set(savedMentors);
    if (newSaved.has(mentorId)) {
      newSaved.delete(mentorId);
    } else {
      newSaved.add(mentorId);
    }
    setSavedMentors(newSaved);
  };

  const bookSession = (mentorId) => {
    window.location.href = `/book-session?mentor=${mentorId}`;
  };

  const sendMessage = (mentorId) => {
    window.location.href = `/messages?mentor=${mentorId}`;
  };

  if (loading) {
    return (
      <div className="mentors-page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading mentors...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mentors-page">
      <div className="mentors-container">
        {/* Header */}
        <div className="page-header">
          <div className="header-content">
            <h1>Find Your Perfect Mentor</h1>
            <p>Connect with experienced professionals who can guide your learning journey</p>
          </div>
          
          <div className="header-stats">
            <div className="stat">
              <span className="stat-number">{mentors.length}+</span>
              <span className="stat-label">Expert Mentors</span>
            </div>
            <div className="stat">
              <span className="stat-number">500+</span>
              <span className="stat-label">Skills Covered</span>
            </div>
            <div className="stat">
              <span className="stat-number">95%</span>
              <span className="stat-label">Success Rate</span>
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="search-section">
          <div className="main-search">
            <div className="search-bar">
              <Search size={20} />
              <input
                type="text"
                placeholder="Search by name, skill, or expertise..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            
            <button 
              className={`filters-toggle ${showFilters ? 'active' : ''}`}
              onClick={() => setShowFilters(!showFilters)}
            >
              <SlidersHorizontal size={20} />
              Filters
              {showFilters && <span className="filter-count">4</span>}
            </button>
          </div>

          {showFilters && (
            <div className="filters-panel">
              <div className="filter-group">
                <label>Subject</label>
                <select value={selectedSubject} onChange={(e) => setSelectedSubject(e.target.value)}>
                  {subjects.map(subject => (
                    <option key={subject} value={subject}>{subject}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label>Rating</label>
                <select value={selectedRating} onChange={(e) => setSelectedRating(e.target.value)}>
                  {ratingOptions.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label>Price Range</label>
                <select value={selectedPrice} onChange={(e) => setSelectedPrice(e.target.value)}>
                  {priceOptions.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label>Sort By</label>
                <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                  {sortOptions.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </div>

        {/* Results */}
        <div className="results-section">
          <div className="results-header">
            <h2>{filteredAndSortedMentors.length} Mentors Found</h2>
            <div className="quick-sort">
              <span>Sort by:</span>
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                {sortOptions.map(option => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="mentors-grid">
            {filteredAndSortedMentors.map(mentor => (
              <div key={mentor.id} className="mentor-card">
                <div className="mentor-header">
                  <div className="mentor-avatar">
                    {mentor.avatar ? (
                      <img src={mentor.avatar} alt={mentor.name} />
                    ) : (
                      <div className="avatar-placeholder">
                        {mentor.name.charAt(0)}
                      </div>
                    )}
                    <div className="online-status"></div>
                  </div>
                  
                  <div className="mentor-basic-info">
                    <h3>{mentor.name}</h3>
                    <p className="mentor-title">{mentor.title}</p>
                    <div className="mentor-location">
                      <MapPin size={14} />
                      <span>{mentor.location}</span>
                    </div>
                  </div>

                  <button 
                    className={`save-btn ${savedMentors.has(mentor.id) ? 'saved' : ''}`}
                    onClick={() => toggleSaveMentor(mentor.id)}
                  >
                    {savedMentors.has(mentor.id) ? 
                      <BookmarkCheck size={20} /> : 
                      <Bookmark size={20} />
                    }
                  </button>
                </div>

                <div className="mentor-stats">
                  <div className="stat-item">
                    <Star size={14} fill="currentColor" />
                    <span>{mentor.rating}</span>
                    <span className="reviews">({mentor.reviewCount})</span>
                  </div>
                  <div className="stat-item">
                    <Users size={14} />
                    <span>{mentor.totalSessions} sessions</span>
                  </div>
                  <div className="stat-item">
                    <Clock size={14} />
                    <span>{mentor.responseTime}</span>
                  </div>
                </div>

                <div className="mentor-badges">
                  {mentor.badges.map(badge => (
                    <span key={badge} className="badge">
                      <Award size={12} />
                      {badge}
                    </span>
                  ))}
                </div>

                <div className="mentor-expertise">
                  {mentor.expertise.slice(0, 4).map(skill => (
                    <span key={skill} className="skill-tag">{skill}</span>
                  ))}
                  {mentor.expertise.length > 4 && (
                    <span className="more-skills">+{mentor.expertise.length - 4} more</span>
                  )}
                </div>

                <p className="mentor-bio">{mentor.bio}</p>

                <div className="mentor-specialties">
                  <h4>Specializes in:</h4>
                  <div className="specialties-list">
                    {mentor.specialties.map(specialty => (
                      <span key={specialty} className="specialty">{specialty}</span>
                    ))}
                  </div>
                </div>

                <div className="mentor-footer">
                  <div className="pricing">
                    <span className="price">${mentor.hourlyRate}/hour</span>
                    <span className="availability">{mentor.availability}</span>
                  </div>
                  
                  <div className="action-buttons">
                    <button 
                      className="message-btn"
                      onClick={() => sendMessage(mentor.id)}
                    >
                      <MessageSquare size={16} />
                      Message
                    </button>
                    <button 
                      className="book-btn"
                      onClick={() => bookSession(mentor.id)}
                    >
                      <Video size={16} />
                      Book Session
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredAndSortedMentors.length === 0 && (
            <div className="no-results">
              <Users className="no-results-icon" />
              <h3>No mentors found</h3>
              <p>Try adjusting your search criteria or filters</p>
              <button onClick={() => {
                setSearchTerm('');
                setSelectedSubject('');
                setSelectedRating('');
                setSelectedPrice('');
              }}>
                Clear All Filters
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MentorsPage;
