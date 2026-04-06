from validation import is_valid_movie


def test_valid_movie():
    movie = {
        "id": 1,
        "title": "Inception",
        "vote_average": 8.8,
        "vote_count": 12000,
        "popularity": 55.3,
        "release_date": "2010-07-16"
    }

    valid, reason = is_valid_movie(movie)
    assert valid is True
    assert reason == "Valid"


def test_invalid_movie_missing_id():
    movie = {
        "title": "Inception",
        "vote_average": 8.8,
        "vote_count": 12000,
        "popularity": 55.3,
        "release_date": "2010-07-16"
    }

    valid, reason = is_valid_movie(movie)
    assert valid is False
    assert reason == "Missing movie ID"


def test_invalid_movie_missing_title():
    movie = {
        "id": 1,
        "vote_average": 8.8,
        "vote_count": 12000,
        "popularity": 55.3,
        "release_date": "2010-07-16"
    }

    valid, reason = is_valid_movie(movie)
    assert valid is False
    assert reason == "Missing or invalid title"
