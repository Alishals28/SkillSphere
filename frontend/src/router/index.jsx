import { createBrowserRouter, Navigate } from 'react-router-dom';

// Layout components
import Layout from '../components/layout/Layout';
import AuthLayout from '../components/layout/AuthLayout';

// Route protection components
import { ProtectedRoute, PublicRoute, DashboardRedirect } from '../components/common/RouteProtection';

// Auth pages
import LoginPage from '../pages/auth/LoginPage';
import RegisterPage from '../pages/auth/RegisterPage';

// Dashboard pages
import LearnerDashboard from '../pages/dashboard/LearnerDashboard';
import MentorDashboard from '../pages/dashboard/MentorDashboard';
import AdminDashboard from '../pages/dashboard/AdminDashboard';

// Mentor pages
import MentorListPage from '../pages/mentors/MentorListPage';
import MentorProfilePage from '../pages/mentors/MentorProfilePage';

// Session pages
import SessionsPage from '../pages/sessions/SessionsPage';
import SessionDetailPage from '../pages/sessions/SessionDetailPage';

// Profile pages
import ProfilePage from '../pages/profile/ProfilePage';
import EditProfilePage from '../pages/profile/EditProfilePage';

// Admin pages
import AdminMentorsPage from '../pages/admin/AdminMentorsPage';
import AdminAnalyticsPage from '../pages/admin/AdminAnalyticsPage';

// Other pages
import HomePage from '../pages/HomePage';
import NotFoundPage from '../pages/NotFoundPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: 'dashboard',
        element: (
          <ProtectedRoute>
            <DashboardRedirect />
          </ProtectedRoute>
        ),
      },
      {
        path: 'dashboard/learner',
        element: (
          <ProtectedRoute allowedRoles={['learner']}>
            <LearnerDashboard />
          </ProtectedRoute>
        ),
      },
      {
        path: 'dashboard/mentor',
        element: (
          <ProtectedRoute allowedRoles={['mentor']}>
            <MentorDashboard />
          </ProtectedRoute>
        ),
      },
      {
        path: 'dashboard/admin',
        element: (
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminDashboard />
          </ProtectedRoute>
        ),
      },
      {
        path: 'mentors',
        element: (
          <ProtectedRoute>
            <MentorListPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'mentors/:id',
        element: (
          <ProtectedRoute>
            <MentorProfilePage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'sessions',
        element: (
          <ProtectedRoute>
            <SessionsPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'sessions/:id',
        element: (
          <ProtectedRoute>
            <SessionDetailPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'profile',
        element: (
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'profile/edit',
        element: (
          <ProtectedRoute>
            <EditProfilePage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin',
        element: (
          <ProtectedRoute allowedRoles={['admin']}>
            <Navigate to="/admin/mentors" replace />
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/mentors',
        element: (
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminMentorsPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/analytics',
        element: (
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminAnalyticsPage />
          </ProtectedRoute>
        ),
      },
    ],
  },
  {
    path: '/auth',
    element: <AuthLayout />,
    children: [
      {
        path: 'login',
        element: (
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        ),
      },
      {
        path: 'register',
        element: (
          <PublicRoute>
            <RegisterPage />
          </PublicRoute>
        ),
      },
    ],
  },
  // Redirect old auth routes
  {
    path: '/login',
    element: <Navigate to="/auth/login" replace />,
  },
  {
    path: '/register',
    element: <Navigate to="/auth/register" replace />,
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
]);

export default router;
