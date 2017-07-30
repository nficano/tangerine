"""
    google image me
    ~~~~~~~~~~~~~~~

    image me -- ask me for an image of anything

    # Sample usage:
    from gendo import Gendo
    import image_me as google

    gendo = Gendo('xoxb-your-key-here')

    @gendo.listen_for('image me')
    def image_me(user, message):
        query = message.replace('image me', '')
        return google.random_google_image_search(query)

    if __name__ == '__main__':
        gendo.run()
"""
import random

import requests

URL = 'https://www.googleapis.com/customsearch/v1'
CSE_KEY = ''
CSE_ID = ''


def google_image_search(query):
    resp = requests.get(URL, params={
        'v': '1.0', 'searchType': 'image', 'q': query.strip(),
        'cx': CSE_ID, 'key': CSE_KEY})
    if not resp.ok:
        yield
    for i in resp.json().get('items', []):
        yield i.get('link')


def random_google_image_search(query):
    if query:
        return random.choice([r for r in google_image_search(query)])


if __name__ == '__main__':
    print(random_google_image_search('nick ficano'))
