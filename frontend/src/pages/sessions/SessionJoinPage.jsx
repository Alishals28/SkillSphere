import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Video, 
  VideoOff, 
  Mic, 
  MicOff, 
  Phone, 
  PhoneOff, 
  Monitor, 
  Users, 
  MessageSquare, 
  Settings,
  Camera,
  Volume2,
  VolumeX,
  Maximize,
  FileText,
  Download,
  Upload
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import './SessionJoinPage.css';

const SessionJoinPage = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  // Video/Audio refs
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const whiteboardRef = useRef(null);
  
  // Session state
  const [session, setSession] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  
  // Media controls
  const [isVideoOn, setIsVideoOn] = useState(true);
  const [isAudioOn, setIsAudioOn] = useState(true);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [isSpeakerOn, setIsSpeakerOn] = useState(true);
  
  // UI state
  const [showChat, setShowChat] = useState(false);
  const [showWhiteboard, setShowWhiteboard] = useState(false);
  const [showParticipants, setShowParticipants] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  // Chat
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  
  // Mock session data
  useEffect(() => {
    // Simulate loading session data
    const mockSession = {
      id: sessionId,
      title: 'React Hooks Deep Dive',
      mentor: {
        id: 2,
        name: 'Dr. Sarah Martinez',
        avatar: null,
        expertise: 'React Development'
      },
      student: {
        id: 1,
        name: 'John Doe',
        avatar: null
      },
      scheduledTime: '2024-01-10T14:00:00Z',
      duration: 60,
      status: 'in-progress',
      description: 'Comprehensive session on React Hooks including useState, useEffect, and custom hooks'
    };
    
    setSession(mockSession);
    
    // Simulate connection process
    setTimeout(() => {
      setConnectionStatus('connected');
      setIsConnected(true);
    }, 2000);
  }, [sessionId]);

  // Initialize media stream
  useEffect(() => {
    if (isConnected) {
      initializeMedia();
    }
    
    return () => {
      // Cleanup media streams
      if (localVideoRef.current && localVideoRef.current.srcObject) {
        const tracks = localVideoRef.current.srcObject.getTracks();
        tracks.forEach(track => track.stop());
      }
    };
  }, [isConnected]);

  const initializeMedia = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      });
      
      if (localVideoRef.current) {
        localVideoRef.current.srcObject = stream;
      }
    } catch (error) {
      console.error('Error accessing media devices:', error);
    }
  };

  const toggleVideo = () => {
    setIsVideoOn(!isVideoOn);
    if (localVideoRef.current && localVideoRef.current.srcObject) {
      const tracks = localVideoRef.current.srcObject.getVideoTracks();
      tracks.forEach(track => {
        track.enabled = !isVideoOn;
      });
    }
  };

  const toggleAudio = () => {
    setIsAudioOn(!isAudioOn);
    if (localVideoRef.current && localVideoRef.current.srcObject) {
      const tracks = localVideoRef.current.srcObject.getAudioTracks();
      tracks.forEach(track => {
        track.enabled = !isAudioOn;
      });
    }
  };

  const toggleScreenShare = async () => {
    try {
      if (!isScreenSharing) {
        const stream = await navigator.mediaDevices.getDisplayMedia({
          video: true,
          audio: true
        });
        
        if (localVideoRef.current) {
          localVideoRef.current.srcObject = stream;
        }
        setIsScreenSharing(true);
      } else {
        // Switch back to camera
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true
        });
        
        if (localVideoRef.current) {
          localVideoRef.current.srcObject = stream;
        }
        setIsScreenSharing(false);
      }
    } catch (error) {
      console.error('Error with screen sharing:', error);
    }
  };

  const endSession = () => {
    // Cleanup and navigate back
    if (localVideoRef.current && localVideoRef.current.srcObject) {
      const tracks = localVideoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
    }
    navigate('/sessions');
  };

  const sendChatMessage = () => {
    if (chatInput.trim()) {
      const newMessage = {
        id: Date.now(),
        sender: user.name,
        message: chatInput,
        timestamp: new Date().toISOString()
      };
      setChatMessages([...chatMessages, newMessage]);
      setChatInput('');
    }
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  if (!session) {
    return (
      <div className="session-loading">
        <div className="loading-content">
          <div className="spinner"></div>
          <h3>Loading session...</h3>
          <p>Please wait while we prepare your session</p>
        </div>
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="session-connecting">
        <div className="connecting-content">
          <div className="connection-spinner"></div>
          <h3>Connecting to session...</h3>
          <p>Status: {connectionStatus}</p>
          <div className="connection-steps">
            <div className="step completed">✓ Joining session</div>
            <div className="step completed">✓ Setting up media</div>
            <div className="step active">⏳ Connecting to peer</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`session-join-page ${isFullscreen ? 'fullscreen' : ''}`}>
      {/* Session Header */}
      <div className="session-header">
        <div className="session-info">
          <h2>{session.title}</h2>
          <p>with {session.mentor.name}</p>
        </div>
        
        <div className="session-actions">
          <button 
            className="action-btn"
            onClick={() => setShowParticipants(!showParticipants)}
            title="Participants"
          >
            <Users size={20} />
          </button>
          
          <button 
            className="action-btn"
            onClick={() => setShowChat(!showChat)}
            title="Chat"
          >
            <MessageSquare size={20} />
            {chatMessages.length > 0 && (
              <span className="notification-badge">{chatMessages.length}</span>
            )}
          </button>
          
          <button 
            className="action-btn"
            onClick={() => setShowWhiteboard(!showWhiteboard)}
            title="Whiteboard"
          >
            <FileText size={20} />
          </button>
          
          <button 
            className="action-btn"
            onClick={toggleFullscreen}
            title="Fullscreen"
          >
            <Maximize size={20} />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="session-content">
        {/* Video Area */}
        <div className="video-area">
          {/* Remote Video (Mentor/Peer) */}
          <div className="remote-video-container">
            <video 
              ref={remoteVideoRef}
              className="remote-video"
              autoPlay
              playsInline
            />
            <div className="video-overlay">
              <div className="participant-info">
                <div className="participant-avatar">
                  {session.mentor.avatar ? (
                    <img src={session.mentor.avatar} alt={session.mentor.name} />
                  ) : (
                    <div className="avatar-placeholder">
                      {session.mentor.name.charAt(0)}
                    </div>
                  )}
                </div>
                <div className="participant-details">
                  <h4>{session.mentor.name}</h4>
                  <p>{session.mentor.expertise}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Local Video (Self) */}
          <div className="local-video-container">
            <video 
              ref={localVideoRef}
              className="local-video"
              autoPlay
              playsInline
              muted
            />
            <div className="video-controls-overlay">
              <span className="video-label">You</span>
            </div>
          </div>
        </div>

        {/* Whiteboard */}
        {showWhiteboard && (
          <div className="whiteboard-container">
            <div className="whiteboard-header">
              <h3>Shared Whiteboard</h3>
              <div className="whiteboard-tools">
                <button className="tool-btn active">Pen</button>
                <button className="tool-btn">Eraser</button>
                <button className="tool-btn">Text</button>
                <button className="tool-btn">Clear</button>
              </div>
            </div>
            <canvas 
              ref={whiteboardRef}
              className="whiteboard"
              width="800" 
              height="600"
            />
          </div>
        )}

        {/* Chat Panel */}
        {showChat && (
          <div className="chat-panel">
            <div className="chat-header">
              <h3>Session Chat</h3>
              <button 
                className="close-btn"
                onClick={() => setShowChat(false)}
              >
                ×
              </button>
            </div>
            
            <div className="chat-messages">
              {chatMessages.map(msg => (
                <div key={msg.id} className="chat-message">
                  <div className="message-sender">{msg.sender}</div>
                  <div className="message-content">{msg.message}</div>
                  <div className="message-time">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="chat-input-area">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                placeholder="Type a message..."
                className="chat-input"
              />
              <button 
                onClick={sendChatMessage}
                className="send-btn"
                disabled={!chatInput.trim()}
              >
                Send
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Control Bar */}
      <div className="control-bar">
        <div className="media-controls">
          <button 
            className={`control-btn ${isVideoOn ? 'active' : 'inactive'}`}
            onClick={toggleVideo}
            title={isVideoOn ? 'Turn off camera' : 'Turn on camera'}
          >
            {isVideoOn ? <Video size={24} /> : <VideoOff size={24} />}
          </button>
          
          <button 
            className={`control-btn ${isAudioOn ? 'active' : 'inactive'}`}
            onClick={toggleAudio}
            title={isAudioOn ? 'Mute microphone' : 'Unmute microphone'}
          >
            {isAudioOn ? <Mic size={24} /> : <MicOff size={24} />}
          </button>
          
          <button 
            className={`control-btn ${isSpeakerOn ? 'active' : 'inactive'}`}
            onClick={() => setIsSpeakerOn(!isSpeakerOn)}
            title={isSpeakerOn ? 'Mute speaker' : 'Unmute speaker'}
          >
            {isSpeakerOn ? <Volume2 size={24} /> : <VolumeX size={24} />}
          </button>
          
          <button 
            className={`control-btn ${isScreenSharing ? 'sharing' : ''}`}
            onClick={toggleScreenShare}
            title={isScreenSharing ? 'Stop sharing' : 'Share screen'}
          >
            <Monitor size={24} />
          </button>
        </div>

        <div className="session-controls">
          <div className="session-timer">
            <span>45:23</span>
          </div>
          
          <button 
            className="end-call-btn"
            onClick={endSession}
            title="End session"
          >
            <PhoneOff size={24} />
            End Session
          </button>
        </div>

        <div className="additional-controls">
          <button className="control-btn" title="Settings">
            <Settings size={24} />
          </button>
          
          <button className="control-btn" title="Upload file">
            <Upload size={24} />
          </button>
          
          <button className="control-btn" title="Download resources">
            <Download size={24} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default SessionJoinPage;
