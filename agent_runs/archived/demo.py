from api.client import APIClient
from api.auth import TokenAuth
from api.exceptions import APIClientError

# For demonstration, use httpbin.org (no auth required)
client = APIClient('https://httpbin.org')

try:
    response = client.get('/get', params={'test': 'value'})
    print('Response:', response)
except APIClientError as e:
    print('API Client Error:', e)
