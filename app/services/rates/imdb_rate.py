from bs4 import BeautifulSoup
import urllib.request
import ssl
import json


def open_link(link):
    ssl._create_default_https_context = ssl._create_unverified_context
    with urllib.request.urlopen(link) as url:
        return url.read()


class ImdbRate:

    @staticmethod
    def call(imdb_id):
        if imdb_id[:2] == 'tt':
            imdb_id = imdb_id[2:]

        return ImdbRate.get_rate(imdb_id)

    @staticmethod
    def get_rate(imdb_id):

        if imdb_id is None:
            return None, None, None

        try:
            imdb_link = "https://www.imdb.com/title/tt" + str(imdb_id).zfill(7)
            imdb_page = BeautifulSoup(open_link(imdb_link), "html.parser")

            json_data = json.loads(imdb_page.find('script', type='application/ld+json').text)

            if 'aggregateRating' not in json_data:
                return imdb_id, None, None

            aggregate_rating = json_data['aggregateRating']
            imbd_rate = float(aggregate_rating['ratingValue'])
            imbd_rates_count = int(aggregate_rating['ratingCount'])

            return imdb_id, imbd_rate, imbd_rates_count

        except urllib.error.HTTPError:
            return imdb_id, None, None
