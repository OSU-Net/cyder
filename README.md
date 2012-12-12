Cyder
=====

Cyder is a DNS/DHCP web manager written in Python.

Installation
============

```
git submodule update --init --recursive
pip install requirements/dev.txt
pip install -e git+git://github.com/uberj/dnspython.git#egg=dnspython
rubygems install sass
python manage.py syncdb
python manage.py loaddata cyder/core/fixtures/initial_data.json
```
