class APIClientError(Exception):
    """Base exception for API client errors."""
    pass

class AuthenticationError(APIClientError):
    """Raised when authentication fails."""
    pass

class RequestError(APIClientError):
    """Raised for general request errors."""
    pass

class ResponseParseError(APIClientError):
    """Raised when response parsing fails."""
    pass
