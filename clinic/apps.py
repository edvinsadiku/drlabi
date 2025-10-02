# clinic/apps.py
from django.apps import AppConfig

class ClinicConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "clinic"
    verbose_name = "Clinic"

    def ready(self):
        # Importo modelet e tjera që ke jashtë models.py
        import clinic.models_new
