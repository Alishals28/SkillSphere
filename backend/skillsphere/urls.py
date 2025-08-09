"""
URL configuration for skillsphere project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from availability.urls import public_urlpatterns as availability_public_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication & User Management
    path('api/', include('users.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    
    # Core Features
    path('api/skills/', include('skills.urls')),
    path('api/availability/', include('availability.urls')),
    path('api/bookings/', include('bookings.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/ai/', include('ai.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/search/', include('search.urls')),
    
    # Public endpoints (no auth required)
    path('api/', include(availability_public_urls)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
