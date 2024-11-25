class FetcherException(Exception):
    """Base exception for fetcher module"""
    pass

class APIConnectionError(FetcherException):
    """Raised when unable to connect to the news API"""
    pass

class APIResponseError(FetcherException):
    """Raised when receiving invalid response from API"""
    pass

class APIRateLimitError(FetcherException):
    """Raised when API rate limit is exceeded"""
    pass