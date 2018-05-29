# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify
import json

# Import the database object from the main app module
from app import db

# Import module models (i.e. Movie)
from app.mod_api_movies.models import Movie

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_api_movies = Blueprint('movies', __name__)


# Set the route and accepted methods
@mod_api_movies.route('/movies/', methods=['GET', 'POST'])
def get_movies():
    return jsonify(Movie.get_tmdb_now_playing_movies(format='api_json', order='score'))
