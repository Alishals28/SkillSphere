from django.urls import path
from . import views

urlpatterns = [
    # Notification CRUD
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    
    # Notification actions
    path('<int:notification_id>/mark-read/', views.mark_notification_read, name='mark-notification-read'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark-all-read'),
    path('bulk-action/', views.bulk_notification_action, name='bulk-notification-action'),
    
    # Notification stats and preferences
    path('stats/', views.notification_stats, name='notification-stats'),
    path('preferences/', views.NotificationPreferenceView.as_view(), name='notification-preferences'),
    
    # Admin
    path('create/', views.CreateNotificationView.as_view(), name='create-notification'),
]
