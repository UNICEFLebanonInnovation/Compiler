class CacheControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Keep the existing no-cache default while preserving the stricter
        # private/no-store policy supplied by photo export responses.
        if not response.has_header('Cache-Control'):
            response['Cache-Control'] = 'no-cache'

        return response
