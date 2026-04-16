from validation import is_valid_movie

# Valid cases


def test_valid_movie():
    movie = {
        "id": 1,
        "title": "Inception",
        "vote_average": 8.8,
        "vote_count": 12000,
        "popularity": 55.3,
        "release_date": "2010-07-16",
    }
    valid, reason = is_valid_movie(movie)
    assert valid is True
    assert reason == "Valid"


def test_valid_movie_without_release_date():
    """release_date is optional — None should still be valid"""
    movie = {
        "id": 2,
        "title": "No Date Movie",
        "vote_average": 7.0,
        "vote_count": 500,
        "popularity": 10.0,
        "release_date": None,
    }
    valid, reason = is_valid_movie(movie)
    assert valid is True
    assert reason == "Valid"


def test_valid_movie_zero_rating():
    """A rating of exactly 0 is valid"""
    movie = {
        "id": 3,
        "title": "Zero Rated",
        "vote_average": 0,
        "vote_count": 1,
        "popularity": 1.0,
    }
    valid, reason = is_valid_movie(movie)
    assert valid is True


# Missing / invalid ID


def test_invalid_movie_missing_id():
    movie = {
        "title": "Inception",
        "vote_average": 8.8,
        "vote_count": 12000,
        "popularity": 55.3,
    }
    valid, reason = is_valid_movie(movie)
    assert valid is False
    assert reason == "Missing movie ID"


def test_invalid_movie_id_zero():
    """id=0 is falsy — should be treated as missing"""
    movie = {
        "id": 0,
        "title": "Inception",
        "vote_average": 8.8,
        "vote_count": 12000,
        "popularity": 55.3,
    }
    valid, reason = is_valid_movie(movie)
    assert valid is False
    assert reason == "Missing movie ID"


# Missing / invalid title


def test_invalid_movie_missing_title():
    movie = {
        "id": 1,
        "vote_average": 8.8,
        "vote_count": 12000,
        "popularity": 55.3,
    }
    valid, reason = is_valid_movie(movie)
    assert valid is False
    assert reason == "Missing or invalid title"


def test_invalid_movie_empty_title():
    movie = {
        "id": 1,
        "title": "",
        "vote_average": 8.8,
        "vote_count": 12000,
        "popularity": 55.3,
    }
    valid, reason = is_valid_movie(movie)
    assert valid is False
    assert reason == "Missing or invalid title"


def test_invalid_movie_numeric_title():
    movie = {
        "id": 1,
        "title": 12345,
        "vote_average": 8.8,
        "vote_count": 12000,
        "popularity": 55.3,
    }
    valid, reason = is_valid_movie(movie)
    assert valid is False
    assert reason == "Missing or invalid title"


# Missing / invalid rating


def test_invalid_movie_missing_rating():
    movie = {
        "id": 1,
        "title": "Inception",
        "vote_count": 12000,
        "popularity": 55.3,
    }
    valid, reason = is_valid_movie(movie)
    assert valid is False
    assert reason == "Missing or invalid rating"


def test_invalid_movie_string_rating():
    movie = {
        "id": 1,
        "title": "Inception",
        "vote_average": "high",
        "vote_count": 12000,
        "popularity": 55.3,
    }
    valid, reason = is_valid_movie(movie)
    assert valid is False
    assert reason == "Missing or invalid rating"


# Missing / invalid vote count


def test_invalid_movie_missing_votes():
    movie = {
        "id": 1,
        "title": "Inception",
        "vote_average": 8.8,
        "popularity": 55.3,
    }
    valid, reason = is_valid_movie(movie)
    assert valid is False
    assert reason == "Missing or invalid vote count"


def test_invalid_movie_float_votes():
    """vote_count must be an int, not a float"""
    movie = {
        "id": 1,
        "title": "Inception",
        "vote_average": 8.8,
        "vote_count": 100.5,
        "popularity": 55.3,
    }
    valid, reason = is_valid_movie(movie)
    assert valid is False
    assert reason == "Missing or invalid vote count"


# Missing / invalid popularity


def test_invalid_movie_missing_popularity():
    movie = {
        "id": 1,
        "title": "Inception",
        "vote_average": 8.8,
        "vote_count": 12000,
    }
    valid, reason = is_valid_movie(movie)
    assert valid is False
    assert reason == "Missing or invalid popularity"


def test_invalid_movie_string_popularity():
    movie = {
        "id": 1,
        "title": "Inception",
        "vote_average": 8.8,
        "vote_count": 12000,
        "popularity": "very popular",
    }
    valid, reason = is_valid_movie(movie)
    assert valid is False
    assert reason == "Missing or invalid popularity"


# Invalid release date


def test_invalid_movie_numeric_release_date():
    """release_date must be a string if provided"""
    movie = {
        "id": 1,
        "title": "Inception",
        "vote_average": 8.8,
        "vote_count": 12000,
        "popularity": 55.3,
        "release_date": 20100716,
    }
    valid, reason = is_valid_movie(movie)
    assert valid is False
    assert reason == "Invalid release date"
