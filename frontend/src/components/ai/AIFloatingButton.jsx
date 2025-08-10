import React, { useState } from 'react';
import { Bot, Sparkles } from 'lucide-react';
import './AIFloatingButton.css';

const AIFloatingButton = ({ onClick, hasNotification = false }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className="ai-floating-container">
      {/* Tooltip */}
      {isHovered && (
        <div className="ai-tooltip">
          <span>Ask AI Assistant</span>
          <div className="tooltip-arrow"></div>
        </div>
      )}
      
      {/* Main Button */}
      <button
        onClick={onClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className="ai-floating-button"
        aria-label="Open AI Assistant"
      >
        {/* Background Effects */}
        <div className="ai-button-bg"></div>
        <div className="ai-button-ring"></div>
        
        {/* Icon */}
        <div className="ai-button-icon">
          <Bot size={24} />
        </div>
        
        {/* Sparkle Effect */}
        <div className="ai-sparkles">
          <Sparkles className="sparkle sparkle-1" size={12} />
          <Sparkles className="sparkle sparkle-2" size={10} />
          <Sparkles className="sparkle sparkle-3" size={8} />
        </div>
        
        {/* Notification Badge */}
        {hasNotification && (
          <div className="ai-notification-badge">
            <div className="notification-dot"></div>
          </div>
        )}
      </button>
    </div>
  );
};

export default AIFloatingButton;
