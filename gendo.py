import os
import redis
import yaml
import random
import re
import requests
from gendo import Gendo

path = os.path.dirname(os.path.abspath(__file__))
path_to_yaml = os.path.join(path, 'config.yaml')

with open(path_to_yaml, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

channel = cfg.get('gendo', {}).get('channel')
token = cfg.get('gendo', {}).get('auth_token')
gendo = Gendo(__name__, token, channel)

db = None


def setup_redis():
    global db
    db = redis.StrictRedis(host='localhost', port=6379, db=0)


@gendo.listen_for('cookies')
def cookies(user, message):
    return "I *LOVE* COOOOOOOOKIES!!!!"


@gendo.listen_for('morning')
def morning(user, message):
    return "mornin' @{0}".format(gendo.get_user_name(user))


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
        'safe': 'off'
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


@gendo.listen_for('sneaky fish count')
def sneaky_fish_counts(user, message):
    report = []
    if not get_total_sneaky_fishes():
        return "no sneaky fishes"
    for user_id, count in get_all_sneaky_fishes():
        suffix = ('' if count == 1 else 's')
        report.append("{0} has {1} accusation{2}.".format(
            gendo.get_user_name(user_id), int(count), suffix))
    return '```' + '\n'.join(report) + '```'


@gendo.listen_for('is a sneaky fish')
def sneaky_fish(user, message):
    fishes = re.findall('<\@([0-9A-Z]*)>', message)
    current_sneakiest_fish = get_sneakest_fish()

    if len(fishes) == 0:
        # a sneaky fish is required.
        return

    # unique fishes only
    fishes = set(fishes)
    for user_id in fishes:
        name = gendo.get_user_name(user_id)
        if get_count_for_user(user_id) == 0:
            gendo.speak("{0} is *now* a sneaky fish".format(name))
        set_sneaky_fish(user_id)

    user_id = get_sneakest_fish()
    if not current_sneakiest_fish:
        return "{0} is sneakiest fish".format(
            gendo.get_user_name(user_id))
    elif current_sneakiest_fish == user_id:
        return "{0} is _still_ the sneakiest fish".format(
            gendo.get_user_name(current_sneakiest_fish))
    else:
        return "{0} has become the sneakiest fish".format(
            gendo.get_user_name(user_id))


def set_sneaky_fish(user_id):
    db.zincrby("sneaky_fishes", user_id)


def get_count_for_user(user_id):
    res = db.zscore("sneaky_fishes", user_id)
    if not res:
        return 0
    return res


def get_all_sneaky_fishes():
    return db.zrevrangebyscore("sneaky_fishes", "+inf", "-inf",
                               withscores=True)


def get_total_sneaky_fishes():
    return db.zcount("sneaky_fishes", "-inf", "+inf")


def get_sneakest_fish():
    sneaky_fishes = get_all_sneaky_fishes()
    if sneaky_fishes:
        sneakest_fish, _ = sneaky_fishes[0]
        return sneakest_fish
    return None

if __name__ == '__main__':
    setup_redis()
    gendo.run()
