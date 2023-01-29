class IMDBAPIRequestFailedError(Exception):
    """
    Raised when the IMDB API did not return a 200 status or returned an error
    """
    pass