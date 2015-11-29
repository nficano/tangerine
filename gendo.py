import datetime
import os
import random
import re

import requests
from gendo import Gendo

path = os.path.dirname(os.path.abspath(__file__))
path_to_yaml = os.path.join(path, 'config.yaml')
gendo = Gendo.config_from_yaml(__name__, path_to_yaml)


@gendo.listen_for('cookies')
def cookies(user, message):
    return "I *LOVE* COOOOOOOOKIES!!!!"


@gendo.listen_for('welcome back buddy')
def welcome_back_buddy(user, message):
    return "thanks {username}"


@gendo.listen_for('morning')
def morning(user, message):
    # make sure message is morning and doesn't just contain it.
    if message.strip() == "morning":
        now = datetime.datetime.now()
        if now.time() < datetime.time(12):
            return "mornin' @{username}"


@gendo.listen_for('image me')
def image_me(user, message):
    matches = re.findall('image me(.*)', message)
    if not matches:
        return
    query = matches[0].strip()
    results = _search_google_images(query)
    if results:
        while True:
            image_url = _get_random_image(results)
            if _verify_image(image_url):
                return image_url


def _verify_image(url):
    resp = requests.get(url)
    is_working = resp.ok
    content_type = resp.headers.get('Content-Type', '')
    if is_working and 'image' in content_type:
        return True
    return False


def _search_google_images(query):
    results = []
    url = 'https://ajax.googleapis.com/ajax/services/search/images'
    params = {
        'v': '1.0',
        'q': query,
        'safe': gendo.settings.get('image_me', {}).get('safe_search', 'off')
    }
    if 'gif' in query:
        params['as_filetype'] = 'gif'
    resp = requests.get(url, params=params)
    if resp.ok:
        results = resp.json().get('responseData', {}).get('results', [])
    return results


def _get_random_image(results):
    min_int, max_int = (0, len(results) - 1)
    idx = random.randint(min_int, max_int)
    return results[idx].get('url')

if __name__ == '__main__':
    gendo.run()
