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

import re
from .conversation import HelpAction
from ..api.action import Action, ActionFactory
from ..api.event import Message

"""
    < @bot
    > Hello, I am @@.
    > I am here to match you with a different person every week for having lunch.
    > Please talk to me if you require any help.
"""

def user_mentioned(message, id):
    return bool(re.search('<@' + id + '>', message))

class IntroAction(Action):
    def handle(self, client, state):
        # if channel
        if user_mentioned(self.event.text, client.id()):
            messages = [
                "Hello <@" + self.event.user + ">, I am " + client.real_name() + ".",
                "I am here to match you with a different person every week for having lunch."
            ]
            action = None
            if "help" in self.event.text:
                action = HelpAction(self.event, True)
            else:
                messages.append("Please talk to me if you require any help.")
            client.send_message(self.event.channel, *messages)
            return action

class Factory(ActionFactory):
    def create_action(self, event, state):
        if isinstance(event, Message) and '@' in event.text:
            return IntroAction(event)

Action.register_factory(Factory())
