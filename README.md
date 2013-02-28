yder
=====

Cyder is a DNS/DHCP web manager written in Python.

Installation
============

```
git submodule update --init --recursive
sudo apt-get install python-dev libldap2-dev libsasl2-dev libssl-dev
pip install -r requirements/dev.txt
python manage.py syncdb
python manage.py loaddata cyder/core/fixtures/core/users.json
rubygems install sass
cp cyder/settings/local.py-dist cyder/settings/local.py
sed -i 's/SASS_BIN = '.*'/SASS_BIN = $(which sass)/' cyder/settings/local.py
cd vendor/src/jingo-minify && git remote add ngokevin git@github.com:ngokevin/jingo-minify.git && git pull ngokevin master
```

