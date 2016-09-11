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

class ActionFactory(object):
    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        cls = type(self)
        return hash(cls.__module__ + '.' + cls.__name__)

    def create_action(self, event, state):
        raise NotImplementedError()

class Action(object):
    factories = set()

    @staticmethod
    def register_factory(factory):
        Action.factories.add(factory)

    @staticmethod
    def new(event, state):
        actions = []
        for factory in Action.factories:
            actions.append(factory.create_action(event, state))
        return MergedAction.new(*actions)

    def __init__(self, event):
        self.event = event

    def handle(self, client, state):
        raise NotImplementedError()

class MergedAction(Action):
    @staticmethod
    def new(*actions):
        actions = list(filter(None, actions))
        if not actions:
            return None
        elif len(actions) == 1:
            return actions[0]
        else:
            return MergedAction(*actions)

    def __init__(self, *actions):
        self.actions = actions

    def handle(self, client, state):
        actions = []
        for action in self.actions:
            try:
                if action:
                    actions.append(action.handle(client, state))
            except Exception as e:
                debug(e, exc_info=True)
        return MergedAction(*actions)

class Reaction(Action):
    def __init__(self, event, reaction):
        Action.__init__(self, event)
        self.reaction = reaction

    def handle(self, client, state):
        client.server.api_call('reactions.add', name=self.reaction,
                channel=self.event.channel, timestamp=self.event.ts)

