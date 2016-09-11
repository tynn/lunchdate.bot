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

import uuid
from unittest import TestCase
from impl.api.event import *

message = {
    u'type': u'message',
    u'text': u'Hello <@U234FV5FE>',
    u'user': u'U234BD8D6',
    u'channel': u'C234JJP37',
    u'team': u'T234NHK4H',
    u'ts': u'1471774910.000002',
}

class EventTest(TestCase):
    def test_new_unknown(self):
        event = Event.new({u'type': u'none'})
        self.assertIsNone(event)

    def test_new_message(self):
        event = Event.new(message)
        self.assertEquals(event.text, message['text'])
        self.assertEquals(event.channel, message['channel'])

