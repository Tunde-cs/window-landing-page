class RemoveXRobotsTagMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if 'X-Robots-Tag' in response:
            del response['X-Robots-Tag']
        return response