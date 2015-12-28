#!/usr/bin/env/python
# -*- coding: utf-8 -*-
import json
import logging
import datetime
import os
import sys
import time

from slackclient import SlackClient
from scheduler import Task
from . import __version__
import yaml

log = logging.getLogger(__name__)


class Gendo(object):
    def __init__(self, slack_token=None, settings=None):
        self.settings = settings or {}
        self.listeners = []
        self.scheduled_tasks = []
        self.client = SlackClient(
            slack_token or self.settings.get('gendo', {}).get('auth_token'))
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
        running = True
        if self.client.rtm_connect():
            while running:
                time.sleep(self.sleep)
                now = datetime.datetime.now()
                try:
                    data = self.client.rtm_read()
                    if data and data[0].get('type') == 'message':
                        user = data[0].get('user')
                        message = data[0].get('text')
                        channel = data[0].get('channel')
                        self.respond(user, message, channel)

                    for idx, task in enumerate(self.scheduled_tasks):
                        if now > task.next_run:
                            t = self.scheduled_tasks.pop(idx)
                            t.run()
                            self.add_cron(t.schedule, t.fn, **t.options)
                except (KeyboardInterrupt, SystemExit):
                    log.info("attempting graceful shutdown...")
                    running = False
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

    def respond(self, user, message, channel):
        if not message:
            return
        elif message == 'gendo version':
            self.speak("Gendo v{0}".format(__version__))
            return
        for phrase, view_func, options in self.listeners:
            if phrase in message.lower():
                response = view_func(user, message, **options)
                if response:
                    if '{user.username}' in response:
                        response = response.replace('{user.username}',
                                                    self.get_user_name(user))
                    self.speak(response, channel)

    def add_listener(self, rule, view_func=None, **options):
        self.listeners.append((rule, view_func, options))

    def add_cron(self, schedule, f, **options):
        self.scheduled_tasks.append(Task(schedule, f, **options))

    def speak(self, message, channel):
        self.client.api_call("chat.postMessage", as_user="true:",
                             channel=channel, text=message)

    def get_user_info(self, user_id):
        user = self.client.api_call('users.info', user=user_id)
        return json.loads(user)

    def get_user_name(self, user_id):
        user = self.get_user_info(user_id)
        return user.get('user', {}).get('name')
