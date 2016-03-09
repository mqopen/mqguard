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

import argparse
import mqguard

class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    def __init__(self, prog, indent_increment=2, max_help_position=64, width=180):
        argparse.ArgumentDefaultsHelpFormatter.__init__(self, prog, indent_increment, max_help_position, width)

def create_parser():
    parser = argparse.ArgumentParser(
        description="MQTT traffic diagnostic tool v{}".format(mqguard.__version__),
        epilog="Copyright (C) {} <{}>".format(mqguard.__author__, mqguard.__email__),
        formatter_class=HelpFormatter)
    parser.add_argument('-c', '--config',
                        help='path to configuration file',
                        default="/etc/mqguard.conf")
    parser.add_argument('-v', '--verbose',
                        help='verbose',
                        action='store_true')
    parser.add_argument('--version',
                        action='version',
                        version='{}'.format(mqguard.__version__))
    return parser

def parse_args():
    parser = create_parser()
    return parser.parse_args()
