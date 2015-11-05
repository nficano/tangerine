import logging
import json
from slackclient import SlackClient

from .helpers import _PackageBoundObject

log = logging.getLogger(__name__)


class Gendo(_PackageBoundObject):
    def __init__(self, import_name, slack_token, channel):
        _PackageBoundObject.__init__(self, import_name)
        self.listeners = []
        self.client = SlackClient(slack_token)
        self.channel = channel
        self.sleep = 0.5

    def listen_for(self, rule, **options):
        def decorator(f):
            self.add_listener(rule, f, **options)
            return f
        return decorator

    def run(self):
        if self.client.rtm_connect():
            while True:
                try:
                    data = self.client.rtm_read()
                    if data and data[0].get('type') == 'message':
                        print data[0].get('text')
                        self.respond(data[0].get('text'))
                except (KeyboardInterrupt, SystemExit):
                    print "Shutting down..."
                    break

    def respond(self, message):
        for phrase, view_func, options in self.listeners:
            if phrase in message.lower():
                response = view_func(message, **options)
                if response:
                    self.speak(response)

    def add_listener(self, rule, view_func=None, **options):
        self.listeners.append((rule, view_func, options))

    def speak(self, message):
        self.client.api_call("chat.postMessage", as_user="true:",
                             channel=self.channel, text=message)

    def get_user_info(self, user_id):
        user = self.client.api_call('users.info', user=user_id)
        return json.loads(user)

    def get_user_name(self, user_id):
        user = self.get_user_info(user_id)
        return user.get('user', {}).get('name')
