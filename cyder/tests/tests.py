"""
    file that we'll add all of the unit tests we want ran before every deploy
    ./manage.py test -s tests.tests
"""
from cyder.mozdns.tests.all import *
from cyder.core.tests.all import *
