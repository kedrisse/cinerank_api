import urllib.request

api_key = '32c2115b63d2b870f0f58d85da6a8183'


def open_link(link):
    with urllib.request.urlopen(link) as url:
        return url.read()