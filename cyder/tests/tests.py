"""
File that we'll add all of the unit tests we want run before every deploy
./manage.py test -s tests.tests
"""
from cyder.cydns.tests.all import *
from cyder.cydhcp.tests.all import *
