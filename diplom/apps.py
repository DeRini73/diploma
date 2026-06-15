from django.apps import AppConfig

class DiplomConfig(AppConfig):
    name = 'diplom'

    def ready(self):
        from . import hawk_handler