# Import flask and template operators
from flask import Flask, render_template
from flask_cors import CORS
from flask_scss import Scss
import locale

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Define the WSGI application object
app = Flask(__name__)
CORS(app)
Scss(app)

# Configurations
app.config.from_object('config')

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


# Import a module / component using its blueprint handler variable (mod_auth)
from app.mod_api_movies.controllers import mod_api_movies

# Register blueprint(s)
app.register_blueprint(mod_api_movies)

# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()
