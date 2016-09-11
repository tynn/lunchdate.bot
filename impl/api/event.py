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
from logging import debug

def model_name_for_type(name):
    return ''.join(map(lambda u: u.capitalize(), name.split('_')))

class Event(object):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def new(event):
        try:
            key = 'subtype' if 'subtype' in event else 'type'
            name = model_name_for_type(event[key])
            cls = globals()[name]
            return cls(**event)
        except Exception as e:
            debug(e)

class Hello(Event):
    pass

class Message(Event):
    def __init__(self, text, channel, user, ts, **kwargs):
        self.text = text
        self.channel = channel
        self.user = user
        self.ts = ts

class MessageChanged(Message):
    def __init__(self, message, channel, **kwargs):
        Message.__init__(self, channel=channel, **message)

class Pong(Event):
    pass

class PresenceChange(Event):
    def __init__(self, presence, user, **kwargs):
        self.presence = presence
        self.user = user

class User(Event):
    def __init__(self, name, **kwargs):
        self.name = name

class Notify(Event):
    def __init__(self, single, *pairs):
        self.single = single
        self.pairs = pairs
