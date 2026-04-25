from unittest.mock import patch, MagicMock
import pandas as pd

# Streamlit mock factory


def make_st_mock():
    """
    Builds a MagicMock that covers every st.* call made in dashboard.py.
    The key things to get right:
    - cache_data needs to be a passthrough decorator so cached functions run
    - columns needs to return a list of the right length (3 for the home page,
      2 for the analytics section)
    - session_state needs selected_movie_id set to avoid AttributeError
    """
    st = MagicMock()
    st.cache_data = lambda **kwargs: (lambda f: f)
    st.session_state = MagicMock()
    st.session_state.selected_movie_id = None
    st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
    st.secrets = {}
    return st


def sample_df() -> pd.DataFrame:
    """Returns a small DataFrame shaped like the real movies table."""
    return pd.DataFrame(
        [
            {
                "movie_id": 1,
                "title": "Inception",
                "rating": 8.8,
                "popularity": 55.3,
                "release_date": "2010-07-16",
                "category": "top_rated",
            },
            {
                "movie_id": 2,
                "title": "The Dark Knight",
                "rating": 9.0,
                "popularity": 80.1,
                "release_date": "2008-07-18",
                "category": "top_rated",
            },
            {
                "movie_id": 3,
                "title": "Interstellar",
                "rating": 8.6,
                "popularity": 45.2,
                "release_date": "2014-11-07",
                "category": "popular",
            },
        ]
    )


# render_home_page


def test_render_home_page_runs(monkeypatch):
    # Home page should render without raising any exceptions
    st_mock = make_st_mock()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import dashboard

    importlib.reload(dashboard)

    dashboard.render_home_page()
    st_mock.title.assert_called_once()


def test_render_home_page_calls_title(monkeypatch):
    # The page title should contain the word "Movie"
    st_mock = make_st_mock()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import dashboard

    importlib.reload(dashboard)

    dashboard.render_home_page()

    title_call = st_mock.title.call_args[0][0]
    assert "Movie" in title_call


# render_local_analytics


def test_render_local_analytics_with_data(monkeypatch):
    # When the database has rows, no warning should be shown
    st_mock = make_st_mock()
    st_mock.text_input.return_value = ""
    # analytics section uses 2-column layout, not 3
    st_mock.columns.return_value = [MagicMock(), MagicMock()]

    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import dashboard

    importlib.reload(dashboard)

    # Patch get_local_data so no real DB is needed,
    # patch plt so no actual matplotlib figures are created
    with patch("dashboard.get_local_data", return_value=sample_df()), patch(
        "dashboard.plt"
    ) as mock_plt:
        mock_plt.subplots.return_value = (MagicMock(), MagicMock())
        dashboard.render_local_analytics()

    st_mock.warning.assert_not_called()


def test_render_local_analytics_empty_db(monkeypatch):
    # An empty DataFrame should trigger st.warning and return early
    st_mock = make_st_mock()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import dashboard

    importlib.reload(dashboard)

    with patch("dashboard.get_local_data", return_value=pd.DataFrame()):
        dashboard.render_local_analytics()

    st_mock.warning.assert_called_once()


def test_render_local_analytics_search(monkeypatch):
    # Searching for a title should filter the dataframe and call st.dataframe
    st_mock = make_st_mock()
    st_mock.text_input.return_value = "Inception"
    st_mock.columns.return_value = [MagicMock(), MagicMock()]

    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import dashboard

    importlib.reload(dashboard)

    with patch("dashboard.get_local_data", return_value=sample_df()), patch(
        "dashboard.plt"
    ) as mock_plt:
        mock_plt.subplots.return_value = (MagicMock(), MagicMock())
        dashboard.render_local_analytics()

    st_mock.dataframe.assert_called()


# render_genre_recommendations


def test_render_genre_recommendations_no_api_key(monkeypatch):
    # If TMDB_API_KEY is not set, a warning should be shown and
    # the function should return without making any API calls
    st_mock = make_st_mock()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import dashboard

    importlib.reload(dashboard)

    with patch("dashboard.TMDB_API_KEY", None):
        dashboard.render_genre_recommendations()

    st_mock.warning.assert_called_once()


def test_render_genre_recommendations_with_genres(monkeypatch):
    # When genres load successfully, the genre selectbox should be rendered
    st_mock = make_st_mock()
    st_mock.selectbox.return_value = "Horror"
    st_mock.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
    st_mock.session_state.selected_movie_id = None

    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import dashboard

    importlib.reload(dashboard)

    fake_genres = [{"id": 27, "name": "Horror"}, {"id": 28, "name": "Action"}]
    fake_movies = [
        {
            "id": 1,
            "title": "A Horror Film",
            "poster_path": None,
            "release_date": "2022-01-01",
            "vote_average": 6.5,
        }
    ] * 3

    with patch("dashboard.TMDB_API_KEY", "fake_key"), patch(
        "dashboard.get_genres", return_value=fake_genres
    ), patch("dashboard.get_movies_by_genre", return_value=fake_movies):
        dashboard.render_genre_recommendations()

    st_mock.selectbox.assert_called_once()


def test_render_genre_recommendations_no_movies(monkeypatch):
    # If the genre returns no movies, st.info should be shown
    st_mock = make_st_mock()
    st_mock.selectbox.return_value = "Horror"
    st_mock.session_state.selected_movie_id = None

    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import dashboard

    importlib.reload(dashboard)

    fake_genres = [{"id": 27, "name": "Horror"}]

    with patch("dashboard.TMDB_API_KEY", "fake_key"), patch(
        "dashboard.get_genres", return_value=fake_genres
    ), patch("dashboard.get_movies_by_genre", return_value=[]):
        dashboard.render_genre_recommendations()

    st_mock.info.assert_called_once()


# render_dashboard_page


def test_render_dashboard_page_runs(monkeypatch):
    # render_dashboard_page should call both sub-renderers exactly once
    st_mock = make_st_mock()
    monkeypatch.setitem(__import__("sys").modules, "streamlit", st_mock)

    import importlib
    import dashboard

    importlib.reload(dashboard)

    with patch("dashboard.render_local_analytics") as mock_local, patch(
        "dashboard.render_genre_recommendations"
    ) as mock_genre:
        dashboard.render_dashboard_page()

    mock_local.assert_called_once()
    mock_genre.assert_called_once()
    st_mock.title.assert_called_once()
