from django.apps import AppConfig


class ManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.manager'
    verbose_name = 'Манаджер'
