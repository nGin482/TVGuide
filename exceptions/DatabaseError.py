class DatabaseError(Exception):
    """
    Raised when a MongoDB operation fails
    """
    pass

class EpisodeNotFoundError(Exception):
    """
    Raised when the Episode subdocument does not exist in the Database
    """
    pass

class SeasonNotFoundError(Exception):
    """
    Raised when the Season subdocument does not exist in the Database
    """
    pass

class ShowNotFoundError(Exception):
    """
    Raised when the RecordedShow document can not be found in the Database
    """
    pass