from logger_setup import get_logger

logger = get_logger("validation")


def is_valid_movie(movie: dict) -> tuple[bool, str]:
    """
    Validate a movie record before inserting into the database.
    Returns:
        (True, "Valid") if record is usable
        (False, reason) if record should be skipped
    """

    if not movie.get("id"):
        return False, "Missing movie ID"

    title = movie.get("title")
    if not title or not isinstance(title, str):
        return False, "Missing or invalid title"

    rating = movie.get("vote_average")
    if rating is None or not isinstance(rating, (int, float)):
        return False, "Missing or invalid rating"

    votes = movie.get("vote_count")
    if votes is None or not isinstance(votes, int):
        return False, "Missing or invalid vote count"

    popularity = movie.get("popularity")
    if popularity is None or not isinstance(popularity, (int, float)):
        return False, "Missing or invalid popularity"

    release_date = movie.get("release_date")
    if release_date is not None and not isinstance(release_date, str):
        return False, "Invalid release date"

    return True, "Valid"
