import requests
from .exceptions import AuthenticationError, RequestError, ResponseParseError
from .retry import retry
from .utils import build_url

class APIClient:
    def __init__(self, base_url, auth=None, timeout=10):
        self.base_url = base_url
        self.auth = auth
        self.timeout = timeout

    def _get_headers(self, headers=None):
        base_headers = {}
        if self.auth:
            base_headers.update(self.auth.get_headers())
        if headers:
            base_headers.update(headers)
        return base_headers

    @retry(max_attempts=3, delay=2)
    def request(self, method, path, **kwargs):
        url = build_url(self.base_url, path)
        headers = self._get_headers(kwargs.pop('headers', None))
        try:
            response = requests.request(method, url, headers=headers, timeout=self.timeout, **kwargs)
        except requests.RequestException as e:
            raise RequestError(f"Request failed: {e}")
        if response.status_code == 401:
            raise AuthenticationError("Authentication failed.")
        try:
            data = response.json()
        except Exception:
            raise ResponseParseError("Failed to parse response JSON.")
        if not response.ok:
            raise RequestError(f"API error: {response.status_code} {data}")
        return data

    def get(self, path, **kwargs):
        return self.request('GET', path, **kwargs)

    def post(self, path, **kwargs):
        return self.request('POST', path, **kwargs)
