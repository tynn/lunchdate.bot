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
from impl.messenger.storage import *

class StorageTest(TestCase):
    def setUp(self):
        self.state = {'weeks':{}}

    def test_add_user(self):
        week = current_week(self.state)
        add_user("abc", self.state)
        self.assertTrue(week.single)
        self.assertFalse(week.pairs)
        add_user("xyz", self.state)
        self.assertFalse(week.single)
        self.assertEqual(set(week.pairs[0]), {"abc", "xyz"})

    def test_remove_user(self):
        week = current_week(self.state)
        remove_user("abc", self.state)
        self.assertEqual(week.ignore["abc"], 0)
        add_user("efg", self.state)
        remove_user("efg", self.state)
        self.assertFalse(week.single)
        self.assertEqual(week.ignore["efg"], 0)
        week.pairs.append(("hij", "klm"))
        remove_user("klm", self.state)
        self.assertIn("hij", week.single)
        self.assertEqual(week.ignore["klm"], 0)
        week.ignore["nop"] = -1
        remove_user("nop", self.state)
        self.assertEqual(week.ignore["nop"], 1)
        week.ignore["nop"] = 2
        remove_user("nop", self.state)
        self.assertEqual(week.ignore["nop"], 2)

    def test_update_attendance(self):
        week = current_week(self.state)
        update_attendance("abc", True, 3, self.state)
        self.assertTrue(week.single)
        update_attendance("abc", False, 3, self.state)
        self.assertTrue(week.single)
        self.assertEqual(week.ignore["abc"], -3)
        update_attendance("abc", False, 0, self.state)
        self.assertFalse(week.single)
        self.assertEqual(week.ignore["abc"], 3)
        update_attendance("efg", False, 3, self.state)
        self.assertEqual(week.ignore["efg"], -3)
        update_attendance("efg", False, 2, self.state)
        self.assertEqual(week.ignore["efg"], -2)
        update_attendance("efg", False, 0, self.state)
        self.assertEqual(week.ignore["efg"], 2)
        update_attendance("efg", False, 1, self.state)
        self.assertEqual(week.ignore["efg"], 1)
        update_attendance("efg", True, 1, self.state)
        self.assertEqual(week.ignore["efg"], 0)
        update_attendance("efg", True, 0, self.state)
        self.assertNotIn("efg", week.ignore)
        self.assertIn("efg", week.single)
        update_attendance("hij", False, 3, self.state)
        update_attendance("hij", False, 0, self.state)
        self.assertEqual(week.ignore["hij"], 3)
        update_attendance("hij", True, 0, self.state)
        self.assertEqual(week.ignore["hij"], -3)
        self.assertFalse(week.single)
        update_attendance("hij", True, 3, self.state)
        self.assertNotIn("hij", week.ignore)
        update_attendance("hij", False, 2, self.state)
        self.assertEqual(week.ignore["hij"], -2)
        update_attendance("hij", False, 0, self.state)
        self.assertEqual(week.ignore["hij"], 2)
        self.assertTrue(week.single)

