from django.urls import path
from . import views

app_name = 'skills'

urlpatterns = [
    # Skill categories
    path('categories/', views.SkillCategoryListView.as_view(), name='skill-categories-list'),
    path('categories/<int:pk>/', views.SkillCategoryDetailView.as_view(), name='skill-category-detail'),
    
    # Skills
    path('', views.SkillListCreateView.as_view(), name='skills-list'),
    path('<int:pk>/', views.SkillDetailView.as_view(), name='skill-detail'),
    path('search/', views.SkillSearchView.as_view(), name='skills-search'),
    path('popular/', views.PopularSkillsView.as_view(), name='popular-skills'),
    
    # Mentor skills management
    path('mentor/skills/', views.MentorSkillListView.as_view(), name='mentor-skills-list'),
    path('mentor/skills/<int:pk>/', views.MentorSkillDetailView.as_view(), name='mentor-skill-detail'),
    path('mentor/skills/bulk/', views.bulk_add_mentor_skills, name='bulk-add-mentor-skills'),
    
    # Mentor tags
    path('mentor/tags/', views.MentorTagListView.as_view(), name='mentor-tags-list'),
    path('mentor/tags/<int:pk>/', views.MentorTagDetailView.as_view(), name='mentor-tag-detail'),
    
    # Statistics
    path('stats/', views.skill_statistics, name='skills-stats'),
]
