import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Calendar,
  Clock,
  Plus,
  Edit3,
  Trash2,
  Users,
  Video,
  MessageSquare,
  CheckCircle,
  XCircle,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Filter,
  Download,
  Settings
} from 'lucide-react';
import './SchedulePage.css';

const SchedulePage = () => {
  const { user } = useAuth();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [viewMode, setViewMode] = useState('month'); // month, week, day
  const [sessions, setSessions] = useState([]);
  const [availabilitySlots, setAvailabilitySlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedSession, setSelectedSession] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');

  // Mock data based on user role
  useEffect(() => {
    setTimeout(() => {
      if (user?.role === 'mentor') {
        setSessions([
          {
            id: 1,
            title: 'React Basics Session',
            studentName: 'Alice Johnson',
            studentAvatar: null,
            date: new Date(2024, 11, 20, 14, 0), // December 20, 2:00 PM
            duration: 60,
            type: '1-on-1 Mentoring',
            status: 'confirmed',
            meetingLink: 'https://meet.google.com/abc-def-ghi',
            notes: 'Cover React hooks and state management',
            price: 45
          },
          {
            id: 2,
            title: 'Code Review Session',
            studentName: 'Bob Smith',
            studentAvatar: null,
            date: new Date(2024, 11, 21, 10, 30), // December 21, 10:30 AM
            duration: 45,
            type: 'Code Review',
            status: 'pending',
            notes: 'Review portfolio project',
            price: 45
          },
          {
            id: 3,
            title: 'Project Help',
            studentName: 'Carol White',
            studentAvatar: null,
            date: new Date(2024, 11, 22, 16, 0), // December 22, 4:00 PM
            duration: 90,
            type: 'Project Help',
            status: 'confirmed',
            meetingLink: 'https://meet.google.com/xyz-abc-def',
            notes: 'Help with final project deployment',
            price: 67.5
          }
        ]);

        setAvailabilitySlots([
          { id: 1, day: 'Monday', startTime: '09:00', endTime: '17:00', active: true },
          { id: 2, day: 'Tuesday', startTime: '09:00', endTime: '17:00', active: true },
          { id: 3, day: 'Wednesday', startTime: '09:00', endTime: '17:00', active: true },
          { id: 4, day: 'Thursday', startTime: '09:00', endTime: '17:00', active: true },
          { id: 5, day: 'Friday', startTime: '09:00', endTime: '15:00', active: true },
          { id: 6, day: 'Saturday', startTime: '10:00', endTime: '14:00', active: false },
          { id: 7, day: 'Sunday', startTime: '10:00', endTime: '14:00', active: false }
        ]);
      } else {
        setSessions([
          {
            id: 1,
            title: 'JavaScript Fundamentals',
            mentorName: 'Dr. Sarah Martinez',
            mentorAvatar: null,
            date: new Date(2024, 11, 19, 15, 0), // December 19, 3:00 PM
            duration: 60,
            type: '1-on-1 Mentoring',
            status: 'confirmed',
            meetingLink: 'https://meet.google.com/abc-def-ghi',
            notes: 'Prepare questions about closures and async/await',
            price: 45
          },
          {
            id: 2,
            title: 'Portfolio Review',
            mentorName: 'Emma Thompson',
            mentorAvatar: null,
            date: new Date(2024, 11, 23, 11, 0), // December 23, 11:00 AM
            duration: 45,
            type: 'Portfolio Review',
            status: 'pending',
            notes: 'Bring portfolio mockups',
            price: 40
          }
        ]);
      }
      setLoading(false);
    }, 1000);
  }, [user]);

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', { 
      weekday: 'long',
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed': return '#10b981';
      case 'pending': return '#f59e0b';
      case 'cancelled': return '#ef4444';
      case 'completed': return '#6366f1';
      default: return '#6b7280';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'confirmed': return <CheckCircle size={16} />;
      case 'pending': return <AlertCircle size={16} />;
      case 'cancelled': return <XCircle size={16} />;
      case 'completed': return <CheckCircle size={16} />;
      default: return <Clock size={16} />;
    }
  };

  const filterSessions = (sessions) => {
    if (filterStatus === 'all') return sessions;
    return sessions.filter(session => session.status === filterStatus);
  };

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add all days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    return days;
  };

  const getSessionsForDate = (date) => {
    if (!date) return [];
    return sessions.filter(session => {
      const sessionDate = new Date(session.date);
      return sessionDate.toDateString() === date.toDateString();
    });
  };

  const navigateMonth = (direction) => {
    const newDate = new Date(currentDate);
    newDate.setMonth(currentDate.getMonth() + direction);
    setCurrentDate(newDate);
  };

  const joinSession = (session) => {
    if (session.meetingLink) {
      window.open(session.meetingLink, '_blank');
    } else {
      alert('Meeting link not available yet');
    }
  };

  const cancelSession = (sessionId) => {
    if (confirm('Are you sure you want to cancel this session?')) {
      setSessions(prev => prev.map(session => 
        session.id === sessionId 
          ? { ...session, status: 'cancelled' }
          : session
      ));
    }
  };

  const rescheduleSession = (sessionId) => {
    alert('Reschedule functionality would open a date/time picker');
  };

  if (loading) {
    return (
      <div className="schedule-page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading schedule...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="schedule-page">
      <div className="schedule-container">
        {/* Header */}
        <div className="page-header">
          <div className="header-content">
            <h1>
              {user?.role === 'mentor' ? 'My Schedule' : 'My Sessions'}
            </h1>
            <p>
              {user?.role === 'mentor' 
                ? 'Manage your availability and upcoming sessions'
                : 'View and manage your booked sessions'
              }
            </p>
          </div>
          
          <div className="header-actions">
            <div className="view-selector">
              <button 
                className={viewMode === 'month' ? 'active' : ''}
                onClick={() => setViewMode('month')}
              >
                Month
              </button>
              <button 
                className={viewMode === 'week' ? 'active' : ''}
                onClick={() => setViewMode('week')}
              >
                Week
              </button>
              <button 
                className={viewMode === 'list' ? 'active' : ''}
                onClick={() => setViewMode('list')}
              >
                List
              </button>
            </div>
            
            {user?.role === 'mentor' && (
              <button 
                className="add-availability-btn"
                onClick={() => setShowAddModal(true)}
              >
                <Plus size={20} />
                Set Availability
              </button>
            )}
          </div>
        </div>

        {/* Filters */}
        <div className="filters-section">
          <div className="filter-group">
            <Filter size={20} />
            <select 
              value={filterStatus} 
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">All Sessions</option>
              <option value="confirmed">Confirmed</option>
              <option value="pending">Pending</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          
          <div className="filter-actions">
            <button className="export-btn">
              <Download size={16} />
              Export
            </button>
            {user?.role === 'mentor' && (
              <button className="settings-btn">
                <Settings size={16} />
                Settings
              </button>
            )}
          </div>
        </div>

        {/* Calendar View */}
        {viewMode === 'month' && (
          <div className="calendar-section">
            <div className="calendar-header">
              <button 
                className="nav-btn"
                onClick={() => navigateMonth(-1)}
              >
                <ChevronLeft size={20} />
              </button>
              
              <h2>
                {currentDate.toLocaleDateString('en-US', { 
                  month: 'long', 
                  year: 'numeric' 
                })}
              </h2>
              
              <button 
                className="nav-btn"
                onClick={() => navigateMonth(1)}
              >
                <ChevronRight size={20} />
              </button>
            </div>

            <div className="calendar-grid">
              <div className="calendar-weekdays">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                  <div key={day} className="weekday">{day}</div>
                ))}
              </div>
              
              <div className="calendar-days">
                {getDaysInMonth(currentDate).map((date, index) => {
                  const daySessions = date ? getSessionsForDate(date) : [];
                  const isToday = date && date.toDateString() === new Date().toDateString();
                  const isSelected = date && date.toDateString() === selectedDate.toDateString();
                  
                  return (
                    <div 
                      key={index} 
                      className={`calendar-day ${!date ? 'empty' : ''} ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''}`}
                      onClick={() => date && setSelectedDate(date)}
                    >
                      {date && (
                        <>
                          <span className="day-number">{date.getDate()}</span>
                          {daySessions.length > 0 && (
                            <div className="day-sessions">
                              {daySessions.slice(0, 2).map(session => (
                                <div 
                                  key={session.id} 
                                  className="session-indicator"
                                  style={{ backgroundColor: getStatusColor(session.status) }}
                                  title={`${session.title} - ${formatTime(session.date)}`}
                                >
                                  {session.title.substring(0, 10)}...
                                </div>
                              ))}
                              {daySessions.length > 2 && (
                                <div className="more-sessions">
                                  +{daySessions.length - 2} more
                                </div>
                              )}
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Sessions List */}
        <div className="sessions-section">
          <h3>
            {viewMode === 'month' 
              ? `Sessions for ${formatDate(selectedDate)}`
              : 'Upcoming Sessions'
            }
          </h3>
          
          <div className="sessions-list">
            {filterSessions(
              viewMode === 'month' 
                ? getSessionsForDate(selectedDate)
                : sessions
            ).map(session => (
              <div key={session.id} className="session-card">
                <div className="session-header">
                  <div className="session-info">
                    <h4>{session.title}</h4>
                    <p className="session-participant">
                      with {session.mentorName || session.studentName}
                    </p>
                  </div>
                  
                  <div 
                    className="session-status"
                    style={{ color: getStatusColor(session.status) }}
                  >
                    {getStatusIcon(session.status)}
                    <span>{session.status}</span>
                  </div>
                </div>

                <div className="session-details">
                  <div className="detail-item">
                    <Calendar size={16} />
                    <span>{formatDate(session.date)}</span>
                  </div>
                  <div className="detail-item">
                    <Clock size={16} />
                    <span>{formatTime(session.date)} ({session.duration} min)</span>
                  </div>
                  <div className="detail-item">
                    <Users size={16} />
                    <span>{session.type}</span>
                  </div>
                </div>

                {session.notes && (
                  <div className="session-notes">
                    <p>{session.notes}</p>
                  </div>
                )}

                <div className="session-actions">
                  <div className="session-price">
                    ${session.price}
                  </div>
                  
                  <div className="action-buttons">
                    {session.status === 'confirmed' && session.meetingLink && (
                      <button 
                        className="join-btn"
                        onClick={() => joinSession(session)}
                      >
                        <Video size={16} />
                        Join
                      </button>
                    )}
                    
                    <button 
                      className="message-btn"
                      onClick={() => alert('Message functionality')}
                    >
                      <MessageSquare size={16} />
                      Message
                    </button>
                    
                    {session.status !== 'completed' && session.status !== 'cancelled' && (
                      <>
                        <button 
                          className="reschedule-btn"
                          onClick={() => rescheduleSession(session.id)}
                        >
                          <Edit3 size={16} />
                          Reschedule
                        </button>
                        
                        <button 
                          className="cancel-btn"
                          onClick={() => cancelSession(session.id)}
                        >
                          <Trash2 size={16} />
                          Cancel
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {filterSessions(
              viewMode === 'month' 
                ? getSessionsForDate(selectedDate)
                : sessions
            ).length === 0 && (
              <div className="no-sessions">
                <Calendar className="no-sessions-icon" />
                <h3>No sessions found</h3>
                <p>
                  {viewMode === 'month'
                    ? 'No sessions scheduled for this date'
                    : 'No sessions match your current filter'
                  }
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Mentor Availability Section */}
        {user?.role === 'mentor' && (
          <div className="availability-section">
            <h3>Weekly Availability</h3>
            <div className="availability-grid">
              {availabilitySlots.map(slot => (
                <div key={slot.id} className={`availability-slot ${slot.active ? 'active' : 'inactive'}`}>
                  <div className="slot-day">{slot.day}</div>
                  <div className="slot-time">
                    {slot.active ? `${slot.startTime} - ${slot.endTime}` : 'Not available'}
                  </div>
                  <button 
                    className="toggle-btn"
                    onClick={() => {
                      setAvailabilitySlots(prev => prev.map(s => 
                        s.id === slot.id 
                          ? { ...s, active: !s.active }
                          : s
                      ));
                    }}
                  >
                    {slot.active ? 'Disable' : 'Enable'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SchedulePage;
