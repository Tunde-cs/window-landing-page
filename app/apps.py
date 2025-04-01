from django.apps import AppConfig

class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        import app.signals  # ✅ This line ensures signals.py runs at startup
