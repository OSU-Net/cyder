.. _coding_standards:

Coding Ideas (Standards)
========================

The Zen of Python, by Tim Peters::

    Beautiful is better than ugly.
    Explicit is better than implicit.
    Simple is better than complex.
    Complex is better than complicated.
    Flat is better than nested.
    Sparse is better than dense.
    Readability counts.
    Special cases aren't special enough to break the rules.
    Although practicality beats purity.
    Errors should never pass silently.
    Unless explicitly silenced.
    In the face of ambiguity, refuse the temptation to guess.
    There should be one-- and preferably only one --obvious way to do it.
    Although that way may not be obvious at first unless you're Dutch.
    Now is better than never.
    Although never is often better than *right* now.
    If the implementation is hard to explain, it's a bad idea.
    If the implementation is easy to explain, it may be a good idea.
    Namespaces are one honking great idea -- let's do more of those!


Follow pep8::

    pip install pep8
    pep8 <all of the files!!>

Model code should have 100% statement coverage.

Before you do anything with an IP address (as a string or int) put it into the ipaddr library
functions IPv4Address and IPv6Address. This will standardize how things are formated, stored, and
displayed.

In most cases policy should happen in forms and function should happen in models.
