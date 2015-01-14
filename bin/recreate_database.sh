#!/bin/bash

python -m bin.lib.recreate_database
./manage.py syncdb --noinput
./manage.py migrate cyder
