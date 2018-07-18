# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db
from app.services.gaumont.cinema import Cinema
from app.services.rates.allocine_rate import AllocineRate
from app.services.rates.imdb_rate import ImdbRate
from app.services.tmdb.tmdb_movie import TmdbMovie
from sqlalchemy.sql import func
import datetime


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
                'allocine': ('http://www.allocine.fr/film/fichefilm_gen_cfilm=' + str(
                    movie.allocine_id) + '.html') if movie.allocine_id is not None else None
            },
            'upcoming_seances': movie.get_upcoming_seances_json()
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

    release_date = db.Column(db.Date, nullable=True)

    tmdb_movie = None
    upcoming_seances = None

    allocine_rate_count_avg = {}
    imdb_rate_count_avg = {}

    def get_rate_count_svg_tab(self):

        if self.release_date not in Movie.allocine_rate_count_avg:
            Movie.allocine_rate_count_avg[self.release_date] = \
            Movie.query.filter_by(release_date=self.release_date).with_entities(
                func.avg(Movie.allocine_number_rate).label('average'))[0][0]

        if self.release_date not in Movie.imdb_rate_count_avg:
            Movie.imdb_rate_count_avg[self.release_date] = \
                Movie.query.filter_by(release_date=self.release_date).with_entities(
                    func.avg(Movie.imdb_number_rate).label('average'))[0][0]

        return {
            'allocine': Movie.allocine_rate_count_avg[self.release_date],
            'imdb': Movie.imdb_rate_count_avg[self.release_date],
        }

    def set_tmdb_movie(self, tmdb_movie):
        self.tmdb_movie = tmdb_movie

    def set_upcoming_seances(self, upcoming_seances):
        self.upcoming_seances = upcoming_seances

    def get_upcoming_seances_by_day(self):
        days = {}

        for seance in self.upcoming_seances:
            if seance.timestamp.date() not in days:
                days[seance.timestamp.date()] = [seance]
            else:
                days[seance.timestamp.date()].append(seance)

        return days

    def get_upcoming_seances_by_day_by_version(self):
        days = {}

        for seance in self.upcoming_seances:
            if seance.timestamp.date() not in days:
                days[seance.timestamp.date()] = {}
                if seance.get_version() not in days[seance.timestamp.date()]:
                    days[seance.timestamp.date()][seance.get_version()] = [seance]
                else:
                    days[seance.timestamp.date()][seance.get_version()].append(seance)
            else:
                if seance.get_version() not in days[seance.timestamp.date()]:
                    days[seance.timestamp.date()][seance.get_version()] = [seance]
                else:
                    days[seance.timestamp.date()][seance.get_version()].append(seance)

        return days

    def get_upcoming_seances_json(self):
        upcoming_seances = []

        for s in self.upcoming_seances:
            upcoming_seances.append(s.json_format())

        return upcoming_seances

    def get_rates(self):
        return {
            'imdb': {
                'rate': self.imdb_rate,
                'rates_count': self.imdb_number_rate,
                'max_rate': 10
            },
            'allocine': {
                'rate': self.allocine_rate,
                'rates_count': self.allocine_number_rate,
                'max_rate': 5
            },
        }

    def get_not_none_rates(self):
        rates = self.get_rates()
        res = {}

        for site in rates:
            res[site] = rates[site]
            if rates[site]['rate'] is None:
                res[site]['rate'] = 0
                res[site]['rates_count'] = 0

        return res

    def all_rates_are_none(self):
        rates = self.get_rates()
        for site in rates:
            if rates[site]['rate'] is not None:
                return False

        return True

    def get_external_ids(self):
        return {
            'imdb': ("https://www.imdb.com/title/tt" + str(self.imdb_id).zfill(
                7)) if self.imdb_id is not None else None,
            'allocine': ('http://www.allocine.fr/film/fichefilm_gen_cfilm=' + str(
                self.allocine_id) + '.html') if self.allocine_id is not None else None
        }

    def get_avg_number_rates(self, avg_significance):
        res = 0
        rates = self.get_not_none_rates()
        rates_avg = self.get_rate_count_svg_tab()

        for site in rates:
            res += (rates[site]['rates_count'] + rates_avg[site] * avg_significance)

        return res

    def score(self):
        rates = self.get_not_none_rates()
        avg_significance = 1/50

        if len(rates.keys()) == 0:
            return 0.

        rates_count_avg = self.get_rate_count_svg_tab()
        score = 0

        for site in rates:
            score += self.local_score(rates[site]['rate'], rates[site]['max_rate'], rates[site]['rates_count'],
                                      rates_count_avg[site] * avg_significance)
        score /= self.get_avg_number_rates(avg_significance)

        return round(score, 1)

    def local_score(self, rate, max_rate, number_rate, constante=0.5):
        return ((number_rate * rate / max_rate) + (0.5 * constante)) * 10

    @staticmethod
    def get_gaumont_movies(cine_id):
        cine = Cinema.get_cinema(cine_id)

        gaumont_movies = []

        for f in cine.get_films():

            # upcoming_seances = f.get_today_upcoming_seances(cine_id)
            upcoming_seances = f.get_upcoming_seances_of_the_week(cine_id)
            if len(upcoming_seances) > 0:

                # si on a déjà l'id dans la DB
                if Movie.query.filter_by(gaumont_id=f.id).count() > 0:
                    movie = Movie.query.filter_by(gaumont_id=f.id).first()
                    tmdb_movie = TmdbMovie.search_in_now_playing(movie.tmdb_id, nb_pages=5)
                    if tmdb_movie is None:
                        tmdb_movie = TmdbMovie.get_film(movie.tmdb_id)
                else:
                    tmdb_movie = TmdbMovie.search_film(f.name)
                    if tmdb_movie is None:
                        continue

                    allocine = {}
                    imdb = {}

                    allocine['id'], allocine['rate'], allocine['count'] = AllocineRate.call(tmdb_movie.original_title,
                                                                                            tmdb_movie.title)

                    imdb_id = tmdb_movie.get_external_ids()['imdb_id']
                    if imdb_id is None:
                        imdb['id'], imdb['rate'], imdb['count'] = None, None, None
                    else:
                        imdb['id'], imdb['rate'], imdb['count'] = ImdbRate.call(imdb_id[2:])

                    movie = Movie(gaumont_id=f.id, tmdb_id=tmdb_movie.id, imdb_id=imdb['id'],
                                  imdb_rate=imdb['rate'], imdb_number_rate=imdb['count'],
                                  allocine_id=allocine['id'], allocine_rate=allocine['rate'],
                                  allocine_number_rate=allocine['count'], release_date=tmdb_movie.french_release_date())

                    db.session.add(movie)
                    db.session.commit()

                movie.set_tmdb_movie(tmdb_movie)
                movie.set_upcoming_seances(upcoming_seances)

                gaumont_movies.append(movie)

        return gaumont_movies

    @staticmethod
    def get_today_movies(cine_id):
        today_movies = []
        gaumont_movies = Movie.get_gaumont_movies(cine_id)

        return gaumont_movies

        # for m in gaumont_movies:
        #    upcoming_seances = m.gaumont_movie.get_today_upcoming_seances(cine_id)
        #    if len(upcoming_seances) > 0:
        #        today_movies.append(m)

        # return today_movies

    @staticmethod
    def get_today_movies_order_by_score(cine_id, format=None):
        gaumont_movies = Movie.get_today_movies(cine_id)
        gaumont_movies = sorted(gaumont_movies, key=lambda x: x.score(), reverse=True)

        if format == 'api_json':
            return build_api_index_response(gaumont_movies)

        return gaumont_movies

    @staticmethod
    def get_tmdb_now_playing_movies(format=None, order=None):
        now_playing_movies = []
        thmdb_now_playing_movies = TmdbMovie.get_now_playing()

        for tmdb_movie in thmdb_now_playing_movies:
            if Movie.query.filter_by(tmdb_id=tmdb_movie.id).count() > 0:
                movie = Movie.query.filter_by(tmdb_id=tmdb_movie.id).first()
                movie.set_tmdb_movie(tmdb_movie)

                now_playing_movies.append(movie)

            else:
                allocine = {}
                imdb = {}

                allocine['id'], allocine['rate'], allocine['count'] = AllocineRate.call(tmdb_movie.original_title,
                                                                                        tmdb_movie.title)

                imdb_id = tmdb_movie.get_external_ids()['imdb_id'][2:]
                imdb['id'], imdb['rate'], imdb['count'] = ImdbRate.call(imdb_id)

                movie = Movie(gaumont_id=tmdb_movie.id, tmdb_id=tmdb_movie.id, imdb_id=imdb['id'],
                              imdb_rate=imdb['rate'], imdb_number_rate=imdb['count'],
                              allocine_id=allocine['id'], allocine_rate=allocine['rate'],
                              allocine_number_rate=allocine['count'])
                movie.set_tmdb_movie(tmdb_movie)

                db.session.add(movie)
                db.session.commit()

                now_playing_movies.append(movie)

        if order == 'score':
            now_playing_movies = sorted(now_playing_movies, key=lambda x: x.score(), reverse=True)

        if format == 'api_json':
            return build_api_index_response(now_playing_movies)

        return now_playing_movies

    @staticmethod
    def update_rates():
        for movie in Movie.query.filter(
                Movie.release_date >= (datetime.date.today() - datetime.timedelta(2 * 365 / 12))).order_by(
                Movie.release_date.desc(), Movie.date_created.desc()):
            allocine = {}
            imdb = {}

            if movie.release_date is None and movie.tmdb_id is not None:
                tmdb = TmdbMovie.get_film(movie.tmdb_id)
                movie.release_date = tmdb.french_release_date()

            allocine['id'], movie.allocine_rate, movie.allocine_number_rate = AllocineRate.get_rate(movie.allocine_id)
            imdb['id'], movie.imdb_rate, movie.imdb_number_rate = ImdbRate.get_rate(movie.imdb_id)
            db.session.commit()
            print(movie.id, 'mis à jour')
