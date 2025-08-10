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
        // Generate username from email (part before @)
        username: formData.email.split('@')[0],
      };

      // Add optional fields only if they have values
      if (formData.bio && formData.bio.trim()) userData.bio = formData.bio;
      if (formData.phone && formData.phone.trim()) userData.phone_number = formData.phone;
      if (formData.country && formData.country.trim()) userData.country = formData.country;
      if (formData.dateOfBirth) userData.date_of_birth = formData.dateOfBirth;
      if (formData.timezone && formData.timezone.trim()) userData.timezone = formData.timezone;
      
      // Role-specific fields for learners
      if (formData.role === 'learner') {
        if (formData.learningGoals && formData.learningGoals.trim()) {
          userData.learning_goals = formData.learningGoals;
        }
        if (formData.experienceLevel && formData.experienceLevel.trim()) {
          userData.experience_level = formData.experienceLevel;
        }
        if (formData.preferredSessionDuration) {
          userData.preferred_session_duration = formData.preferredSessionDuration;
        }
      }
      
      // Mentor fields
      if (formData.role === 'mentor') {
        if (formData.mentorBio && formData.mentorBio.trim()) {
          userData.mentor_bio = formData.mentorBio;
        }
        if (formData.teachingExperience && formData.teachingExperience.trim()) {
          userData.teaching_experience = formData.teachingExperience;
        }
        if (formData.hourlyRate) {
          userData.hourly_rate = formData.hourlyRate;
        }
        if (formData.portfolioUrl && formData.portfolioUrl.trim()) {
          userData.portfolio_url = formData.portfolioUrl;
        }
        if (formData.linkedinUrl && formData.linkedinUrl.trim()) {
          userData.linkedin_url = formData.linkedinUrl;
        }
        if (formData.githubUrl && formData.githubUrl.trim()) {
          userData.github_url = formData.githubUrl;
        }
      }

      console.log('Cleaned userData being sent:', userData);

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
          // Handle API error response
          let errorMessage = 'Registration failed';
          if (response.error) {
            if (typeof response.error === 'string') {
              errorMessage = response.error;
            } else if (response.error.non_field_errors) {
              errorMessage = response.error.non_field_errors[0];
            } else if (response.error.email) {
              errorMessage = `Email: ${response.error.email[0]}`;
            } else if (response.error.password) {
              errorMessage = `Password: ${response.error.password[0]}`;
            } else {
              // Extract first field error
              const firstKey = Object.keys(response.error)[0];
              if (firstKey && Array.isArray(response.error[firstKey])) {
                errorMessage = `${firstKey.replace('_', ' ')}: ${response.error[firstKey][0]}`;
              } else {
                errorMessage = JSON.stringify(response.error);
              }
            }
          }
          throw new Error(errorMessage);
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
          // Handle API error response
          let errorMessage = 'Registration failed';
          if (response.error) {
            console.log('Processing API error:', response.error);
            if (typeof response.error === 'string') {
              errorMessage = response.error;
            } else if (response.error.non_field_errors) {
              errorMessage = response.error.non_field_errors[0];
            } else if (response.error.email) {
              errorMessage = `Email: ${response.error.email[0]}`;
            } else if (response.error.password) {
              errorMessage = `Password: ${response.error.password[0]}`;
            } else {
              // Extract first field error
              const firstKey = Object.keys(response.error)[0];
              if (firstKey && Array.isArray(response.error[firstKey])) {
                errorMessage = `${firstKey.replace('_', ' ')}: ${response.error[firstKey][0]}`;
              } else {
                errorMessage = JSON.stringify(response.error);
              }
            }
          }
          console.log('Final error message:', errorMessage);
          throw new Error(errorMessage);
        }
      }
    } catch (error) {
      // This catch block should only handle network errors or unexpected errors
      console.error('Unexpected registration error:', error);
      
      // If it's already an Error we threw, re-throw it
      if (error.message && error.message !== '[object Object]') {
        throw error;
      }
      
      // Otherwise, handle unexpected errors
      throw new Error('Network error - please check your connection and try again');
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
