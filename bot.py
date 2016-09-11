#!/usr/bin/env python
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
if __name__ == '__main__':
    import logging, os
    log_level = os.getenv("LOG_LEVEL", "DEBUG")
    logging.getLogger().handlers[:] = []
    logging.basicConfig(format='%(created)d %(levelname)s: %(message)s', level=log_level)

    slack_token = os.getenv("SLACK_TOKEN", None)
    from impl import SlackBot
    if slack_token:
        SlackBot().start(slack_token)
    else:
        from beepboop.bot_manager import BotManager
        from beepboop.resourcer import Resourcer
        Resourcer(BotManager(SlackBot)).start()

    logging.shutdown()
