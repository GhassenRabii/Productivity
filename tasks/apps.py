
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    name = "accounts"
    
    def ready(self):
        from . import signals  

class TasksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tasks"

    def ready(self):
        import tasks.signals  # ensures signals are registered
