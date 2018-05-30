import json
import urllib.request
import urllib.parse
import ssl
from difflib import SequenceMatcher

from app.services.tmdb import api_key, language


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio() > 0.8


def api_request_log(msg):
    TmdbMovie.nb_api_request += 1
    print(str(TmdbMovie.nb_api_request) + '. TMDB API REQUEST - ' + msg)


class TmdbMovie:
    now_playing_movies = {}
    nb_api_request = 0
    loaded_movies = {}

    def __init__(self, id=None, original_title=None, poster_path=None, backdrop_path=None, title=None, imdb_id=None,
                 overview=None):
        self.id = id
        self.original_title = original_title
        self.poster_path = poster_path
        self.title = title
        self.external_ids = None
        self.imdb_id = imdb_id
        self.backdrop_path = backdrop_path
        self.overview = overview

    def get_poster_path(self):
        if self.poster_path is None:
            return None
        return 'https://image.tmdb.org/t/p/w500' + self.poster_path

    def get_backdrop_path(self):
        if self.backdrop_path is None:
            return None
        return 'https://image.tmdb.org/t/p/original' + self.backdrop_path

    def get_external_ids(self):
        if self.external_ids is not None:
            return self.external_ids

        api_request_log('get_external_ids')
        content_url = "https://api.themoviedb.org/3/movie/" + str(self.id) + "/external_ids?api_key=" + api_key
        with urllib.request.urlopen(content_url) as url:
            self.external_ids = json.loads(url.read().decode())
            return self.external_ids

    @staticmethod
    def search_film(movie_name):
        api_request_log('search_film ' + movie_name)

        content_url = 'https://api.themoviedb.org/3/search/multi?query=' + urllib.parse.quote_plus(movie_name) + \
                      '&api_key=' + api_key + '&include_adult=false&language=' + language

        ssl._create_default_https_context = ssl._create_unverified_context
        with urllib.request.urlopen(content_url) as url:
            results = json.loads(url.read().decode())['results']

            for res in results:
                if res['media_type'] == 'movie':
                    return TmdbMovie(id=res['id'],
                                     original_title=res['original_title'],
                                     poster_path=res['poster_path'],
                                     backdrop_path=res['backdrop_path'],
                                     title=res['title'],
                                     overview=res['overview'])

    @staticmethod
    def get_film(movie_id):
        if movie_id in TmdbMovie.loaded_movies:
            return TmdbMovie.loaded_movies[movie_id]

        api_request_log('get_film ' + str(movie_id))
        content_url = 'https://api.themoviedb.org/3/movie/' + str(movie_id) + \
                      '?api_key=' + api_key + '&language=' + language

        ssl._create_default_https_context = ssl._create_unverified_context
        with urllib.request.urlopen(content_url) as url:
            res = json.loads(url.read().decode())
            TmdbMovie.loaded_movies[movie_id] = TmdbMovie(id=res['id'],
                                                          original_title=res['original_title'],
                                                          poster_path=res['poster_path'],
                                                          backdrop_path=res['backdrop_path'],
                                                          title=res['title'],
                                                          overview=res['overview'])

            return TmdbMovie.loaded_movies[movie_id]

    @staticmethod
    def get_now_playing(page=1):

        if page in TmdbMovie.now_playing_movies and TmdbMovie.now_playing_movies[page] is not None:
            return TmdbMovie.now_playing_movies[page]

        now_playing_movies = []

        api_request_log('get_now_playing page ' + str(page))
        content_url = 'https://api.themoviedb.org/3/movie/now_playing?api_key=' + api_key + \
                      '&language=' + language + '&page=' + str(page) + '&region=FR'

        ssl._create_default_https_context = ssl._create_unverified_context
        with urllib.request.urlopen(content_url) as url:
            results = json.loads(url.read().decode())['results']

            for res in results:
                now_playing_movies.append(TmdbMovie(id=res['id'],
                                                    original_title=res['original_title'],
                                                    poster_path=res['poster_path'],
                                                    backdrop_path=res['backdrop_path'],
                                                    title=res['title'],
                                                    overview=res['overview']))

        TmdbMovie.now_playing_movies[page] = now_playing_movies

        return now_playing_movies

    @staticmethod
    def search_in_now_playing(tmdb_id, nb_pages=1):

        for page in range(nb_pages):
            page = page + 1

            for tmdb_movie in TmdbMovie.get_now_playing(page):
                if tmdb_movie.id == tmdb_id:
                    return tmdb_movie

        return None
