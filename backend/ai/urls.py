from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'learning-paths', views.LearningPathViewSet, basename='learning-path')
router.register(r'skill-assessments', views.SkillAssessmentViewSet, basename='skill-assessment')
router.register(r'mentor-recommendations', views.MentorRecommendationViewSet, basename='mentor-recommendation')

urlpatterns = [
    # Include ViewSet routes
    path('', include(router.urls)),
    
    # AI Responses
    path('responses/', views.AIResponseListView.as_view(), name='ai-response-list'),
    path('responses/<int:pk>/', views.AIResponseDetailView.as_view(), name='ai-response-detail'),
    
    # Learning Recommendations
    path('learning-recommendations/', views.generate_learning_recommendations, name='generate-learning-recommendations'),
    
    # Mentor Recommendations (function-based views)
    path('mentor-recommendations/generate/', views.generate_mentor_recommendations, name='generate-mentor-recommendations'),
    path('mentor-recommendations/<int:recommendation_id>/rate/', views.rate_mentor_recommendation, name='rate-mentor-recommendation'),
    
    # Q&A Assistant
    path('ask/', views.ask_ai_question, name='ask-ai-question'),
    
    # Session Summaries
    path('sessions/<int:session_id>/summary/', views.generate_session_summary, name='generate-session-summary'),
    
    # Dashboard & Analytics
    path('dashboard-stats/', views.ai_dashboard_stats, name='ai-dashboard-stats'),
]
