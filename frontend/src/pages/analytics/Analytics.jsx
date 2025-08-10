import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  TrendingUp, 
  Calendar, 
  Clock, 
  Star, 
  Users, 
  Award,
  Target,
  BookOpen,
  ChevronDown,
  Download,
  Filter,
  BarChart3,
  PieChart,
  LineChart
} from 'lucide-react';
import './Analytics.css';

const Analytics = () => {
  const { user } = useAuth();
  const [timeRange, setTimeRange] = useState('30d');
  const [activeChart, setActiveChart] = useState('overview');
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Mock analytics data - replace with API call
  useEffect(() => {
    const mockData = {
      overview: {
        totalSessions: user?.role === 'mentor' ? 127 : 45,
        totalHours: user?.role === 'mentor' ? 254 : 89,
        averageRating: user?.role === 'mentor' ? 4.8 : null,
        totalEarnings: user?.role === 'mentor' ? 3850 : null,
        progressScore: user?.role === 'learner' ? 78 : null,
        skillsLearned: user?.role === 'learner' ? 12 : null
      },
      performance: {
        sessionsThisMonth: user?.role === 'mentor' ? 23 : 8,
        growthRate: user?.role === 'mentor' ? 15 : 25,
        completionRate: 92,
        satisfactionScore: user?.role === 'mentor' ? 4.7 : 4.6
      },
      trends: {
        dailyStats: [
          { date: '2024-01-01', sessions: 3, hours: 6, rating: 4.8 },
          { date: '2024-01-02', sessions: 5, hours: 10, rating: 4.9 },
          { date: '2024-01-03', sessions: 2, hours: 4, rating: 4.7 },
          { date: '2024-01-04', sessions: 4, hours: 8, rating: 4.8 },
          { date: '2024-01-05', sessions: 6, hours: 12, rating: 4.9 },
          { date: '2024-01-06', sessions: 3, hours: 6, rating: 4.8 },
          { date: '2024-01-07', sessions: 4, hours: 8, rating: 4.8 }
        ],
        skillDistribution: user?.role === 'mentor' ? [
          { skill: 'React.js', count: 45, percentage: 35 },
          { skill: 'Python', count: 38, percentage: 30 },
          { skill: 'Node.js', count: 25, percentage: 20 },
          { skill: 'Data Science', count: 19, percentage: 15 }
        ] : [
          { skill: 'JavaScript', count: 15, percentage: 33 },
          { skill: 'Python', count: 12, percentage: 27 },
          { skill: 'React', count: 10, percentage: 22 },
          { skill: 'CSS', count: 8, percentage: 18 }
        ]
      }
    };

    setTimeout(() => {
      setAnalyticsData(mockData);
      setLoading(false);
    }, 800);
  }, [user?.role, timeRange]);

  const StatCard = ({ icon: Icon, title, value, subtitle, trend, color = 'primary' }) => (
    <div className={`stat-card ${color}`}>
      <div className="stat-icon">
        <Icon size={24} />
      </div>
      <div className="stat-content">
        <h3 className="stat-title">{title}</h3>
        <p className="stat-value">{value}</p>
        {subtitle && <span className="stat-subtitle">{subtitle}</span>}
        {trend && (
          <div className={`stat-trend ${trend > 0 ? 'positive' : 'negative'}`}>
            <TrendingUp size={16} />
            {trend > 0 ? '+' : ''}{trend}% vs last month
          </div>
        )}
      </div>
    </div>
  );

  const ProgressBar = ({ label, value, maxValue, color = 'primary' }) => (
    <div className="progress-item">
      <div className="progress-header">
        <span className="progress-label">{label}</span>
        <span className="progress-value">{value}/{maxValue}</span>
      </div>
      <div className="progress-bar">
        <div 
          className={`progress-fill ${color}`}
          style={{ width: `${(value / maxValue) * 100}%` }}
        />
      </div>
    </div>
  );

  const ChartToggle = ({ type, label, icon: Icon, isActive, onClick }) => (
    <button 
      className={`chart-toggle ${isActive ? 'active' : ''}`}
      onClick={() => onClick(type)}
    >
      <Icon size={18} />
      {label}
    </button>
  );

  if (loading) {
    return (
      <div className="analytics-page">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-page">
      <div className="analytics-header">
        <div className="header-content">
          <h1>Analytics Dashboard</h1>
          <p>Track your {user?.role === 'mentor' ? 'mentoring' : 'learning'} progress and performance</p>
        </div>
        
        <div className="header-controls">
          <div className="time-selector">
            <select 
              value={timeRange} 
              onChange={(e) => setTimeRange(e.target.value)}
              className="time-dropdown"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
            </select>
            <ChevronDown className="dropdown-icon" />
          </div>
          
          <button className="export-btn">
            <Download size={18} />
            Export Report
          </button>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="stats-grid">
        <StatCard
          icon={Calendar}
          title="Total Sessions"
          value={analyticsData.overview.totalSessions}
          subtitle="completed"
          trend={analyticsData.performance.growthRate}
          color="primary"
        />
        
        <StatCard
          icon={Clock}
          title="Total Hours"
          value={analyticsData.overview.totalHours}
          subtitle="spent"
          trend={12}
          color="secondary"
        />
        
        {user?.role === 'mentor' ? (
          <>
            <StatCard
              icon={Star}
              title="Average Rating"
              value={analyticsData.overview.averageRating}
              subtitle="out of 5.0"
              trend={3}
              color="success"
            />
            
            <StatCard
              icon={Award}
              title="Total Earnings"
              value={`$${analyticsData.overview.totalEarnings}`}
              subtitle="this month"
              trend={18}
              color="warning"
            />
          </>
        ) : (
          <>
            <StatCard
              icon={Target}
              title="Progress Score"
              value={`${analyticsData.overview.progressScore}%`}
              subtitle="overall progress"
              trend={8}
              color="success"
            />
            
            <StatCard
              icon={BookOpen}
              title="Skills Learned"
              value={analyticsData.overview.skillsLearned}
              subtitle="new skills"
              trend={20}
              color="warning"
            />
          </>
        )}
      </div>

      {/* Performance Metrics */}
      <div className="analytics-section">
        <div className="section-header">
          <h2>Performance Metrics</h2>
          <div className="chart-toggles">
            <ChartToggle
              type="overview"
              label="Overview"
              icon={BarChart3}
              isActive={activeChart === 'overview'}
              onClick={setActiveChart}
            />
            <ChartToggle
              type="trends"
              label="Trends"
              icon={LineChart}
              isActive={activeChart === 'trends'}
              onClick={setActiveChart}
            />
            <ChartToggle
              type="distribution"
              label="Distribution"
              icon={PieChart}
              isActive={activeChart === 'distribution'}
              onClick={setActiveChart}
            />
          </div>
        </div>

        <div className="chart-container">
          {activeChart === 'overview' && (
            <div className="overview-chart">
              <div className="metric-cards">
                <div className="metric-card">
                  <h4>Sessions This Month</h4>
                  <p className="metric-value">{analyticsData.performance.sessionsThisMonth}</p>
                  <ProgressBar 
                    label="Monthly Goal" 
                    value={analyticsData.performance.sessionsThisMonth} 
                    maxValue={30}
                    color="primary"
                  />
                </div>
                
                <div className="metric-card">
                  <h4>Completion Rate</h4>
                  <p className="metric-value">{analyticsData.performance.completionRate}%</p>
                  <ProgressBar 
                    label="Target" 
                    value={analyticsData.performance.completionRate} 
                    maxValue={100}
                    color="success"
                  />
                </div>
                
                <div className="metric-card">
                  <h4>Satisfaction Score</h4>
                  <p className="metric-value">{analyticsData.performance.satisfactionScore}/5.0</p>
                  <ProgressBar 
                    label="Rating" 
                    value={analyticsData.performance.satisfactionScore} 
                    maxValue={5}
                    color="warning"
                  />
                </div>
              </div>
            </div>
          )}

          {activeChart === 'trends' && (
            <div className="trends-chart">
              <h4>Daily Activity (Last 7 Days)</h4>
              <div className="trend-bars">
                {analyticsData.trends.dailyStats.map((day, index) => (
                  <div key={index} className="trend-bar">
                    <div className="bar-container">
                      <div 
                        className="bar sessions"
                        style={{ height: `${(day.sessions / 6) * 100}%` }}
                        title={`${day.sessions} sessions`}
                      />
                    </div>
                    <span className="bar-label">
                      {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}
                    </span>
                  </div>
                ))}
              </div>
              <div className="chart-legend">
                <div className="legend-item">
                  <div className="legend-color sessions"></div>
                  <span>Sessions per day</span>
                </div>
              </div>
            </div>
          )}

          {activeChart === 'distribution' && (
            <div className="distribution-chart">
              <h4>{user?.role === 'mentor' ? 'Teaching Areas' : 'Learning Areas'}</h4>
              <div className="skill-distribution">
                {analyticsData.trends.skillDistribution.map((skill, index) => (
                  <div key={index} className="skill-item">
                    <div className="skill-info">
                      <span className="skill-name">{skill.skill}</span>
                      <span className="skill-count">{skill.count} sessions</span>
                    </div>
                    <div className="skill-bar">
                      <div 
                        className="skill-fill"
                        style={{ 
                          width: `${skill.percentage}%`,
                          backgroundColor: `hsl(${220 + index * 30}, 70%, 60%)`
                        }}
                      />
                    </div>
                    <span className="skill-percentage">{skill.percentage}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Goals & Achievements */}
      <div className="analytics-section">
        <div className="section-header">
          <h2>Goals & Achievements</h2>
        </div>
        
        <div className="goals-grid">
          <div className="goal-card">
            <div className="goal-header">
              <Target className="goal-icon" />
              <h4>Monthly Target</h4>
            </div>
            <ProgressBar 
              label={user?.role === 'mentor' ? 'Sessions taught' : 'Sessions attended'} 
              value={analyticsData.performance.sessionsThisMonth} 
              maxValue={30}
              color="primary"
            />
            <p className="goal-description">
              {30 - analyticsData.performance.sessionsThisMonth} more sessions to reach your monthly goal
            </p>
          </div>
          
          <div className="goal-card">
            <div className="goal-header">
              <Award className="goal-icon" />
              <h4>Quality Score</h4>
            </div>
            <ProgressBar 
              label="Rating average" 
              value={analyticsData.performance.satisfactionScore} 
              maxValue={5}
              color="success"
            />
            <p className="goal-description">
              Maintain above 4.5 to earn quality bonus
            </p>
          </div>
          
          <div className="goal-card">
            <div className="goal-header">
              <Users className="goal-icon" />
              <h4>Growth Rate</h4>
            </div>
            <ProgressBar 
              label="Monthly growth" 
              value={analyticsData.performance.growthRate} 
              maxValue={25}
              color="warning"
            />
            <p className="goal-description">
              {analyticsData.performance.growthRate}% growth this month - great progress!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
