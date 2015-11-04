# -*- coding: utf-8 -*-
import random
import re
import requests
import time
import json
import operator
from collections import Counter
from slackclient import SlackClient

sneaky_fish_count = Counter()
client = None
channel = "#general"
token = "xxxx-xxxx-xxx-xxxxx-xxx-xxxx"


def setup_slack_client():
    global client
    client = SlackClient(token)


def loop():
    if client.rtm_connect():
        while True:
            time.sleep(0.5)
            data = client.rtm_read()
            try:
                if data and data[0].get('type') == 'message':
                    text = data[0].get('text')
                    watch_for(text, 'cookies', "I *LOVE* COOOOOOOOKIES!!!!")
                    watch_for(text, 'image me', image_me)
                    watch_for(text, 'sneaky fish', sneaky_fish)
                    watch_for(text, 'sneaky fish counts', sneaky_fish_counts)
            except Exception as e:
                print e


def watch_for(what, phrase, reply):
    if phrase and phrase in what:
        if isinstance(reply, basestring):
            speak(reply)
        else:
            reply(what)


def speak(message):
    client.api_call("chat.postMessage",
                    as_user="true:",
                    channel=channel,
                    text=message)


def sneaky_fish_counts(message):
    if len(sneaky_fish_count) == 0:
        speak("no sneaky fishes")
    else:
        for k, v in sneaky_fish_count.items():
            if v == 1:
                speak("{0} has {1} accusation.".format(k, v))
            else:
                speak("{0} has {1} accusations.".format(k, v))


def sneaky_fish(message):
    fishes = re.findall('<\@([0-9A-Z]*)>', message)
    if len(sneaky_fish_count) == 0:
        current_sneakiest_fish = None
    else:
        current_sneakiest_fish = max(sneaky_fish_count.iteritems(),
                                     key=operator.itemgetter(1))[0]
    if len(fishes) == 0:
        # a sneaky fish is required.
        return

    # unique fishes only
    fishes = set(fishes)
    for user_id in fishes:
        user = client.api_call('users.info', user=user_id)
        user = json.loads(user)
        name = user.get('user', {}).get('name')
        if sneaky_fish_count[name] == 0:
            speak("@{0} is *now* a sneaky fish".format(name))
        sneaky_fish_count[name] += 1

    sneakiest_fish = max(sneaky_fish_count.iteritems(),
                         key=operator.itemgetter(1))[0]
    if not current_sneakiest_fish:
        speak("@{0} is sneakiest fish".format(sneakiest_fish))
    elif current_sneakiest_fish == sneakiest_fish:
        speak("@{0} is _still_ the sneakiest fish".format(sneakiest_fish))
    else:
        speak("@{0} has become the sneakiest fish".format(sneakiest_fish))


def image_me(message):
    matches = re.findall('image me(.*)', message)
    if not matches:
        return
    message = matches[0].strip()
    url = 'https://ajax.googleapis.com/ajax/services/search/images'
    resp = requests.get(url, params={'v': '1.0', 'q': message})
    if resp.ok:
        results = resp.json().get('responseData', {}).get('results', [])
        if results:
            min_int, max_int = (0, len(results) - 1)
            idx = random.randint(min_int, max_int)
            speak(results[idx].get('url'))


if __name__ == '__main__':
    setup_slack_client()
    loop()
