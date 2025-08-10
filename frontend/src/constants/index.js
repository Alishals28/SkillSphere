// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login/',
    REGISTER: '/auth/register/',
    LOGOUT: '/auth/logout/',
    REFRESH: '/auth/token/refresh/',
    USER: '/auth/user/',
    CHANGE_PASSWORD: '/auth/change-password/',
  },
  MENTORS: '/mentors/',
  BOOKINGS: '/bookings/',
  SEARCH: '/search/',
  CHAT: '/chat/',
  NOTIFICATIONS: '/notifications/',
  REVIEWS: '/reviews/',
  SKILLS: '/skills/',
  ANALYTICS: '/analytics/',
  ADMIN: '/admin/',
  GAMIFICATION: '/gamification/',
  AI: '/ai/',
};

// User Roles
export const USER_ROLES = {
  LEARNER: 'learner',
  MENTOR: 'mentor',
  ADMIN: 'admin',
};

// Booking Status
export const BOOKING_STATUS = {
  PENDING: 'pending',
  CONFIRMED: 'confirmed',
  CANCELLED: 'cancelled',
  COMPLETED: 'completed',
  NO_SHOW: 'no_show',
};

// Session Status
export const SESSION_STATUS = {
  SCHEDULED: 'scheduled',
  LIVE: 'live',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled',
};

// Notification Types
export const NOTIFICATION_TYPES = {
  BOOKING_REQUEST: 'booking_request',
  BOOKING_CONFIRMED: 'booking_confirmed',
  BOOKING_CANCELLED: 'booking_cancelled',
  SESSION_REMINDER: 'session_reminder',
  REVIEW_RECEIVED: 'review_received',
  MESSAGE_RECEIVED: 'message_received',
  MENTOR_APPROVED: 'mentor_approved',
  BADGE_EARNED: 'badge_earned',
};

// Badge Categories
export const BADGE_CATEGORIES = {
  LEARNING: 'learning',
  TEACHING: 'teaching',
  MILESTONES: 'milestones',
  QUALITY: 'quality',
  SPECIAL: 'special',
};

// Search Filters
export const SEARCH_FILTERS = {
  SKILLS: 'skills',
  RATING: 'rating',
  PRICE_RANGE: 'price_range',
  AVAILABILITY: 'availability',
  EXPERIENCE_LEVEL: 'experience_level',
  LANGUAGES: 'languages',
};

// Experience Levels
export const EXPERIENCE_LEVELS = {
  BEGINNER: 'beginner',
  INTERMEDIATE: 'intermediate',
  ADVANCED: 'advanced',
  EXPERT: 'expert',
};

// Session Duration Options (in minutes)
export const SESSION_DURATIONS = {
  30: '30 minutes',
  45: '45 minutes',
  60: '1 hour',
  90: '1.5 hours',
  120: '2 hours',
};

// Time Zones (common ones)
export const COMMON_TIMEZONES = [
  { value: 'UTC', label: 'UTC' },
  { value: 'America/New_York', label: 'Eastern Time (ET)' },
  { value: 'America/Chicago', label: 'Central Time (CT)' },
  { value: 'America/Denver', label: 'Mountain Time (MT)' },
  { value: 'America/Los_Angeles', label: 'Pacific Time (PT)' },
  { value: 'Europe/London', label: 'Greenwich Mean Time (GMT)' },
  { value: 'Europe/Berlin', label: 'Central European Time (CET)' },
  { value: 'Asia/Tokyo', label: 'Japan Standard Time (JST)' },
  { value: 'Asia/Shanghai', label: 'China Standard Time (CST)' },
  { value: 'Asia/Kolkata', label: 'India Standard Time (IST)' },
];

// Price Ranges for Filtering
export const PRICE_RANGES = [
  { min: 0, max: 25, label: '$0 - $25' },
  { min: 25, max: 50, label: '$25 - $50' },
  { min: 50, max: 100, label: '$50 - $100' },
  { min: 100, max: 200, label: '$100 - $200' },
  { min: 200, max: null, label: '$200+' },
];

// Languages
export const LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' },
  { code: 'it', name: 'Italian' },
  { code: 'pt', name: 'Portuguese' },
  { code: 'ru', name: 'Russian' },
  { code: 'zh', name: 'Chinese' },
  { code: 'ja', name: 'Japanese' },
  { code: 'ko', name: 'Korean' },
  { code: 'ar', name: 'Arabic' },
  { code: 'hi', name: 'Hindi' },
];

// File Upload Limits
export const FILE_UPLOAD = {
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_TYPES: {
    IMAGES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    DOCUMENTS: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
    ALL: ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
  },
};

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 12,
  MAX_PAGE_SIZE: 100,
};

// Theme
export const THEMES = {
  LIGHT: 'light',
  DARK: 'dark',
};

// Local Storage Keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'accessToken',
  REFRESH_TOKEN: 'refreshToken',
  USER: 'user',
  THEME: 'theme',
  SEARCH_HISTORY: 'searchHistory',
  PREFERENCES: 'preferences',
};

// Form Validation
export const VALIDATION = {
  EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE_REGEX: /^\+?[\d\s\-\(\)]+$/,
  PASSWORD_MIN_LENGTH: 8,
  USERNAME_MIN_LENGTH: 3,
  USERNAME_MAX_LENGTH: 30,
  BIO_MAX_LENGTH: 1000,
  REVIEW_MAX_LENGTH: 500,
  MESSAGE_MAX_LENGTH: 1000,
};

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection and try again.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  NOT_FOUND: 'The requested resource was not found.',
  SERVER_ERROR: 'Server error. Please try again later.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  SESSION_EXPIRED: 'Your session has expired. Please log in again.',
};

// Success Messages
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'Successfully logged in!',
  REGISTER_SUCCESS: 'Account created successfully!',
  PROFILE_UPDATED: 'Profile updated successfully!',
  BOOKING_CREATED: 'Booking request sent successfully!',
  BOOKING_CANCELLED: 'Booking cancelled successfully!',
  REVIEW_SUBMITTED: 'Review submitted successfully!',
  MESSAGE_SENT: 'Message sent successfully!',
  PASSWORD_CHANGED: 'Password changed successfully!',
};

// Routes
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  MENTORS: '/mentors',
  MENTOR_PROFILE: '/mentors/:id',
  BOOKINGS: '/bookings',
  SESSIONS: '/sessions',
  CHAT: '/chat',
  PROFILE: '/profile',
  ADMIN: '/admin',
  NOTIFICATIONS: '/notifications',
  HELP: '/help',
  PRIVACY: '/privacy',
  TERMS: '/terms',
};

export default {
  API_ENDPOINTS,
  USER_ROLES,
  BOOKING_STATUS,
  SESSION_STATUS,
  NOTIFICATION_TYPES,
  BADGE_CATEGORIES,
  SEARCH_FILTERS,
  EXPERIENCE_LEVELS,
  SESSION_DURATIONS,
  COMMON_TIMEZONES,
  PRICE_RANGES,
  LANGUAGES,
  FILE_UPLOAD,
  PAGINATION,
  THEMES,
  STORAGE_KEYS,
  VALIDATION,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  ROUTES,
};
