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

from time import localtime, tzset
from .storage import NewAction
from ..api.action import Action, ActionFactory, MergedAction
from ..api.event import Hello, Pong, PresenceChange

tzset()

class AwayAction(Action):
    def __init__(self, event, away):
        Action.__init__(self, event)
        self.away = away

    def handle(self, client, state):
        if not self.event or self.event.user == client.id():
            presence = 'away' if self.event else 'auto'
            client.api_call('users.setPresence', presence=presence)
            state['away'] = self.away

class Factory(ActionFactory):
    def create_action(self, event, state):
        if isinstance(event, (Hello, Pong)):
            away = state.get('away', True)
            time = localtime()
            if away is (8 <= time.tm_hour < 18 and time.tm_wday < 5):
                action = AwayAction(None, not away)
                if not away or time.tm_wday or 12 <= time.tm_hour:
                    return action
                return MergedAction.new(action, NewAction(event))
        elif isinstance(event, PresenceChange):
            away = state.get('away', True)
            if (event.presence == 'away') is not away:
                return AwayAction(event, not away)

Action.register_factory(Factory())
