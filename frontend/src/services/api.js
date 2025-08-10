import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
const tokenManager = {
  getAccessToken: () => localStorage.getItem('accessToken'),
  getRefreshToken: () => localStorage.getItem('refreshToken'),
  setTokens: (accessToken, refreshToken) => {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
  },
  clearTokens: () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  },
};

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = tokenManager.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = tokenManager.getRefreshToken();
        if (refreshToken) {
          const response = await axios.post(`${BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          tokenManager.setTokens(access, refreshToken);
          
          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        tokenManager.clearTokens();
        // Redirect to login page
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

// API response wrapper
const apiCall = async (method, url, data = null, config = {}) => {
  try {
    const response = await api({
      method,
      url,
      data,
      ...config,
    });
    return {
      success: true,
      data: response.data,
      status: response.status,
    };
  } catch (error) {
    console.error('API Call Error:', error);
    return {
      success: false,
      error: error.response?.data || error.message,
      status: error.response?.status,
    };
  }
};

// Specific API methods
export const authAPI = {
  login: (email, password) => apiCall('POST', '/auth/login/', { email, password }),
  register: (userData) => apiCall('POST', '/auth/register/', userData),
  logout: (refreshToken) => apiCall('POST', '/auth/logout/', { refresh: refreshToken }),
  refreshToken: (refreshToken) => apiCall('POST', '/auth/token/refresh/', { refresh: refreshToken }),
  getCurrentUser: () => apiCall('GET', '/auth/user/'),
  updateProfile: (userData) => apiCall('PATCH', '/auth/user/', userData),
  changePassword: (passwordData) => apiCall('POST', '/auth/change-password/', passwordData),
  
  // 2FA endpoints
  setup2FA: (password) => apiCall('POST', '/auth/2fa/setup/', { password }),
  enable2FA: (code) => apiCall('POST', '/auth/2fa/enable/', { code }),
  disable2FA: (password) => apiCall('POST', '/auth/2fa/disable/', { password }),
  verify2FA: (code) => apiCall('POST', '/auth/2fa/verify/', { code }),
  get2FAStatus: () => apiCall('GET', '/auth/2fa/status/'),
};

export const mentorsAPI = {
  getMentors: (params) => apiCall('GET', '/mentors/', { params }),
  getMentor: (id) => apiCall('GET', `/mentors/${id}/`),
  updateMentorProfile: (data) => apiCall('PATCH', '/mentors/profile/', data),
  getMentorAvailability: (mentorId) => apiCall('GET', `/mentors/${mentorId}/availability/`),
  updateAvailability: (data) => apiCall('POST', '/mentors/availability/', data),
  getMentorAnalytics: () => apiCall('GET', '/mentors/analytics/'),
};

export const bookingsAPI = {
  createBooking: (data) => apiCall('POST', '/bookings/', data),
  getBookings: (params) => apiCall('GET', '/bookings/', { params }),
  getBooking: (id) => apiCall('GET', `/bookings/${id}/`),
  updateBooking: (id, data) => apiCall('PATCH', `/bookings/${id}/`, data),
  cancelBooking: (id) => apiCall('POST', `/bookings/${id}/cancel/`),
  rescheduleBooking: (id, data) => apiCall('POST', `/bookings/${id}/reschedule/`, data),
};

export const searchAPI = {
  searchMentors: (query, filters) => apiCall('GET', '/search/mentors/', { 
    params: { q: query, ...filters } 
  }),
  searchSkills: (query) => apiCall('GET', '/search/skills/', { params: { q: query } }),
  getPopularSearches: () => apiCall('GET', '/search/popular/'),
  getSuggestions: (query) => apiCall('GET', '/search/suggestions/', { params: { q: query } }),
};

export const chatAPI = {
  getConversations: () => apiCall('GET', '/chat/conversations/'),
  getConversation: (id) => apiCall('GET', `/chat/conversations/${id}/`),
  sendMessage: (conversationId, message) => apiCall('POST', `/chat/conversations/${conversationId}/messages/`, message),
  markAsRead: (conversationId) => apiCall('POST', `/chat/conversations/${conversationId}/mark-read/`),
};

export const notificationsAPI = {
  getNotifications: (params) => apiCall('GET', '/notifications/', { params }),
  markAsRead: (id) => apiCall('PATCH', `/notifications/${id}/`, { read: true }),
  markAllAsRead: () => apiCall('POST', '/notifications/mark-all-read/'),
  getUnreadCount: () => apiCall('GET', '/notifications/unread-count/'),
};

export const reviewsAPI = {
  createReview: (data) => apiCall('POST', '/reviews/', data),
  getReviews: (params) => apiCall('GET', '/reviews/', { params }),
  updateReview: (id, data) => apiCall('PATCH', `/reviews/${id}/`, data),
  deleteReview: (id) => apiCall('DELETE', `/reviews/${id}/`),
};

export const skillsAPI = {
  getSkills: () => apiCall('GET', '/skills/'),
  getSkillCategories: () => apiCall('GET', '/skills/categories/'),
  getSkillDetails: (id) => apiCall('GET', `/skills/${id}/`),
};

export const analyticsAPI = {
  getDashboardStats: () => apiCall('GET', '/analytics/dashboard/'),
  getLearningProgress: () => apiCall('GET', '/analytics/learning-progress/'),
  getMentorStats: () => apiCall('GET', '/analytics/mentor-stats/'),
  getBookingTrends: (period) => apiCall('GET', '/analytics/booking-trends/', { params: { period } }),
};

export const adminAPI = {
  getPendingMentors: () => apiCall('GET', '/admin/mentors/pending/'),
  approveMentor: (id) => apiCall('POST', `/admin/mentors/${id}/approve/`),
  rejectMentor: (id, reason) => apiCall('POST', `/admin/mentors/${id}/reject/`, { reason }),
  getPlatformStats: () => apiCall('GET', '/admin/stats/'),
  getReportedContent: () => apiCall('GET', '/admin/reported-content/'),
  moderateContent: (id, action) => apiCall('POST', `/admin/moderate/${id}/`, { action }),
};

export const gamificationAPI = {
  getUserBadges: () => apiCall('GET', '/gamification/my-badges/'),
  getAllBadges: () => apiCall('GET', '/gamification/badges/'),
  checkBadges: () => apiCall('POST', '/gamification/check-badges/'),
};

export const aiAPI = {
  getRecommendations: (type, params) => apiCall('GET', `/ai/recommendations/${type}/`, { params }),
  getMentorSuggestions: () => apiCall('GET', '/ai/mentor-suggestions/'),
  getSkillAssessment: (skillId) => apiCall('GET', `/ai/skill-assessment/${skillId}/`),
  generateLearningPath: (goals) => apiCall('POST', '/ai/learning-path/', { goals }),
};

export { api, apiCall, tokenManager };
export default api;
