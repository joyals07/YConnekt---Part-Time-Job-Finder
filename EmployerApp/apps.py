from django.apps import AppConfig

class EmployerAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'EmployerApp'

    def ready(self):
        import EmployerApp.signals