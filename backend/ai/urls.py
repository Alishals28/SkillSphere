from django.urls import path
from . import views

urlpatterns = [
    # AI Responses
    path('responses/', views.AIResponseListView.as_view(), name='ai-response-list'),
    path('responses/<int:pk>/', views.AIResponseDetailView.as_view(), name='ai-response-detail'),
    
    # Learning Recommendations
    path('learning-recommendations/', views.generate_learning_recommendations, name='generate-learning-recommendations'),
    
    # Mentor Recommendations
    path('mentor-recommendations/', views.get_mentor_recommendations, name='get-mentor-recommendations'),
    path('mentor-recommendations/generate/', views.generate_mentor_recommendations, name='generate-mentor-recommendations'),
    path('mentor-recommendations/<int:recommendation_id>/rate/', views.rate_mentor_recommendation, name='rate-mentor-recommendation'),
    
    # Q&A Assistant
    path('ask/', views.ask_ai_question, name='ask-ai-question'),
    
    # Learning Paths
    path('learning-paths/', views.LearningPathListView.as_view(), name='learning-path-list'),
    path('learning-paths/<int:pk>/', views.LearningPathDetailView.as_view(), name='learning-path-detail'),
    
    # Session Summaries
    path('sessions/<int:session_id>/summary/', views.generate_session_summary, name='generate-session-summary'),
    
    # Skill Assessments
    path('skill-assessments/', views.SkillAssessmentListView.as_view(), name='skill-assessment-list'),
    
    # Dashboard
    path('dashboard-stats/', views.ai_dashboard_stats, name='ai-dashboard-stats'),
]
