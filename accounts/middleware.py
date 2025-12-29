# accounts/middleware.py
"""
Простые middleware для отладки
"""

class SimpleMiddleware:
    """Простой middleware для тестирования"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Код до обработки запроса
        response = self.get_response(request)
        # Код после обработки запроса
        return response