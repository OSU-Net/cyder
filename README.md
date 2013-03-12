Cyder
=====

Django DNS/DHCP web manager.

It is meant as a ground-up rewrite of Oregon State University's DNS/DHCP
network web manager, Maintain, which was previously built with PHP. This would
be the fifth coming of Maintain.

Cyder provides a web frontend designed with user experience and visual design
in mind. It provides an easy-to-use and attractive interface for network administrators
to create, viw, delete, and update DNS records and DHCP objects.

On the backend are build scripts that generate DNS BIND files and DHCP builds
directly from the database backing Cyder. The database schema and backend
validations have been designed using the appropriate RFCs.

![Cyder](http://imgur.com/TiFvTnU.jpg)


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

Coding Standards
================

Adhere to coding standards, or feel the wrath of my **erupting burning finger**.

- [Mozilla Webdev Coding Guide](http://mozweb.readthedocs.org/en/latest/coding.html)
- Strict 80-character limit on lines of code in Python, recommended in HTML and JS
- 2-space HTML indents, 4-space indent everything else
- Single-quotes over double-quotes
- Use whitespace to separate logical blocks of code - no 200 line walls of code
- Reduce, reuse, recycle - this project is very generic-heavy, look for previously invented wheels
- Keep files litter-free: throw away old print statements and pdb imports
- Descriptive variable names - verbose > incomprehensible

For multi-line blocks of code, either use 4-space hanging indents or visual indents.

```
# Hanging Indent
Ship.objects.get_or_create(
    captain='Mal', address='Serenity', class='Firefly')

# Visual Indent
Ship.objects.get_or_create(captain='Mal', address='Serenity',
                           class='Firefly')
```
