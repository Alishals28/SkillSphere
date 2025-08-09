"""
Simple Badge URLs

URL patterns for the simple badge system.
"""

from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    # Badge endpoints
    path('badges/', views.BadgeListView.as_view(), name='badge-list'),
    path('badges/my/', views.UserBadgesView.as_view(), name='user-badges'),
    path('badges/check/', views.check_badges, name='check-badges'),
]
