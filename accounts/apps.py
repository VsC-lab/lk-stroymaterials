from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        """
        Метод вызывается при готовности приложения.
        Здесь регистрируем сигналы.
        """
        # Импортируем и регистрируем сигналы
        from . import signals