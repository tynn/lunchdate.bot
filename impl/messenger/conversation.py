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
from ..api.action import Action, ActionFactory, MergedAction
from ..api.event import Message
from .storage import current_week, update_attendance

"""
    < help
    < can|cannot|can't|not make this|next [23]|two|three weeks?

    < show me this week
    < match lunch dates

    > There is no date for you this week.
    > I told the others, maybe we will find one for you anyhow.
"""

MENTION = re.compile(r'<@([0-9A-Z]+)>')
ONLY_A_BOT = "I am only a bot and thus not able to engage in a deep conversation."

class ConversationAction(Action):
    def open_channel(self, client, user):
        return client.api_call('im.open', user=user)['channel']['id']

    def is_self(self, client):
        return self.event.user == client.id()

    def is_private(self, client):
        return client.api_call('im.history', channel=self.event.channel)['ok']

    def is_admin(self, client):
        for user in client.server.login_data['users']:
            if user['id'] == self.event.user:
                return user['is_admin']

    def is_conversation(self, client):
        return not self.is_self(client) and self.is_private(client)

class BotAction(ConversationAction):
    def handle(self, client, state):
        if self.event.user != client.id() and self.is_private(client):
            client.send_message(self.event.channel, ONLY_A_BOT)

class HelpAction(ConversationAction):
    def __init__(self, event, force=False):
        ConversationAction.__init__(self, event)
        self.force = force

    def handle(self, client, state):
        if self.force or self.is_private(client):
            client.send_message(self.event.channel,
                "You can ask me for help anytime, but you already know that.",
                "Also you should tell me if you cannot make it this or the next one to three weeks.",
                "If for some reason you can make it this week again, you should mention it to me too.",
                 *self.admin_info(client))

    def admin_info(self, client):
        messages = []
        if self.is_admin(client) and self.is_private(client):
            messages.extend([
                "Since you are an admin I can give you even more information.",
                "You can ask me to show you this weeks matchings or to update these with new team members.",
                "Also you can say if somebody can or cannot make it sometime, like you do it for yourself."
            ])
        messages.append("And always remember " + ONLY_A_BOT)
        return messages

class SingleAction(ConversationAction):
    def handle(self, client, state):
        client.send_message(self.open_channel(client, self.event),
                "There is no date for you this week.",
                "I told the others, maybe we will find one for you anyhow.")

class PlanningAction(ConversationAction):
    def __init__(self, event, match):
        ConversationAction.__init__(self, event)
        self.start = match.start()
        self.match = match.groups()

    def handle(self, client, state):
        if self.is_self(client) or not self.is_private(client):
            return
        client.send_message(self.event.channel,
                "I will keep this in mind, thank you.")
        att = self.match[0]
        att = att is None or att == "can "
        span = self.number(self.match[3])
        span = span if span is not None else 0 if self.match[2] == "this" else 1
        users = [self.event.user]
        if self.is_admin(client):
            user_id = True
            while user_id:
                start = 0 if user_id is True else user_id.end()
                if start:
                    users.append(user_id.groups()[0])
                user_id = MENTION.search(self.event.text, start, self.start)
            if len(users) > 1:
                del users[0]
        actions = map(lambda u: update_attendance(u, att, span, state), users)
        return MergedAction.new(*actions)

    def number(self, value):
        if value is None:
            return
        if value == " two":
            return 2
        if value == " three":
            return 3
        return int(value)

class AdminInfoAction(ConversationAction):
    def handle(self, client, state):
        if self.is_admin(client) and self.is_conversation(client):
            client.send_message(self.event.channel, str(current_week(state)))

class AdminMatchAction(ConversationAction):
    def handle(self, client, state):
        if self.is_admin(client) and self.is_conversation(client):
            week = current_week(state)
            client.send_message(self.event.channel,
                            "Ok, I will update the matching now.")
            return Action.new(week, state)

class Factory(ActionFactory):
    PLANNING = re.compile(r'(can |cannot |can.?t |not )?make ([a-z]+ )*(this|next( [23]| two| three)?) weeks?')
    ADMIN_INFO = re.compile(r'show me this weeks?( data| info| information| matchings)?[.!]?')
    ADMIN_MATCH = re.compile(r'match( the)? lunch dates( now)?[.!]?')

    def create_action(self, event, state):
        if not isinstance(event, Message):
            return
        text = event.text.lower()
        words = self.PLANNING.search(text)
        if words:
            return PlanningAction(event, words)
        if self.ADMIN_INFO.search(text):
            return AdminInfoAction(event)
        if self.ADMIN_MATCH.search(text):
            return AdminMatchAction(event)
        if "help" in text:
            return HelpAction(event)
        return BotAction(event)

Action.register_factory(Factory())
