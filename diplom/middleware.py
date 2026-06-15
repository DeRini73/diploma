import os
from hawk_python_sdk import Hawk


class HawkMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.hawk_client = None

        token = os.getenv('HAWK_API_KEY')
        if token:
            try:
                self.hawk_client = Hawk(token)
            except Exception:
                pass

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if self.hawk_client:
            try:
                self.hawk_client.send(exception)
            except Exception:
                pass
        return None
