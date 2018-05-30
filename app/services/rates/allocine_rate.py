import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
from difflib import SequenceMatcher


def open_link(link):
    with urllib.request.urlopen(link) as url:
        return url.read()


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio() > 0.8


class AllocineRate:

    @staticmethod
    def call(original_name, local_name):
        allocine_query = original_name
        search_link = 'http://www.allocine.fr/recherche/?q=' + urllib.parse.quote_plus(allocine_query)

        content = open_link(search_link)
        page = BeautifulSoup(content, "html.parser")
        movie_link = None

        table = page.select('table.totalwidth.noborder.purehtml')
        if len(table) == 0:
            return None, None, None
        table = table[0]
        links = table.select('tr td.totalwidth a')

        trouve = False
        i = 0

        if len(links) == 0:
            return None, None, None

        while (not trouve) and i < len(links):
            movie_name = links[i].text
            movie_link = links[i]['href']
            trouve = similar(movie_name, original_name) or similar(movie_name, local_name)
            i += 1

        if movie_link is None:
            return None, None, None

        allocine_id = movie_link[26:][:-5]

        return AllocineRate.get_rate(allocine_id)

    @staticmethod
    def get_rate(allocine_id):

        if allocine_id is None:
            return None, None, None

        movie_link = 'http://www.allocine.fr/film/fichefilm_gen_cfilm=' + str(allocine_id) + '.html'
        page = BeautifulSoup(open_link(movie_link), "html.parser")
        aggregate_rating = page.select('div[itemprop="aggregateRating"]')
        if len(aggregate_rating) == 0:
            return allocine_id, None, None

        rating_value = aggregate_rating[0].select('span[itemprop="ratingValue"]')
        if len(rating_value) == 0:
            return allocine_id, None, None

        public_rate = rating_value[0]['content']
        public_rate = float(public_rate.replace(',', '.'))

        rating_count = aggregate_rating[0].select('span[itemprop="ratingCount"]')
        if len(rating_count) == 0:
            return allocine_id, public_rate, None

        allocine_rates_count = int(rating_count[0].text)

        return allocine_id, public_rate, allocine_rates_count
