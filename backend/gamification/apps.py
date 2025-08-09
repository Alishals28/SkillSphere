from django.apps import AppConfig


class GamificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gamification'
    
    def ready(self):
        """Import signals when app is ready"""
        import gamification.signals
    verbose_name = 'Gamification & Badges'
    
    def ready(self):
        """Import signals when the app is ready"""
        import gamification.signals
