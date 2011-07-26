
"""
gal v0.01 

GA Client Launcher

Copyright 2011 Brian Monkaba

This file is part of ga-bitbot.

    ga-bitbot is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ga-bitbot is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ga-bitbot.  If not, see <http://www.gnu.org/licenses/>.
"""

# genetic algo client launcher

from subprocess import check_output as call, Popen, PIPE
import shlex
from os import environ
from time import *

print "Launching GA Clients..."

Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 1 n"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 1 y"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 2 n"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 2 y"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 3 n"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 3 y"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 4 n"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 4 y"'))
"""


Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 3 n"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 3 n"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 3 n"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 3 n"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 3 n"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 3 y"'))

"""
