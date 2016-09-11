# vim: expandtab tabstop=4 shiftwidth=4
#
#  Copyright (c) 2016 Christian Schmitz <tynn.dev@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from logging import debug, error
from time import sleep, time
from slackclient import SlackClient as _SlackClient
from .api.action import Action
from .api.event import Event

class SlackBot(object):
    def __init__(self):
        self.loop = EventLoop()

    def start(self, resource):
        client = SlackClient(self.get_token(resource))
        while self.loop:
            self.start_loop(client)

    def start_loop(self, client):
        try:
            if client.rtm_connect():
                self.loop.start(client)
        except KeyboardInterrupt:
            print('')
        except Exception as e:
            return error(e, exc_info=True)
        del self.loop

    def get_token(self, resource):
        if isinstance(resource, dict):
            return resource['resource']['SlackBotAccessToken']
        return resource

    def stop(self, resource=None):
        self.loop.stop()

class SlackClient(_SlackClient):
    def __init__(self, *args, **kwargs):
        _SlackClient.__init__(self, *args, **kwargs)

    def id(self):
        return self.server.login_data['self']['id']

    def name(self):
        return self.server.username

    def real_name(self):
        name = self.server.username
        for user in self.server.login_data['users']:
            if user['name'] == name:
                return user['real_name']
        return name

    def send_message(self, channel, *messages):
        if isinstance(channel, dict):
            channel = channel['id']
        messages = filter(None, messages)
        self.rtm_send_message(channel, '\n'.join(messages))


class EventLoop(object):
    def __init__(self):
        self.state = {}
        self.queue = []
        self.ping = 0
        self.sleep = 0.5
        self.running = False

    def start(self, client):
        self.running = True
        while self.running:
            self.do_events(client)
            self.do_action(client)
            sleep(self.sleep)

    def do_events(self, client):
        events = client.rtm_read()
        if self.handle_events(client, events):
            self.ping = int(time()) + 10
        elif int(time()) > self.ping:
            client.server.ping()

    def handle_events(self, client, events):
        if not events:
            return False
        for event in events:
            action = Action.new(Event.new(event), self.state)
            self.handle_action(client, action)
        return True

    def do_action(self, client):
        self.queue = list(filter(None, self.queue))
        if self.queue:
            self.handle_action(client, self.queue.pop(0))

    def handle_action(self, client, action):
        try:
            if action:
                self.queue.append(action.handle(client, self.state))
        except Exception as e:
            debug(e, exc_info=True)

    def stop(self):
        self.running = False

