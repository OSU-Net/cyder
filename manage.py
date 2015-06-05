#!/usr/bin/env python

import sys

import activate


activate.activate()
from django.core.management import execute_from_command_line
execute_from_command_line(sys.argv)
