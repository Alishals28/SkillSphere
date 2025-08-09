from django.urls import path
from . import views

urlpatterns = [
    # Advanced mentor search
    path('mentors/', views.AdvancedMentorSearchView.as_view(), name='advanced-mentor-search'),
    
    # Global search
    path('global/', views.GlobalSearchView.as_view(), name='global-search'),
    
    # Search suggestions/autocomplete
    path('suggestions/', views.search_suggestions, name='search-suggestions'),
    
    # Search filter options
    path('filters/', views.search_filters, name='search-filters'),
]
