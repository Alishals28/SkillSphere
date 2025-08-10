import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import './StatsCard.css';

const StatsCard = ({ 
  title, 
  value, 
  change, 
  changeType, 
  icon: Icon, 
  color = 'blue',
  subtitle 
}) => {
  return (
    <div className={`stats-card ${color}`}>
      <div className="stats-header">
        <div className="stats-info">
          <h3 className="stats-title">{title}</h3>
          {subtitle && <p className="stats-subtitle">{subtitle}</p>}
        </div>
        <div className="stats-icon">
          <Icon size={24} />
        </div>
      </div>
      
      <div className="stats-value">
        {value}
      </div>
      
      {change && (
        <div className={`stats-change ${changeType}`}>
          {changeType === 'positive' ? (
            <TrendingUp size={16} />
          ) : (
            <TrendingDown size={16} />
          )}
          <span>{change}</span>
          <span className="change-period">vs last month</span>
        </div>
      )}
    </div>
  );
};

export default StatsCard;
