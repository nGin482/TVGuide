class HTTPRequestError(Exception):
    """
    Raised when the IMDB API did not return a 200 status or returned an error
    """

    def __init__(self, message: str, status_code: int, status_text: str):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.status_text = status_text