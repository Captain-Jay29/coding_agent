# API Client Library

A simple Python API client library with:
- HTTP requests
- Authentication
- Response parsing
- Retry logic
- Error handling

## Usage Example

```
from api.client import APIClient
from api.auth import TokenAuth

client = APIClient('https://api.example.com', auth=TokenAuth('your_token'))
response = client.get('/endpoint')
print(response)
```
