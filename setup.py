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

"""
A Slackbot for matching people for lunch once a week. Just let lunchdate.bot
have the hassle of pairing members of your team randomly, while they choose the
date themselves.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name            ='launchdate.bot',
    version         ='1.0',
    description     ="Slackbot for matching people for lunch once a week",
    long_description=__doc__,
    author          ="Christian Schmitz",
    author_email    ="tynn.dev@gmail.com",
    url             ="https://github.com/tynn/lunchdate.bot",
    license         ='LGPLv3+',
    packages        =[
        'launchdate-bot',
        'launchdate-bot.api',
        'launchdate-bot.messenger'
    ],
    package_dir     ={'launchdate-bot': 'impl'},
    platforms       =['Linux'],
    classifiers     =[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: '
            'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ])
