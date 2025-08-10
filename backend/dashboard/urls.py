from django.urls import path
from . import views_simple

app_name = 'dashboard'

urlpatterns = [
    # Dashboard endpoints
    path('learner/', views_simple.LearnerDashboardView.as_view(), name='learner_dashboard'),
    path('mentor/', views_simple.MentorDashboardView.as_view(), name='mentor_dashboard'),
]
