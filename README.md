# SkillSphere 🌟

> **Connecting Learners with Expert Mentors for Personalized Skill Development**

SkillSphere is a comprehensive online mentoring platform that bridges the gap between passionate learners and experienced mentors across various technology domains. Built with modern web technologies, it provides an interactive ecosystem for skill development, real-time collaboration, and AI-powered learning assistance.

![SkillSphere Banner](https://img.shields.io/badge/SkillSphere-Mentoring%20Platform-blue?style=for-the-badge&logo=react)

## 🚀 Features

### **Core Platform Features**
- 🎯 **Smart Mentor Matching** - AI-powered algorithm matching learners with ideal mentors
- 📅 **Advanced Booking System** - Individual, group, and recurring session management
- 💬 **Real-time Communication** - WebSocket-based chat with file sharing
- 🎥 **Live Video Sessions** - Integrated video conferencing with whiteboard collaboration
- 🤖 **AI Learning Assistant** - Context-aware guidance and personalized recommendations
- 📊 **Progress Analytics** - Comprehensive learning journey tracking
- 💳 **Payment Integration** - Secure payment processing with multiple options
- 👥 **Admin Management** - Complete platform oversight and moderation tools

### **Advanced Features**
- 🔄 **Recurring Sessions** - Package deals with automated scheduling
- 📱 **Responsive Design** - Optimized for desktop, tablet, and mobile
- 🌙 **Dark/Light Themes** - User preference-based UI themes
- 🔔 **Smart Notifications** - Real-time updates and reminders
- 📈 **Skill Assessment** - AI-powered skill evaluation and gap analysis
- 🏆 **Gamification** - Achievement system and progress rewards
- 🔍 **Advanced Search** - Filter mentors by skills, availability, and ratings

## 🛠️ Technology Stack

### **Backend Architecture**
```
🐍 Django 4.2+ (Python)
🗄️ PostgreSQL 14+
🔐 Django REST Framework + JWT Authentication
⚡ Django Channels + WebSocket (Real-time)
📦 Redis (Caching & Message Broker)
🤖 AI Integration (OpenAI GPT)
☁️ AWS S3 (File Storage)
```

### **Frontend Architecture**
```
⚛️ React 18+ with Hooks
🎨 CSS3 + CSS Modules
🛣️ React Router v6
⚡ Vite (Build Tool)
🔗 Axios (HTTP Client)
🎯 Context API (State Management)
📱 Progressive Web App Ready
```

### **Development & DevOps**
```
🔧 Git (Version Control)
📦 npm (Package Management)
🐳 Docker Ready
🚀 CI/CD Ready
📊 Monitoring & Analytics
```

## 📋 Prerequisites

Before running SkillSphere, ensure you have the following installed:

- **Python 3.9+** 🐍
- **Node.js 16+** ⚡
- **PostgreSQL 12+** 🗄️
- **Redis** 📦
- **Git** 🔧


## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Alishals28/skillsphere.git
cd skillsphere
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Environment setup
cp .env.example .env
# Edit .env with your configuration

# Database setup
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start Django server
python manage.py runserver
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Access Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin

## 📁 Project Structure

```
skillsphere/
├── backend/                 # Django Backend
│   ├── skillsphere/        # Main Django project
│   ├── accounts/           # User authentication & profiles
│   ├── skills/            # Skills and expertise management
│   ├── sessions/          # Session booking and management
│   ├── bookings/          # Payment and booking system
│   ├── chat/              # Real-time messaging system
│   ├── ai/                # AI assistant and recommendations
│   ├── analytics/         # Data analytics and reporting
│   ├── reviews/           # Rating and feedback system
│   ├── notifications/     # Notification system
│   └── requirements.txt   # Python dependencies
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Route-specific pages
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API service layers
│   │   ├── contexts/      # React Context providers
│   │   └── utils/         # Utility functions
│   ├── public/            # Static assets
│   └── package.json       # Node.js dependencies
└── README.md              # Project documentation
```

## 🎯 Key Components

### **Dashboard Variants**
- **Learner Dashboard** - Session booking, progress tracking, mentor discovery
- **Mentor Dashboard** - Session management, earnings, student progress
- **Admin Dashboard** - Platform analytics, user management, system monitoring

### **Session Management**
- **Individual Sessions** - One-on-one mentoring with video collaboration
- **Group Sessions** - Multi-participant learning sessions
- **Recurring Packages** - Automated booking for ongoing mentorship

### **AI Integration**
- **Learning Assistant** - Context-aware guidance and recommendations
- **Mentor Matching** - AI-powered mentor suggestions based on goals
- **Progress Analysis** - Intelligent skill gap identification
- **Study Path Generation** - Personalized learning roadmaps

### **Communication System**
- **Real-time Chat** - WebSocket-based messaging with file sharing
- **Video Conferencing** - Integrated video sessions with screen sharing
- **Notification System** - Smart alerts and reminders

## 🔧 Configuration

### Environment Variables

Create `.env` files in both backend and frontend directories:

**Backend (.env)**
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/skillsphere
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your-openai-key
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
STRIPE_SECRET_KEY=your-stripe-key
EMAIL_HOST_PASSWORD=your-email-password
```

**Frontend (.env)**
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_STRIPE_PUBLIC_KEY=your-stripe-public-key
```

## 📚 API Documentation

### **Core Endpoints**

```
Authentication:
POST /api/auth/login/          # User login
POST /api/auth/register/       # User registration
POST /api/auth/refresh/        # Token refresh

Users:
GET  /api/users/profile/       # Get user profile
PUT  /api/users/profile/       # Update profile
GET  /api/users/mentors/       # List mentors

Sessions:
GET  /api/sessions/            # List sessions
POST /api/sessions/            # Create session
GET  /api/sessions/{id}/       # Session details
PUT  /api/sessions/{id}/       # Update session

Bookings:
POST /api/bookings/            # Create booking
GET  /api/bookings/            # List user bookings
PUT  /api/bookings/{id}/       # Update booking

Chat:
GET  /api/chat/conversations/  # List conversations
POST /api/chat/messages/       # Send message
WS   /ws/chat/{conv_id}/       # WebSocket connection

AI Assistant:
POST /api/ai/chat/             # AI conversation
GET  /api/ai/recommendations/  # Get recommendations
POST /api/ai/learning-path/    # Generate learning path
```

## 🧪 Testing

### **Backend Testing**
```bash
cd backend
python manage.py test
```

### **Frontend Testing**
```bash
cd frontend
npm test
```

## 🚀 Deployment

### **Docker Deployment**
```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate
```

### **Production Considerations**
- Set `DEBUG=False` in production
- Configure proper CORS settings
- Set up SSL certificates
- Configure production database
- Set up Redis for production
- Configure file storage (AWS S3)
- Set up monitoring and logging

## 🤝 Contributing

We welcome contributions to SkillSphere! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LoopVerse Web Development Challenge** - Original project inspiration
- **Django & React Communities** - Excellent documentation and support
- **OpenAI** - AI integration capabilities
- **Contributors** - All developers who helped build SkillSphere



**Built with ❤️ by the SkillSphere Team**

[⭐ Star this repo](https://github.com/Alishals28/skillsphere) | [🐛 Report Bug](https://github.com/Alishals28/skillsphere/issues) | [💡 Request Feature](https://github.com/Alishals28/skillsphere/issues)

</div>
