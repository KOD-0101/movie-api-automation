from ui_helpers import poster_url


def test_poster_url_with_valid_path():
    path = "/abc123.jpg"
    expected = "https://image.tmdb.org/t/p/w500/abc123.jpg"
    assert poster_url(path) == expected


def test_poster_url_with_none():
    assert poster_url(None) is None
