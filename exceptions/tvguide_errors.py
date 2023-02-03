class MessageNotFoundException(Exception):
    """
    Raised when a TVGuide message could not be found
    """
    pass

class BBCNotCollectedException(Exception):
    """
    Raised when the BBC page prevents the scraper from collecting guide data
    """
    pass