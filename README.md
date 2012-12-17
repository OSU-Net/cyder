Cyder
=====

Cyder is a DNS/DHCP web manager written in Python.

Installation
============

```
git submodule update --init --recursive
pip install requirements/dev.txt
pip install -e git+git://github.com/uberj/dnspython.git#egg=dnspython
python manage.py syncdb
python manage.py loaddata cyder/core/fixtures/core/users.json
rubygems install sass
cp cyder/settings/local.py-dist cyder/settings/local.py
sed -i 's/SASS_BIN = '.*'/SASS_BIN = $(watch sass)/' cyder/settings/local.py
cd vendor/src/jingo-minify && git remote add ngokevin git@github.com:ngokevin/jingo-minify.git && git pull ngokevin master
```
