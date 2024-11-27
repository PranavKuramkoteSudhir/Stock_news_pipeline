class ProcessorException(Exception):
    """Base exception for processor module"""
    pass

class SentimentAnalysisError(ProcessorException):
    """Raised when sentiment analysis fails"""
    pass

class InvalidInputError(ProcessorException):
    """Raised when input data is invalid or missing required fields"""
    pass

class PersistenceError(ProcessorException):
    """Raised when failing to save results to database"""
    pass

class TextPreprocessingError(ProcessorException):
    """Raised when text preprocessing fails"""
    pass