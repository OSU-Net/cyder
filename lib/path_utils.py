"""Originally from funfactory (funfactory/path_utils.py) on a380a54"""

import os
from os.path import abspath, dirname


def path(*a):
    return os.path.join(ROOT, *a)


def import_mod_by_name(target):
    # stolen from mock :)
    components = target.split('.')
    import_path = components.pop(0)
    thing = __import__(import_path)

    for comp in components:
        import_path += ".%s" % comp
        thing = _dot_lookup(thing, comp, import_path)
    return thing


def _dot_lookup(thing, comp, import_path):
    try:
        return getattr(thing, comp)
    except AttributeError:
        __import__(import_path)
        return getattr(thing, comp)

ROOT = dirname(dirname(abspath(__file__)))
