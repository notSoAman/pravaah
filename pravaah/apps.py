from django.apps import AppConfig


class PravaahConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pravaah'

    def ready(self):
        import pravaah.signals  # noqa: F401

