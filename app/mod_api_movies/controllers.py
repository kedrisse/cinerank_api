# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify
import json

# Import the database object from the main app module
from app import db

# Import module models (i.e. Movie)
from app.mod_api_movies.models import Movie

# Define the blueprint: 'auth', set its url prefix: app.url/auth
from app.services.gaumont.cinema import Cinema
from app.services.gaumont.film_gaumont import FilmGaumont

mod_api_movies = Blueprint('movies', __name__)


# Set the route and accepted methods
@mod_api_movies.route('/', methods=['GET'])
def choose_cinema():
    cinema_id = request.args.get('cinema_id')
    if cinema_id is not None:
        return redirect(url_for('movies.get_movies', cinema_id=cinema_id))

    return render_template('movies/choose_cine.html', cinemas=Cinema.get_cinemas())
    # return jsonify(Movie.get_today_movies_order_by_score(cinema_id, format='api_json'))


# Set the route and accepted methods
@mod_api_movies.route('/movies/<int:cinema_id>/', methods=['GET'])
def get_movies(cinema_id):
    return render_template('movies/index.html', cinema=Cinema.get_cinema(cinema_id), movies=Movie.get_today_movies_order_by_score(cinema_id))
    # return jsonify(Movie.get_today_movies_order_by_score(cinema_id, format='api_json'))


@mod_api_movies.route('/movies/refresh_rates/', methods=['GET'])
def refresh_rates():
    Movie.update_rates()

    return ''
