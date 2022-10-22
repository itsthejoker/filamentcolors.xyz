class CacheControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if "HX-Request" in request.headers:
            response["Cache-Control"] = "no-store, max-age=0"
        return response
