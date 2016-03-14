#!/usr/bin/env python3
# Copyright (C) Ivo Slanina <ivo.slanina@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
import mqguard

setup(
    name = "mqguard",
    url = 'https://github.com/buben19/mqguard',
    version = mqguard.__version__,
    packages = find_packages(exclude = ['doc']),
    install_requires = [
        'mqreceive>=0.1.0',
        'websockets>=2.6'],
    author = mqguard.__author__,
    author_email = mqguard.__email__,
    description = "MQTT traffic diagnostic tool",
    long_description = "",
    license = "GPLv3",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Customer Service',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Communications',
        'Topic :: Home Automation',
        'Topic :: Internet',
    ],
    keywords = 'iot internetofthings mqopen mqtt sensors diagnostic',
    entry_points = {
        "console_scripts": [
            "mqguard = mqguard.__main__:main"
        ]
    }
)
