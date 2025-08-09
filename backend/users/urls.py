from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Email verification
    path('auth/verify-email/', views.EmailVerificationView.as_view(), name='verify_email'),
    path('auth/resend-verification/', views.ResendVerificationEmailView.as_view(), name='resend_verification'),
    
    # Password reset
    path('auth/password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('auth/password-reset-confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # User profile
    path('users/me/', views.UserProfileView.as_view(), name='user_profile'),
    
    # Mentor endpoints
    path('mentors/', views.MentorListView.as_view(), name='mentor_list'),
    path('mentors/<int:pk>/', views.MentorDetailView.as_view(), name='mentor_detail'),
    
    # Admin endpoints
    path('admin/mentors/pending/', views.PendingMentorsView.as_view(), name='pending_mentors'),
    path('admin/mentors/<int:pk>/approve/', views.ApproveMentorView.as_view(), name='approve_mentor'),
]
