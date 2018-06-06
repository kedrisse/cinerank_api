from datetime import datetime
import pytz
from tzlocal import get_localzone # $ pip install tzlocal

from app.services.gaumont.file_manager import FileManager


class Seance:

    json_specificites = None
    json_versions = None
    json_ref = None

    def __init__(self, id, timestamp, film_id, specificites, version):
        self.id = id
        self.timestamp = timestamp
        self.film_id = film_id
        self.specificites = specificites
        self.version = version

    def local_timezone(self):
        tz = pytz.timezone('Europe/Paris')
        return self.timestamp.astimezone(tz)

    def __str__(self):
        return str(self.timestamp)+'\t'+str(self.film_id)

    def get_specificites(self):
        if Seance.json_ref is None:
            Seance.json_ref = FileManager.call("references", "https://api.cinemasgaumontpathe.com/film-cinema-reference/1")

        if Seance.json_specificites is None:
            Seance.json_specificites = Seance.json_ref['specificites']

        spec = []
        for s in self.specificites:
            for j in Seance.json_specificites:
                if s == j['id']:
                    spec.append(j['n'])

        return spec

    def get_version(self):
        if Seance.json_ref is None:
            Seance.json_ref = FileManager.call("references", "https://api.cinemasgaumontpathe.com/film-cinema-reference/1")

        if Seance.json_versions is None:
            Seance.json_versions = Seance.json_ref['versions']

        return Seance.json_versions[self.version-1]['n']

    def json_format(self):
        return {
            'id': self.id,
            'timestamps': self.timestamp,
            'specificites': self.specificites
        }