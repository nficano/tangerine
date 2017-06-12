#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
import json
import logging
import inspect
import datetime
import os
import sys
import time

from slackclient import SlackClient
from box import Box
from .scheduler import Task
import six
import yaml

log = logging.getLogger(__name__)

Listener = namedtuple('Listener', ('rule', 'view_func', 'options'))


class Gendo(object):
    def __init__(self, slack_token=None, settings=None):
        settings = settings or {}
        settings.setdefault('gendo', {})
        settings['gendo'].setdefault('sleep', 0.5)
        self.settings = Box(settings, frozen_box=True, default_box=True)
        self.listeners = []
        self.scheduled_tasks = []

        self.client = SlackClient(
            slack_token or self.settings.gendo.auth_token)
        self.sleep = self.settings.gendo.sleep

    @classmethod
    def config_from_yaml(cls, path_to_yaml):
        with open(path_to_yaml, 'r') as ymlfile:
            settings = yaml.load(ymlfile)
            log.info("settings from %s loaded successfully", path_to_yaml)
            return cls(settings=settings)

    def _verify_rule(self, supplied_rule):
        """Rules must be callable with (user, message) in the signature.
        Strings are automatically converted to callables that match.

        :returns: Callable rule function with user, message as signature.
        :raises ValueError: If `supplied_rule` is neither a string nor a
                            callable with the appropriate signature.
        """
        # If string, make a simple match callable
        if isinstance(supplied_rule, six.string_types):
            return lambda user, message: supplied_rule in message.lower()

        if not six.callable(supplied_rule):
            raise ValueError('Bot rules must be callable or strings')

        expected = ('user', 'message')
        signature = tuple(inspect.getargspec(supplied_rule).args)
        try:
            # Support class- and instance-methods where first arg is
            # something like `self` or `cls`.
            assert len(signature) in (2, 3)
            assert expected == signature or expected == signature[-2:]
        except AssertionError:
            msg = 'Rule signuture must have only 2 arguments: user, message'
            raise ValueError(msg)

        return supplied_rule

    def listen_for(self, rule, **options):
        """Decorator for adding a Rule. See guidelines for rules.
        """
        rule = self._verify_rule(rule)

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
        self.running = True
        if self.client.rtm_connect():
            try:
                self.event_loop()
            except (KeyboardInterrupt, SystemExit):
                log.info("attempting graceful shutdown...")
                self.running = False
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

    def event_loop(self):
        while self.running:
            time.sleep(self.sleep)
            self.process_stream()
            self.process_scheduled_tasks()

    def read_stream(self):
        data = self.client.rtm_read()
        if not data:
            return data
        return [Box(d) for d in data][0]

    def process_stream(self):
        data = self.read_stream()
        if not data or data.type != 'message':
            return
        self.respond(data.user, data.text, data.channel)

    def process_scheduled_tasks(self):
        now = datetime.datetime.now()
        for idx, task in enumerate(self.scheduled_tasks):
            if now > task.next_run:
                t = self.scheduled_tasks.pop(idx)
                t.run()
                self.add_cron(t.schedule, t.fn, **t.options)

    def respond(self, user, message, channel):
        if not message:
            return
        for rule, view_func, options in self.listeners:
            if rule(user, message):
                response = view_func(user, message, **options)
                if response:
                    if '{user.username}' in response:
                        response = response.replace('{user.username}',
                                                    self.get_user_name(user))
                    self.speak(response, channel)

    def add_listener(self, rule, view_func, **options):
        """Adds a listener to the listeners container; verifies that
        `rule` and `view_func` are callable.

        :raises TypeError: if rule is not callable.
        :raises TypeError: if view_func is not callable
        """
        if not six.callable(rule):
            raise TypeError('rule should be callable')
        if not six.callable(view_func):
            raise TypeError('view_func should be callable')
        self.listeners.append(Listener(rule, view_func, options))

    def add_cron(self, schedule, f, **options):
        self.scheduled_tasks.append(Task(schedule, f, **options))

    def speak(self, message, channel):
        self.client.api_call("chat.postMessage", as_user="true:",
                             channel=channel, text=message)

    def get_user_info(self, user_id):
        return self.client.api_call('users.info', user=user_id)

    def get_user_name(self, user_id):
        user = self.get_user_info(user_id)
        return user.get('user', {}).get('name')
