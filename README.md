Cyder
=====

Cyder is a DNS/DHCP web manager written in Python.

Installation
============

Install dependencies. (virtualenv recommended)

```
sudo apt-get install python-dev libldap2-dev libsasl2-dev libssl-dev
git submodule update --init --recursive
pip install -r requirements/dev.txt
```

Set up MySQL along with tables and data. Enter local database settings into
cyder/settings/local.py

```
cp cyder/settings/local.py-dist cyder/settings/local.py
python manage.py syncdb
python manage.py loaddata cyder/core/fixtures/core/users.json
```

Set up Sass CSS with Django. We use a forked version of jingo-minify to compile
Sass automatically. We point our settings file towards the location of the Sass
binary.

```
sudo apt-get install rubygems
sudo gem install sass
sed -i 's/SASS_BIN = \'.*\'/SASS_BIN = \'$(echo which sass)\'/' cyder/settings/local.py
```

Install a PEP8 linter as a git pre-commit hook.

```
git clone git@github.com:jbalogh/check && cd check
sudo python check/setup.py install
cp requirements/.pre-commit cyder/.git/hooks/pre-commit
```
