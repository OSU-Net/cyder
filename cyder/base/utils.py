import distutils.dir_util
import operator
import os
import shlex
import shutil
import subprocess
import syslog
from copy import copy
from sys import stderr

import MySQLdb
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Q
from django.db.models.loading import get_model

from cyder.base.tablefier import Tablefier


def copy_tree(*args, **kwargs):
    distutils.dir_util._path_created = {}
    distutils.dir_util.copy_tree(*args, **kwargs)


def shell_out(command, use_shlex=True):
    """
    A little helper function that will shell out and return stdout,
    stderr, and the return code.
    """
    if use_shlex:
        command_args = shlex.split(command)
    else:
        command_args = command
    p = subprocess.Popen(command_args, stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    out, err = p.communicate()
    return out, err, p.returncode


class Logger(object):
    """
    A Logger logs messages passed to it. Possible destinations include stderr
    and the system journal (syslog).
    """

    def log_debug(self, msg):
        pass

    def log_info(self, msg):
        pass

    def log_notice(self, msg):
        pass

    def error(self, msg):
        raise Exception(msg)


def run_command(command, logger=Logger(), ignore_failure=False,
                failure_msg=None):
    # A single default Logger instance is shared between every call to this
    # function. Keep that in mind if you give Logger more state.
    logger.log_debug('Calling `{0}` in {1}'.format(command, os.getcwd()))
    out, err, returncode = shell_out(command)
    if returncode != 0 and not ignore_failure:
        msg = '{}: '.format(failure_msg) if failure_msg else ''
        msg += '`{}` failed in {}\n\n'.format(
            failure_msg, command, os.getcwd())
        if out:
            msg += '=== stdout ===\n{0}\n'.format(out)
        if err:
            msg += '=== stderr ===\n{0}\n'.format(err)
        msg = msg.rstrip('\n') + '\n'
        logger.error(msg)
    return out, err, returncode


def set_attrs(obj, attrs):
    for name, value in attrs.iteritems():
        setattr(obj, name, value)


def dict_merge(*dicts):
    """Later keys override earlier ones"""
    return dict(reduce(lambda x,y: x + y.items(), dicts, []))


def make_paginator(request, qs, num=20, obj_type=None):
    """
    Paginator, returns object_list.
    """
    page_name = 'page' if not obj_type else '{0}_page'.format(obj_type)
    paginator = Paginator(qs, num)
    paginator.page_name = page_name
    page = request.GET.get(page_name)
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        return paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        return paginator.page(paginator.num_pages)


def tablefy(objects, users=False, extra_cols=None, info=True, request=None,
            update=True):
    """Make list of table headers, rows of table data, list of urls
    that may be associated with table data, and postback urls.

    :param  objects: A list of objects to make table from.
    :type   objects: Generic object.
    :param  extra_cols: Extra columns to add outside of objects' .details()
    :type  extra_cols: [{'header': '',
                         'data': [{'value': '',
                                   'url': ''}]
                       },]
    """
    t = Tablefier(objects, request=request, users=users,
                  extra_cols=extra_cols, update=update)
    return t.get_table()


def make_megafilter(Klass, term):
    """
    Builds a query string that searches over fields in model's
    search_fields.
    """
    term = term.strip()
    megafilter = []
    for field in Klass.search_fields:
        if field == 'mac':
            megafilter.append(Q(**{"mac__icontains": term.replace(':', '')}))
        else:
            megafilter.append(Q(**{"{0}__icontains".format(field): term}))
    return reduce(operator.or_, megafilter)


def filter_by_ctnr(ctnr, Klass=None, objects=None):
    if not Klass and objects is not None:
        Klass = objects.model

    if ctnr.name in ['global', 'default']:
        if objects is None:
            return Klass.objects
        else:
            return objects

    return Klass.filter_by_ctnr(ctnr, objects)


def _filter(request, Klass):
    Ctnr = get_model('cyder', 'ctnr')
    if Klass is not Ctnr:
        objects = filter_by_ctnr(request.session['ctnr'], Klass)
    else:
        objects = Klass.objects

    if request.GET.get('filter'):
        try:
            return objects.filter(make_megafilter(Klass,
                                                  request.GET.get('filter')))
        except TypeError:
            pass

    return objects.distinct()


def remove_dir_contents(dir_name):
    for file_name in os.listdir(dir_name):
        file_path = os.path.join(dir_name, file_name)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)


class classproperty(property):
    """Enables you to make a classmethod a property"""
    def __get__(self, cls, obj):
        return self.fget.__get__(None, obj)()


def simple_descriptor(func):
    class SimpleDescriptor(object):
        pass
    SimpleDescriptor.__get__ = func

    return SimpleDescriptor()


def django_pretty_type(obj_type):
    if obj_type == 'user':
        return 'user'
    else:
        return None


def transaction_atomic(func):
    """Make the outermost function run in a transaction

    This decorator should be used on any function that saves or deletes model
    instances. This includes `save` and `delete` methods.  An exception will
    roll back any changes performed during the outermost method. If a
    `transaction_atomic`-wrapped function calls another
    `transaction_atomic`-wrapped function (including itself), it should pass
    `commit=False`.

    Exceptions pass through this decorator intact.
    """

    def outer(*args, **kwargs):
        if kwargs.pop('commit', True):
            with transaction.commit_on_success():
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    outer.__name__ = func.__name__
    outer.__module__ = func.__module__
    outer.__doc__ = func.__doc__
    return outer


class savepoint_atomic(object):
    def __enter__(self):
        self.sid = transaction.savepoint()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            transaction.savepoint_rollback(self.sid)
        else:
            transaction.savepoint_commit(self.sid)


def get_cursor(alias, use=True):
    """Return a cursor for database `alias` and the name of the database.

    If `use` is False, don't pass the db argument.
    """
    if alias in settings.DATABASES:
        s = settings.DATABASES[alias]
        kwargs = {
            'host': s['HOST'],
            'port': int(s['PORT'] or '0'),
            'db': s['NAME'],
            'user': s['USER'],
            'passwd': s['PASSWORD'],
        }
        kwargs.update(s['OPTIONS'])
        if use:
            kwargs['db'] = s['NAME']
    elif alias in settings.OTHER_DATABASES:
        kwargs = copy(settings.OTHER_DATABASES[alias])
    else:
        raise Exception('No such database in DATABASES or OTHER_DATABASES')
    conf = copy(kwargs)
    if not use:
        del kwargs['db']
    return MySQLdb.connect(**kwargs).cursor(), conf
