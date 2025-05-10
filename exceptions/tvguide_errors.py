class MessageNotFoundException(Exception):
    """
    Raised when a TVGuide message could not be found
    """
    pass

class GuideNotCreatedError(Exception):
    """
    Raised when the Guide has not been created as part of the date's execution
    """
    pass