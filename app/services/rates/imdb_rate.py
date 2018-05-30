from bs4 import BeautifulSoup
import urllib.request
import ssl


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
            imdb_link = "https://www.imdb.com/title/tt" + str(imdb_id)
            imdb_page = BeautifulSoup(open_link(imdb_link), "html.parser")

            aggregate_rating = imdb_page.select('div[itemprop="aggregateRating"]')
            if len(aggregate_rating) == 0:
                return imdb_id, None, None

            rating_value = aggregate_rating[0].select('span[itemprop="ratingValue"]')
            if len(rating_value) == 0:
                return imdb_id, None, None

            imbd_rate = rating_value[0].text
            imbd_rate = float(imbd_rate.replace(',', '.'))

            rating_count = aggregate_rating[0].select('span[itemprop="ratingCount"]')
            if len(rating_count) == 0:
                return imdb_id, imbd_rate, None

            imbd_rates_count = rating_count[0].text
            imbd_rates_count = imbd_rates_count.replace(' ', '')
            imbd_rates_count = int(imbd_rates_count.replace(',', ''))

            return imdb_id, imbd_rate, imbd_rates_count

        except urllib.error.HTTPError:
            return imdb_id, None, None
