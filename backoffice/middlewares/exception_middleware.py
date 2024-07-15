# backoffice/middlewares/exception_middleware.py

from django.http import JsonResponse

class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            response = self.handle_exception(e)

        return response

    def handle_exception(self, e):
        # Add your custom exception handling logic here
        # you can return JsonResponse with the error
        # and status code or any other HttpResponse
        return JsonResponse({"error": str(e)}, status=500)