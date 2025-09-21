from django.http import HttpResponse

class HealthCheckBypassMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Always short-circuit /health/ requests
        if request.path == "/health/":
            return HttpResponse("OK", status=200)
        return self.get_response(request)

