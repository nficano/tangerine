#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import inspect
import logging
import os
import sys
import time
from collections import namedtuple

import six
import yaml
from box import Box
from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import select_autoescape
from slackclient import SlackClient

from .scheduler import Task

log = logging.getLogger(__name__)

Listener = namedtuple(
    'Listener', (
        'rule',
        'view_func',
        'trigger',
        'doc',
        'options',
    ),
)


class Tangerine(object):
    jinja_environment = Environment

    def __init__(self, slack_token=None, settings=None):
        settings = settings or {}
        settings.setdefault('tangerine', {})
        settings['tangerine'].setdefault('sleep', 0.5)
        settings['tangerine'].setdefault('template_folder', 'templates')

        self.settings = Box(settings, frozen_box=True, default_box=True)
        self.listeners = []
        self.scheduled_tasks = []

        self.client = SlackClient(
            slack_token or self.settings.tangerine.auth_token,
        )
        self.sleep = self.settings.tangerine.sleep

    @classmethod
    def config_from_yaml(cls, path_to_yaml):
        with open(path_to_yaml, 'r') as ymlfile:
            settings = yaml.load(ymlfile)
            log.info('settings from %s loaded successfully', path_to_yaml)
            return cls(settings=settings)

    def _verify_rule(self, supplied_rule):
        """Rules must be callable with (user, message) in the signature.
        Strings are automatically converted to callables that match.
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
        """Decorator for adding a Rule. See guidelines for rules."""
        trigger = None
        if isinstance(rule, six.string_types):
            trigger = rule
        rule = self._verify_rule(rule)

        def decorator(f):
            self.add_listener(rule, f, trigger, f.__doc__, **options)
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
                log.info('attempting graceful shutdown...')
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
        if not data or data.type != 'message' or 'user' not in data:
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
        sendable = {
            'user': user,
            'message': message,
            'channel': channel,
        }
        if not message:
            return
        for rule, view_func, _, _, options in self.listeners:
            if rule(user, message):
                args = inspect.getargspec(view_func).args
                kwargs = {k: v for k, v in sendable.items() if k in args}
                response = view_func(**kwargs)
                if response:
                    if 'hide_typing' not in options:
                        # TODO(nficano): this should be configurable
                        time.sleep(.2)
                        self.client.server.send_to_websocket({
                            'type': 'typing',
                            'channel': channel,
                        })
                        time.sleep(.5)
                    if '{user.username}' in response:
                        response = response.replace(
                            '{user.username}',
                            self.get_user_name(user),
                        )
                    self.speak(response, channel)

    def add_listener(self, rule, view_func, trigger, docs, **options):
        """Adds a listener to the listeners container; verifies that
        `rule` and `view_func` are callable.
        """
        if not six.callable(rule):
            raise TypeError('rule should be callable')
        if not six.callable(view_func):
            raise TypeError('view_func should be callable')
        self.listeners.append(
            Listener(rule, view_func, trigger, docs, options),
        )

    def add_cron(self, schedule, f, **options):
        self.scheduled_tasks.append(Task(schedule, f, **options))

    def speak(self, message, channel, **kwargs):
        self.client.api_call(
            'chat.postMessage', as_user=True,
            channel=channel, text=message, **kwargs,
        )

    def get_user_info(self, user_id):
        return self.client.api_call('users.info', user=user_id)

    def get_user_name(self, user_id):
        user = self.get_user_info(user_id)
        return user.get('user', {}).get('name')

    def get_user_id_from_username(self, username):
        for m in self.client.api_call('users.list')['members']:
            if username.lower() == m.get('name', '').lower():
                return m['id']

    def get_channel_id_from_name(self, channel):
        channel = channel.lower().replace('#', '')
        types = ','.join(['public_channel', 'private_channel'])

        response = self.client.api_call(
            'conversations.list', types=types, limit=1000,
        )
        for c in response['channels']:
            if channel == c['name'].lower():
                return c['id']

        response = self.client.api_call('channels.list', limit=1000)
        for c in response['channels']:
            if channel == c['name'].lower():
                return c['id']

    def get_channel_name_from_channel_id(self, channel_id):
        types = ','.join(['public_channel', 'private_channel'])

        response = self.client.api_call(
            'conversations.list', types=types, limit=1000,
        )
        for c in response['channels']:
            if channel_id == c['id']:
                return c['name']

        response = self.client.api_call('channels.list', limit=1000)
        for c in response['channels']:
            if channel_id == c['id']:
                return c['name']

    def get_template_path(self):
        if os.path.isabs(self.settings.tangerine.template_folder):
            return self.settings.tangerine.template_folder
        else:
            return os.path.join(
                os.getcwd(),
                self.settings.tangerine.template_folder,
            )

    def get_jinja_environment(self):
        return self.jinja_environment(
            loader=FileSystemLoader(self.get_template_path()),
            autoescape=select_autoescape(['txt']),
        )

    def render_template(self, template_name, **context):
        env = self.get_jinja_environment()
        template = env.get_template(template_name)
        return template.render(**context)
