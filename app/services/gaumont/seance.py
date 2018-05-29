from datetime import datetime
import pytz
from tzlocal import get_localzone # $ pip install tzlocal

from app.services.gaumont.file_manager import FileManager


class Seance:

    json_specificites = None


    def __init__(self, id, timestamp, film_id, specificites):
        self.id = id
        self.timestamp = timestamp
        self.film_id = film_id
        self.specificites = specificites

    def local_timezone(self):
        return self.timestamp.astimezone(get_localzone())

    def __str__(self):
        return str(self.timestamp)+'\t'+str(self.film_id)

    def get_specificites(self):
        if Seance.json_specificites is None:
            Seance.json_specificites = FileManager.call("references", "https://api.cinemasgaumontpathe.com/film-cinema-reference/1")['specificites']

        spec = []
        for s in self.specificites:
            for j in Seance.json_specificites:
                if s == j['id']:
                    spec.append(j['n'])

        return spec