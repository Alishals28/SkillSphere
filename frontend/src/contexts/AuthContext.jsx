import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI, tokenManager } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Load user from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    const token = tokenManager.getAccessToken();
    
    if (savedUser && token) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
        setIsAuthenticated(true);
        // Verify token is still valid
        authAPI.getCurrentUser().then(response => {
          if (response.success) {
            setUser(response.data);
            localStorage.setItem('user', JSON.stringify(response.data));
          } else {
            logout();
          }
        }).finally(() => {
          setLoading(false);
        });
      } catch (error) {
        console.error('Error parsing saved user:', error);
        logout();
        setLoading(false);
      }
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (credentials, passwordParam) => {
    setLoading(true);
    try {
      // Handle both object and individual parameters
      const email = credentials.email || credentials;
      const password = credentials.password || passwordParam;
      
      const response = await authAPI.login(email, password);
      
      if (response.success) {
        const { access, refresh, user: userData } = response.data;
        
        // Store tokens and user data
        tokenManager.setTokens(access, refresh);
        localStorage.setItem('user', JSON.stringify(userData));
        
        setUser(userData);
        setIsAuthenticated(true);
        
        return { success: true, user: userData };
      } else {
        // Handle API response with success: false
        let errorMessage = 'Login failed';
        
        if (response.error) {
          if (typeof response.error === 'string') {
            errorMessage = response.error;
          } else if (response.error.detail) {
            errorMessage = response.error.detail;
          } else if (response.error.message) {
            errorMessage = response.error.message;
          } else if (response.error.non_field_errors) {
            errorMessage = response.error.non_field_errors[0];
          } else {
            errorMessage = JSON.stringify(response.error);
          }
        }
        
        throw new Error(errorMessage);
      }
    } catch (error) {
      console.error('Login error:', error);
      
      // Extract meaningful error message
      let errorMessage = 'Network error - please check your connection';
      
      if (error.response) {
        // Server responded with error status
        if (error.response.data) {
          if (typeof error.response.data === 'string') {
            errorMessage = error.response.data;
          } else if (error.response.data.error) {
            errorMessage = error.response.data.error;
          } else if (error.response.data.message) {
            errorMessage = error.response.data.message;
          } else if (error.response.data.detail) {
            errorMessage = error.response.data.detail;
          } else if (error.response.data.non_field_errors) {
            errorMessage = error.response.data.non_field_errors[0];
          } else {
            errorMessage = `Server error (${error.response.status})`;
          }
        }
      } else if (error.message && error.message !== '[object Object]') {
        errorMessage = error.message;
      }
      
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const register = async (formData) => {
    setLoading(true);
    try {
      // Transform form data to match backend expectations
      const userData = {
        email: formData.email,
        password: formData.password,
        password_confirm: formData.confirmPassword,
        first_name: formData.firstName,
        last_name: formData.lastName,
        role: formData.role,
        bio: formData.bio,
        phone_number: formData.phone,
        country: formData.country,
        date_of_birth: formData.dateOfBirth,
        timezone: formData.timezone,
        
        // Role-specific fields
        learning_goals: formData.learningGoals,
        experience_level: formData.experienceLevel,
        preferred_session_duration: formData.preferredSessionDuration,
        
        // Mentor fields
        mentor_bio: formData.mentorBio,
        teaching_experience: formData.teachingExperience,
        hourly_rate: formData.hourlyRate,
        portfolio_url: formData.portfolioUrl,
        linkedin_url: formData.linkedinUrl,
        github_url: formData.githubUrl,
      };

      // Handle profile picture separately if provided
      if (formData.profilePicture) {
        const formDataWithFile = new FormData();
        Object.keys(userData).forEach(key => {
          if (userData[key] !== undefined && userData[key] !== '') {
            formDataWithFile.append(key, userData[key]);
          }
        });
        formDataWithFile.append('profile_picture', formData.profilePicture);
        
        const response = await authAPI.register(formDataWithFile);
        
        if (response.success) {
          const { access, refresh, user: newUser } = response.data;
          
          // Store tokens and user data
          tokenManager.setTokens(access, refresh);
          localStorage.setItem('user', JSON.stringify(newUser));
          
          setUser(newUser);
          setIsAuthenticated(true);
          
          return { success: true, user: newUser };
        } else {
          throw new Error(response.error || 'Registration failed');
        }
      } else {
        // No file upload, send as JSON
        const response = await authAPI.register(userData);
        
        if (response.success) {
          const { access, refresh, user: newUser } = response.data;
          
          // Store tokens and user data
          tokenManager.setTokens(access, refresh);
          localStorage.setItem('user', JSON.stringify(newUser));
          
          setUser(newUser);
          setIsAuthenticated(true);
          
          return { success: true, user: newUser };
        } else {
          throw new Error(response.error || 'Registration failed');
        }
      }
    } catch (error) {
      console.error('Registration error:', error);
      
      // Extract meaningful error message
      let errorMessage = 'Registration failed. Please try again.';
      
      if (error.response) {
        // Server responded with error status
        if (error.response.data) {
          if (typeof error.response.data === 'string') {
            errorMessage = error.response.data;
          } else if (error.response.data.error) {
            errorMessage = error.response.data.error;
          } else if (error.response.data.message) {
            errorMessage = error.response.data.message;
          } else if (error.response.data.detail) {
            errorMessage = error.response.data.detail;
          } else if (error.response.data.non_field_errors) {
            errorMessage = error.response.data.non_field_errors[0];
          } else if (error.response.data.email) {
            errorMessage = `Email: ${error.response.data.email[0]}`;
          } else if (error.response.data.password) {
            errorMessage = `Password: ${error.response.data.password[0]}`;
          } else {
            errorMessage = `Server error (${error.response.status})`;
          }
        }
      } else if (error.message && error.message !== '[object Object]') {
        errorMessage = error.message;
      }
      
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      const refreshToken = tokenManager.getRefreshToken();
      if (refreshToken) {
        await authAPI.logout(refreshToken);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local data regardless of API call success
      tokenManager.clearTokens();
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const updateUser = (updatedUser) => {
    setUser(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
  };

  const refreshUserData = async () => {
    try {
      const response = await authAPI.getCurrentUser();
      if (response.success) {
        updateUser(response.data);
        return response.data;
      }
    } catch (error) {
      console.error('Error refreshing user data:', error);
    }
    return null;
  };

  // Check if user has specific role
  const hasRole = (role) => {
    return user?.role === role;
  };

  // Check if user has any of the specified roles
  const hasAnyRole = (roles) => {
    return user && roles.includes(user.role);
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    updateUser,
    refreshUserData,
    hasRole,
    hasAnyRole,
    // Role helpers
    isLearner: hasRole('learner'),
    isMentor: hasRole('mentor'),
    isAdmin: hasRole('admin'),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
