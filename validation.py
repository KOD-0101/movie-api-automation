from logger_setup import get_logger

logger = get_logger("validation")


def is_valid_movie(movie: dict) -> tuple[bool, str]:
    """
    Checks a movie record before it gets inserted into the database.
    Each field is checked for presence and correct type.
    Returns a tuple, (True, "Valid") if the record is fine,
    or (False, reason) if something is wrong with it.
    """

    # id=0 is falsy in Python, so 'not movie.get("id")' catches both
    # missing IDs and IDs set to zero
    if not movie.get("id"):
        return False, "Missing movie ID"

    # title must exist and must be a string
    # integers or None won't pass
    title = movie.get("title")
    if not title or not isinstance(title, str):
        return False, "Missing or invalid title"

    # vote_average can be 0 (valid) but must be a number, not None or a string
    rating = movie.get("vote_average")
    if rating is None or not isinstance(rating, (int, float)):
        return False, "Missing or invalid rating"

    # vote_count must be a whole number
    # floats like 100.5 are rejected
    votes = movie.get("vote_count")
    if votes is None or not isinstance(votes, int):
        return False, "Missing or invalid vote count"

    # popularity must be a number, same pattern as rating
    popularity = movie.get("popularity")
    if popularity is None or not isinstance(popularity, (int, float)):
        return False, "Missing or invalid popularity"

    # release_date is optional, if it's absent that's fine,
    # but if it is present it must be a string, not a number
    release_date = movie.get("release_date")
    if release_date is not None and not isinstance(release_date, str):
        return False, "Invalid release date"

    return True, "Valid"
