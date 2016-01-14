#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests
from pyfieri.guy_fieri import speak
from datetime import date, datetime, timedelta
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


@gendo.listen_for('appetizers')
def appetizers(user, message):
    return speak()


@gendo.cron('0 15 * * *')
def quote_of_the_day():
    """Quote of the day"""
    url = 'http://api.theysaidso.com/qod.json'
    resp = requests.get(url)
    if not resp.ok:
        return
    quote = resp.json().get('contents', {}).get('quotes', [])[0]
    gendo.speak('> {quote} - {author}'.format(**quote), "#outlandish")

if __name__ == '__main__':
    gendo.run()


@gendo.listen_for('swing count')
def swing_count():
    today = date.today()
    now = datetime.now()

    start_of_day = now.replace(hour=9, minute=30)
    end_date = date(2016, 1, 30)
    time_remaining = timedelta(days=0)

    d = today
    while d <= end_date:
        day_of_week = d.weekday()
        if day_of_week < 5:
            num_hours = 12
        elif day_of_week == 5:
            num_hours = 4
        else:
            num_hours = 0
        if d == today:
            end_of_day = start_of_day + timedelta(hours=num_hours)
            if now < end_of_day:
                time_remaining += end_of_day - max(now, start_of_day)
        else:
            time_remaining += timedelta(hours=num_hours)
        d += timedelta(days=1)

    if time_remaining:
        hours = (time_remaining.days * 24) + (time_remaining.seconds / 3600)
        minutes = (time_remaining.seconds % 3600) / 60
        return "There are %s hours and %s minutes of Swing left." % (
            hours, minutes)
    return "Swing is over!"
