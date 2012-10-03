"""
    file that we'll add all of the unit tests we want ran before every deploy
    ./manage.py test -s tests.tests
"""
from cyder.systems.tests import *
from cyder.api_v3.tests import *
from cyder.mozdns.tests.all import *
from cyder.core.tests.all import *
