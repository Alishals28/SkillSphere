from django.urls import path
from . import views

app_name = 'integrations'

urlpatterns = [
    # Provider management
    path('providers/', views.IntegrationProviderListView.as_view(), name='provider-list'),
    
    # User integrations
    path('', views.UserIntegrationListView.as_view(), name='integration-list'),
    path('<uuid:pk>/', views.UserIntegrationDetailView.as_view(), name='integration-detail'),
    
    # OAuth flow
    path('oauth/initiate/', views.initiate_oauth, name='oauth-initiate'),
    path('oauth/callback/<int:provider_id>/', views.oauth_callback, name='oauth-callback'),
    
    # Integration actions
    path('<uuid:integration_id>/test/', views.test_integration, name='integration-test'),
    path('<uuid:integration_id>/sync/', views.sync_integration, name='integration-sync'),
    
    # Integration-specific settings
    path('<uuid:integration_id>/calendar/', views.CalendarIntegrationView.as_view(), name='calendar-settings'),
    path('<uuid:integration_id>/payment/', views.PaymentIntegrationView.as_view(), name='payment-settings'),
    path('<uuid:integration_id>/video/', views.VideoIntegrationView.as_view(), name='video-settings'),
    
    # Logs and monitoring
    path('<uuid:integration_id>/logs/', views.IntegrationLogView.as_view(), name='integration-logs'),
    
    # Webhooks
    path('webhook/<str:provider_name>/<str:endpoint_path>/', views.webhook_handler, name='webhook-handler'),
]
