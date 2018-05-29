import json
import urllib.request
import urllib.parse
import ssl

from app.services.tmdb import api_key


class TmdbMovie:

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

        content_url = "https://api.themoviedb.org/3/movie/" + str(self.id) + "/external_ids?api_key=" + api_key
        with urllib.request.urlopen(content_url) as url:
            self.external_ids = json.loads(url.read().decode())
            return self.external_ids

    @staticmethod
    def search_film(movie_name):
        content_url = 'https://api.themoviedb.org/3/search/multi?query=' + urllib.parse.quote_plus(movie_name) + \
                      '&api_key=' + api_key + '&include_adult=false&language=fr-FR'

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
        content_url = 'https://api.themoviedb.org/3/movie/' + str(movie_id) + \
                      '?api_key=' + api_key + '&language=fr-FR'

        ssl._create_default_https_context = ssl._create_unverified_context
        with urllib.request.urlopen(content_url) as url:
            res = json.loads(url.read().decode())
            return TmdbMovie(id=res['id'],
                             original_title=res['original_title'],
                             poster_path=res['poster_path'],
                             backdrop_path=res['backdrop_path'],
                             title=res['title'],
                             overview=res['overview'])

    @staticmethod
    def get_now_playing():
        now_playing_movies = []
        content_url = 'https://api.themoviedb.org/3/movie/now_playing?api_key=' + api_key + \
                      '&language=fr-FR&page=1&region=FR'

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

        return now_playing_movies
