import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import LearnerDashboard from './pages/dashboard/LearnerDashboard';
import MentorDashboard from './pages/dashboard/MentorDashboard';
import AdminDashboard from './pages/dashboard/AdminDashboard';
import UserProfile from './pages/profile/UserProfile';
import SettingsPage from './pages/settings/Settings';
import NotificationsCenter from './pages/notifications/NotificationsCenter';
import Analytics from './pages/analytics/Analytics';
import './styles/globals.css';

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            
            {/* Protected Dashboard Routes */}
            <Route 
              path="/learner/dashboard" 
              element={
                <ProtectedRoute requiredRole="learner">
                  <LearnerDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/mentor/dashboard" 
              element={
                <ProtectedRoute requiredRole="mentor">
                  <MentorDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/admin/dashboard" 
              element={
                <ProtectedRoute requiredRole="admin">
                  <AdminDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <LearnerDashboard />
                </ProtectedRoute>
              } 
            />
            
            {/* Profile Routes */}
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <UserProfile />
                </ProtectedRoute>
              } 
            />
            
            {/* Settings Routes */}
            <Route 
              path="/settings" 
              element={
                <ProtectedRoute>
                  <SettingsPage />
                </ProtectedRoute>
              } 
            />
            
            {/* Notifications Routes */}
            <Route 
              path="/notifications" 
              element={
                <ProtectedRoute>
                  <NotificationsCenter />
                </ProtectedRoute>
              } 
            />
            
            {/* Analytics Routes */}
            <Route 
              path="/analytics" 
              element={
                <ProtectedRoute>
                  <Analytics />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
