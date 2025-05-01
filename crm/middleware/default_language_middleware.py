from django.utils import translation

class DefaultLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.COOKIES.get('django_language'):
            translation.activate('uz')
            request.LANGUAGE_CODE = 'uz'
        response = self.get_response(request)
        translation.deactivate()
        return response