#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests
from gendo import Gendo

path = os.path.dirname(os.path.abspath(__file__))
path_to_yaml = os.path.join(path, 'config.yaml')
gendo = Gendo.config_from_yaml(path_to_yaml)


@gendo.listen_for('cookies')
def cookies(user, message):
    return "I *LOVE* COOOOOOOOKIES!!!!"


@gendo.listen_for('morning')
def morning(user, message):
    # make sure message is "morning" and doesn't just contain it.
    if message.strip() == "morning":
        return "mornin' @{user.username}"


@gendo.cron('0 15 * * *')
def quote_of_the_day():
    """Quote of the day"""
    url = 'http://api.theysaidso.com/qod.json'
    resp = requests.get(url)
    if not resp.ok:
        return
    quote = resp.json().get('contents', {}).get('quotes', [])[0]
    gendo.speak('{quote} - {author}'.format(**quote), "#outlandish")

if __name__ == '__main__':
    gendo.run()
