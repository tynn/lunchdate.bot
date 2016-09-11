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
from time import localtime
from ..api.action import Action, ActionFactory, MergedAction
from ..api.event import Hello, Notify

"""
    > # -- -@+[0-3] @+@ @+@ ... @ !
"""

SLACKBOT = 'USLACKBOT'

def current_week(state):
    return get_week(localtime().tm_yday // 7, state['weeks'])

def get_week(week_number, weeks):
    week_number += 1
    if week_number in weeks:
        return weeks[week_number]
    week = WeekData('#{} !'.format(week_number))
    for i in range(3):
        if week_number - i in weeks:
            ignore = weeks[week_number - i].ignore.items()
            ignore = map(lambda t: (t[0], abs(t[1]) - i), ignore)
            week.ignore.update(filter(lambda t: t[1] >= 0, ignore))
            break
    weeks[week.number] = week
    return week

def add_user(user_id, state):
    week = current_week(state)
    no_single = not week.single
    week.single.add(user_id)
    if len(week.single) == 2:
        pair = (week.single.pop(), week.single.pop())
        week.pairs.append(pair)
        notify = Notify(None, pair)
    elif no_single:
        notify = Notify(user_id)
    else:
        return
    return MergedAction(week.write(), Action.new(notify, state))

def remove_user(user_id, state):
    week = current_week(state)
    ignore = abs(week.ignore[user_id]) if user_id in week.ignore else 0
    week.ignore[user_id] = ignore
    if user_id in week.single:
        week.single.remove(user_id)
        return week.write()
    for pair in week.pairs:
        if user_id in pair:
            week.pairs.remove(pair)
            return add_user(pair[0] if pair[1] == user_id else pair[1], state)

def update_attendance(user_id, attend, count, state):
    week = current_week(state)
    count = abs(count)
    if user_id not in week.ignore:
        if attend:
            return add_user(user_id, state)
        week.ignore[user_id] = -count
        if count:
            return week.write()
        return remove_user(user_id, state)
    ignore = week.ignore[user_id]
    if not count:
        if attend == (ignore < 0):
            return
        if ignore:
            week.ignore[user_id] = -ignore
        else:
            del week.ignore[user_id]
        if attend:
            return add_user(user_id, state)
        return remove_user(user_id, state)
    if attend:
        if ignore < 0:
            del week.ignore[user_id]
        else:
            week.ignore[user_id] = 0
        return week.write()
    if abs(ignore) == count:
        return
    week.ignore[user_id] = -count if ignore < 0 else count
    return week.write()

def find_paired(state):
    return sum(map(lambda w: w.pairs, state['weeks'].values()), [])

class WeekData(object):
    P = re.compile(r'@([0-9A-Z]+)\+@([0-9A-Z]+)')
    S = re.compile(r'@([0-9A-Z]+)')
    I = re.compile(r'-@([0-9A-Z]+)([+-][0123])?')

    def __init__(self, line):
        self.skip = False
        self.pairs = []
        self.single = set()
        self.ignore = {}
        fields = line.split()
        self.number = int(fields.pop(0)[1:])
        for field in fields:
            if field == '!':
                break
            if field == '--':
                self.skip = True
                continue
            result = self.P.match(field)
            if result:
                self.pairs.append(result.groups())
                continue
            result = self.S.match(field)
            if result:
                self.single.add(result.groups()[0])
                continue
            result = self.I.match(field)
            if result:
                user, count = result.groups()
                self.ignore[user] = int(count)
                continue

    def __repr__(self):
        fields = ['#' + str(self.number)]
        if self.skip:
            fields.append('--')
        fields.extend(map(lambda t: '-@{}{:+d}'.format(*t), self.ignore.items()))
        fields.extend(map(lambda t: '@{}+@{}'.format(*t), self.pairs))
        fields.extend(map(lambda t: '@' + t, self.single))
        fields.append('!')
        return ' '.join(fields)

    def __str__(self):
        fields = ['#' + str(self.number)]
        if self.skip:
            fields.append('--')
        fields.extend(map(lambda t: '-<@{}>{:+d}'.format(*t), self.ignore.items()))
        fields.extend(map(lambda t: '<@{}>+<@{}>'.format(*t), self.pairs))
        fields.extend(map(lambda t: '<@{}>'.format(t), self.single))
        fields.append('!')
        return ' '.join(fields)

    def write(self):
        return WriteAction(self)

class StorageAction(Action):
    def get_messages(self, client):
        channel = client.api_call('im.open', user=SLACKBOT)['channel']['id']
        messages = client.api_call('im.history', channel=channel)
        return messages['messages'], channel

class ReadAction(StorageAction):
    def handle(self, client, state):
        messages, channel = self.get_messages(client)
        messages = map(lambda m: m['text'].split('\n'), messages)
        weeks = map(WeekData, sum(messages, []))
        state['weeks'] = dict(map(lambda w: (w.number, w), weeks))

class NewAction(Action):
    def handle(self, client, state):
        return Action.new(get_week(self.event, state['weeks']), state)

class WriteAction(StorageAction):
    def handle(self, client, state):
        weeks = state['weeks']
        if isinstance(self.event, WeekData):
            self.update(client, self.event, weeks)
        else:
            self.sync(client, self.event, weeks)

    def sync(self, client, week_number, weeks):
        messages, channel = self.get_messages(client)
        for message in messages:
            client.api_call('chat.delete', ts=message['ts'], channel=channel)
        week = weeks[week_number]
        weeks = filter(lambda w: w.number != week_number, weeks.values())
        client.send_message(channel, *map(repr, weeks))
        client.send_message(channel, repr(week))

    def update(self, client, week, weeks):
        user = client.id()
        week_number = '#' + str(week.number)
        messages, channel = self.get_messages(client)
        f = lambda m: m['user'] == user and m['text'].startswith(week_number)
        messages = filter(f, messages)
        if len(messages) != 1:
            return self.sync(client, week.number, weeks)
        ts = messages[0]['ts']
        client.api_call('chat.update', ts=ts, channel=channel, text=repr(week))

class Factory(ActionFactory):
    def create_action(self, event, state):
        if isinstance(event, Hello):
            return ReadAction(None)

Action.register_factory(Factory())
