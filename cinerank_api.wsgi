#!/var/www/cinerank_api/venv/bin/python

activate_this = '/var/www/cinerank_api/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))


import sys
import logging

print(sys.version)

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/cinerank_api/")

from app import app as application
#application.secret_key = 'Add your secret key'
