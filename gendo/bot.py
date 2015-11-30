import json
import logging
import os
import sys
import time

from slackclient import SlackClient
from . import __version__
import yaml

log = logging.getLogger(__name__)


class Gendo(object):
    def __init__(self, slack_token=None, channel=None, settings=None):
        self.settings = settings or {}
        self.listeners = []
        self.scheduled_tasks = []
        self.client = SlackClient(
            slack_token or self.settings.get('gendo', {}).get('auth_token'))
        self.channel = channel or self.settings.get('gendo', {}).get('channel')
        self.sleep = 0.5 or self.settings.get('gendo', {}).get('sleep')

    @classmethod
    def config_from_yaml(cls, path_to_yaml):
        with open(path_to_yaml, 'r') as ymlfile:
            settings = yaml.load(ymlfile)
            return cls(settings=settings)

    def listen_for(self, rule, **options):
        def decorator(f):
            self.add_listener(rule, f, **options)
            return f
        return decorator

    def cron(self, schedule, **options):
        def decorator(f):
            self.add_cron(schedule, f, **options)
            return f
        return decorator

    def run(self):
        if self.client.rtm_connect():
            while True:
                time.sleep(self.sleep)
                try:
                    data = self.client.rtm_read()
                    if data and data[0].get('type') == 'message':
                        user = data[0].get('user')
                        message = data[0].get('text')
                        self.respond(user, message)
                except (KeyboardInterrupt, SystemExit):
                    print "attempting graceful shutdown..."
                    try:
                        sys.exit(0)
                    except SystemExit:
                        os._exit(0)

    def respond(self, user, message):
        if not message:
            return
        elif message == 'gendo version':
            self.speak("Gendo v{0}".format(__version__))
            return
        for phrase, view_func, options in self.listeners:
            if phrase in message.lower():
                response = view_func(user, message, **options)
                if response:
                    if '{username}' in response:
                        response = response.replace('{username}',
                                                    self.get_user_name(user))
                    self.speak(response)

    def add_listener(self, rule, view_func=None, **options):
        self.listeners.append((rule, view_func, options))

    def add_listener(self, schedule, view_func=None, **options):
        self.scheduled_tasks.append((schedule, view_func, options))

    def speak(self, message):
        self.client.api_call("chat.postMessage", as_user="true:",
                             channel=self.channel, text=message)

    def get_user_info(self, user_id):
        user = self.client.api_call('users.info', user=user_id)
        return json.loads(user)

    def get_user_name(self, user_id):
        user = self.get_user_info(user_id)
        return user.get('user', {}).get('name')
