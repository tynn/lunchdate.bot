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
from impl.api.action import *

class ActionStub(Action):
    pass

class ActionFactoryTest(TestCase):
    def test_eq(self):
        class Factory1(ActionFactory):
            pass
        self.assertEqual(Factory1(), Factory1())
        class Factory2(ActionFactory):
            pass
        self.assertNotEqual(Factory1(), Factory2())

    def test_hash(self):
        name = uuid.uuid4().hex
        Factory = type(name, (ActionFactory,), {})
        self.assertEqual(hash(Factory()), hash(__name__ + '.' + name))

class ActionTest(TestCase):
    def setUp(self):
        self.factories = Action.factories
        Action.factories = set()

    def tearDown(self):
        Action.factories = self.factories

    def test_new_without_factory(self):
        action = Action.new(None, {})
        self.assertIsNone(action)

    def test_new_with_one_factory(self):
        class Factory(ActionFactory):
            def create_action(self, *args):
                return ActionStub(None)
        Action.register_factory(Factory())
        action = Action.new(None, {})
        self.assertIsInstance(action, ActionStub)

    def test_new_with_two_factories(self):
        class TestFactory(ActionFactory):
            def __hash__(self):
                return object.__hash__(self)
            def create_action(self, event, *args, **kwargs):
                return ActionStub(None)
        Action.register_factory(TestFactory())
        Action.register_factory(TestFactory())
        action = Action.new(None, {})
        self.assertIsInstance(action, MergedAction)

