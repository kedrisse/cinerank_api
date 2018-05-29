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
@mod_api_movies.route('/movies/<int:cinema_id>/', methods=['GET', 'POST'])
def get_movies(cinema_id):

    return jsonify(Movie.get_today_movies_order_by_score(cinema_id, format='api_json'))
