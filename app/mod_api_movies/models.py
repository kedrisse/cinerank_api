# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db
from app.services.rates.allocine_rate import AllocineRate
from app.services.rates.imdb_rate import ImdbRate
from app.services.tmdb.tmdb_movie import TmdbMovie


def build_api_index_response(movies):
    json = {
        'movies': []
    }

    for movie in movies:
        m = {
            'title': movie.tmdb_movie.title if movie.tmdb_movie is not None else None,
            'original_title': movie.tmdb_movie.original_title if movie.tmdb_movie is not None else None,
            'poster_path': movie.tmdb_movie.get_poster_path() if movie.tmdb_movie is not None else None,
            'backdrop_path': movie.tmdb_movie.get_backdrop_path() if movie.tmdb_movie is not None else None,
            'overview': movie.tmdb_movie.overview if movie.tmdb_movie is not None else None,
            'global_score': movie.score(),
            'rates': {
                'imdb': movie.imdb_rate,
                'allocine': movie.allocine_rate
            },
            'rates_count': {
                'imdb': movie.imdb_number_rate,
                'allocine': movie.allocine_number_rate
            },
            'external_ids': {
                'imdb': ("https://www.imdb.com/title/tt" + str(movie.imdb_id)) if movie.imdb_id is not None else None,
                'allocine': ('http://www.allocine.fr/film/fichefilm_gen_cfilm=' + str(movie.allocine_id) + '.html') if movie.allocine_id is not None else None
            }
        }
        json['movies'].append(m)

    return json


# Define a base model for other database tables to inherit
class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())


# Define a Movie model
class Movie(Base):
    __tablename__ = 'movies'

    gaumont_id = db.Column(db.Integer, nullable=False, unique=True)
    tmdb_id = db.Column(db.Integer, nullable=True, unique=True)
    imdb_id = db.Column(db.Integer, nullable=True, unique=True)
    allocine_id = db.Column(db.Integer, nullable=True, unique=True)

    imdb_rate = db.Column(db.Float, nullable=True)
    allocine_rate = db.Column(db.Float, nullable=True)

    imdb_number_rate = db.Column(db.Integer, nullable=True)
    allocine_number_rate = db.Column(db.Integer, nullable=True)

    tmdb_movie = None

    def set_tmdb_movie(self, tmdb_movie):
        self.tmdb_movie = tmdb_movie

    def score(self, k=0.5):
        if self.imdb_rate is None or self.allocine_rate is None:
            return 0.

        score = self.local_score(self.imdb_rate, 10, self.imdb_number_rate, 5000) + \
                self.local_score(self.allocine_rate, 5, self.allocine_number_rate, 500)
        return round(score, 1)

    def local_score(self, rate, max_rate, number_rate, constante=0.5):
        return (((number_rate * rate / max_rate) + (0.5 * constante)) / (number_rate + constante)) * max_rate

    @staticmethod
    def get_tmdb_now_playing_movies(format=None, order=None):
        now_playing_movies = []
        thmdb_now_playing_movies = TmdbMovie.get_now_playing()

        for tmdb_movie in thmdb_now_playing_movies:
            if Movie.query.filter_by(tmdb_id=tmdb_movie.id).count() > 0:
                print(tmdb_movie.title, 'exists')

                movie = Movie.query.filter_by(tmdb_id=tmdb_movie.id).first()
                movie.set_tmdb_movie(tmdb_movie)

                now_playing_movies.append(movie)

            else:
                allocine = {}
                imdb = {}

                allocine['id'], allocine['rate'], allocine['count'] = AllocineRate.call(tmdb_movie.original_title, tmdb_movie.title)

                imdb_id = tmdb_movie.get_external_ids()['imdb_id'][2:]
                imdb['id'], imdb['rate'], imdb['count'] = ImdbRate.call(imdb_id)

                movie = Movie(gaumont_id=tmdb_movie.id, tmdb_id=tmdb_movie.id, imdb_id=imdb['id'], imdb_rate=imdb['rate'], imdb_number_rate=imdb['count'],
                              allocine_id=allocine['id'], allocine_rate=allocine['rate'], allocine_number_rate=allocine['count'])
                movie.set_tmdb_movie(tmdb_movie)

                db.session.add(movie)
                db.session.commit()

                print(tmdb_movie.title, 'ajouté')

                now_playing_movies.append(movie)

        if order == 'score':
            now_playing_movies = sorted(now_playing_movies, key=lambda x: x.score(), reverse=True)

        if format == 'api_json':
            return build_api_index_response(now_playing_movies)

        return now_playing_movies
