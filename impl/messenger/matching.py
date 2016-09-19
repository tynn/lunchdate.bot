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

from collections import Counter
from networkx import Graph, maximal_matching
from .conversation import SingleAction
from .storage import WeekData, find_paired, SLACKBOT
from ..api.action import Action, ActionFactory, MergedAction
from ..api.event import Message, Notify

"""
    > This week you two will have lunch together.
    > Please find a date yourself and enjoy your lunch.

    > Someone has no date yet. You can help and invite @ for a lunch of three.
"""

class P(tuple):
    def __new__(cls, *v):
        if len(v) == 1:
            v = v[0]
        return tuple.__new__(cls, set(v[:2]))

class MatchAction(Action):
    def handle(self, client, state):
        week = self.event
        users = client.api_call('users.list')['members']
        users = filter(lambda m: not m.get('is_bot', False), users)
        users = set(map(lambda m: m['id'], users)) - {SLACKBOT}
        users -= {m for m in week.ignore if week.ignore[m] >= 0}
        users -= set(sum(week.pairs, ()))
        if not users:
            return
        paired = Counter(map(P, find_paired(state)))
        pairs, single = self.match(users, paired, set(week.pairs))
        pairs -= set(week.pairs)
        week.pairs.extend(pairs)
        if single:
            week.single.clear()
            week.single.add(single)
        return MergedAction.new(week.write(), NotifyAction(pairs, single))

    def match(self, users, paired, pairs):
        all_pairs = {P(l, r) for l in users for r in users if l != r}
        pairs.update(maximal_matching(Graph(list(all_pairs - set(paired)))))
        users -= set(sum(pairs, ()))
        if not users:
            return pairs, None
        if len(users) == 1:
            return pairs, users.pop()
        return self.match(users, paired - Counter(list(paired)), pairs)

class NotifyAction(Action):
    def __init__(self, pairs, single=None):
        self.pairs = pairs
        self.single = single

    def handle(self, client, state):
        return MergedAction(*map(self.create_action, self.pairs))

    def create_action(self, pair):
        action = DateSetAction(pair)
        if not self.single:
            return action
        return MergedAction.new(action, NoDateAction(self.single, pair))

class DateSetAction(Action):
    def __init__(self, users):
        self.users = ','.join(users)

    def handle(self, client, state):
        client.send_message(self.open_channel(client),
	            "This week you two will have lunch together.",
	            "Please find a date yourself and enjoy your lunch.")

    def open_channel(self, client):
        return client.api_call('mpim.open', users=self.users)['group']['id']

class CancelAction(DateSetAction):
    def handle(self, client, state):
        client.send_message(self.open_channel(client),
	            "Ohh, something did not work out this week. Maybe next time.")

class NoDateAction(DateSetAction):
    def __init__(self, user_id, users):
        DateSetAction.__init__(self, users)
        self.user_id = user_id

    def handle(self, client, state):
        client.send_message(self.open_channel(client),
                "Someone else has no date yet.",
                "You can help and invite <@" + self.user_id + "> for a lunch of three.")
        return SingleAction(self.user_id)

class Factory(ActionFactory):
    def create_action(self, event, state):
        if isinstance(event, WeekData):
            return MatchAction(event)
        if isinstance(event, Notify):
            return NotifyAction(event.pairs, event.single)

Action.register_factory(Factory())
