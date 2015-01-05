Cyder
===

[![Build Status](https://travis-ci.org/OSU-Net/cyder.png?branch=master)](https://travis-ci.org/OSU-Net/cyder)

Django DNS/DHCP web manager.

Meant as a ground-up rewrite of Oregon State University's DNS/DHCP network web
manager, Maintain, which was previously built with PHP, this would be the fifth
coming of Maintain.

Cyder provides a web frontend built with user experience and visual design in
mind. It provides an easy-to-use and attractive interface for network
administrators to create, view, delete, and update DNS records and DHCP
objects.

On the backend are build scripts that generate DNS BIND files and DHCP builds
directly from the database backing Cyder. The database schema and backend
data models have been designed-to-spec using the RFCs.

![Cyder](http://i.imgur.com/p8Rmbvv.png)


Setup
===

[Read the Setup wiki page](https://github.com/OSU-Net/cyder/wiki/Setup).

Coding Standards
===

Adhere to coding standards, or feel the wrath of my **erupting burning finger**.

- [Mozilla Webdev Coding Guide](http://mozweb.readthedocs.org/en/latest/reference/index.html)
- [JQuery JavaScript Style Guide](http://contribute.jquery.org/style-guide/js/)
- Strict 80-character limit on lines of code in Python, recommended in HTML and JS
- 2-space HTML indents, 4-space indent everything else
- Single-quotes over double-quotes
- Use whitespace to separate logical blocks of code — no 200 line walls of code
- Reduce, reuse, recycle — this project is very generic-heavy, look for previously invented wheels
- Keep files litter-free: throw away old print statements and pdb imports
- Descriptive variable names — verbose > incomprehensible

For multi-line blocks of code, either use 4-space hanging indents or visual indents.

```
# Hanging Indent
Ship.objects.get_or_create(
    captain='Mal', address='Serenity', class='Firefly')

# Visual Indent
Ship.objects.get_or_create(captain='Mal', address='Serenity',
                           class='Firefly')
```
