import operator

from django.core.paginator import Paginator, Page, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Q, query
from django.db.models.loading import get_model
from django.forms.models import model_to_dict

from cyder.base.constants import DHCP_OBJECTS, DNS_OBJECTS, CORE_OBJECTS
import cyder as cy


def find_get_record_url(obj):
    obj_type = obj._meta.db_table
    if obj_type in DHCP_OBJECTS:
        return reverse('cydhcp-get-record')
    elif obj_type in DNS_OBJECTS:
        return reverse('cydns-get-record')
    elif obj_type in CORE_OBJECTS:
        return reverse('core-get-record')


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


def tablefy(objects, users=False, extra_cols=None, info=True, request=False):
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
    if not objects:
        return None

    if users:
        from cyder.core.cyuser.models import UserProfile
        objects = UserProfile.objects.filter(user__in=objects)

    first_obj = objects[0]
    views = hasattr(first_obj, 'views')
    try:
        Klass = objects.object_list.model
    except:
        Klass = objects[0].__class__

    if request is not False and request.user.get_profile().has_perm(
            request, cy.ACTION_UPDATE, obj_class=Klass):
        try:
            first_obj.get_update_url()
            can_update = True
        except:
            can_update = False
    else:
        can_update = False

    headers = []
    data = []

    # Build headers.
    for title, sort_field, value in first_obj.details()['data']:
        headers.append([title, sort_field])

    if extra_cols:
        for col in extra_cols:
            headers.append([col['header'], col['sort_field']])

    foreign_keys = [j for _, j in headers if j]
    if isinstance(objects, Page) and type(objects.object_list) is not list:
        objects.object_list = objects.object_list.select_related(*foreign_keys)
    elif isinstance(objects, query.QuerySet):
        objects = objects.select_related(*foreign_keys)

    if views:
        headers.append(['Views', None])
        if hasattr(objects, 'object_list'):
            objects.object_list = objects.object_list.prefetch_related('views')

    if can_update:
        headers.append(['Actions', None])

    for i, obj in enumerate(objects):
        row_data = []
        row_data.append({
            'value': ['Info'], 'url': ['info'], 'class': ['info'],
            'img': ['/media/img/magnify.png']})
        # Columns.
        for title, field, value in obj.details()['data']:
            # Build data.
            try:
                url = value.get_detail_url()
                if value == obj:
                    if info is True:
                        row_data[0]['url'] = [url]
                    url = None
            except AttributeError:
                url = None
            if value == obj:
                value = str(value)
            row_data.append({'value': [value], 'url': [url]})

        if extra_cols:
            # Manual extra columns.
            for col in extra_cols:
                d = col['data'][i]
                data_fields = ['value', 'url', 'img', 'class']
                if isinstance(d['value'], list):
                    row_data.append(dict((key, value) for (key, value) in
                                         d.items() if key in data_fields))
                else:
                    row_data.append(dict((key, [value]) for (key, value) in
                                         d.items() if key in data_fields))

        if views:
            # Another column for views.
            view_field = None
            if hasattr(obj, 'views'):
                for view in obj.views.all():
                    if view_field:
                        view_field += ' ' + view.name
                    else:
                        view_field = view.name
                row_data.append({'value': [view_field], 'url': [None]})
            else:
                row_data.append({'value': ['None'], 'url': [None]})

        # Actions
        if can_update:
            row_data.append({'value': ['Update', 'Delete'],
                             'url': [obj.get_update_url(),
                                     obj.get_delete_url()],
                             'data': [[('pk', obj.id),
                                       ('object_type', obj._meta.db_table),
                                       ('getUrl', find_get_record_url(obj))],
                                      None],
                             'class': ['update', 'delete'],
                             'img': ['/media/img/update.png',
                                     '/media/img/delete.png']})

        # Build table.
        if row_data[0]['url'] in [['info'], ['']]:
            del row_data[0]

        data.append(row_data)

    if data[0][0]['value'] == ['Info']:
        headers.insert(0, ['Info', None])
        col_index = 1
    else:
        col_index = 0

    if data and not issubclass(type(objects), Page):
        data = sorted(
            data, key=lambda row: str(row[col_index]['value'][0]).lower())

    return {
        'headers': headers,
        'postback_urls': [obj.details()['url'] for obj in objects],
        'data': data,
    }


def make_megafilter(Klass, term):
    """
    Builds a query string that searches over fields in model's
    search_fields.
    """
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
        return objects or Klass.objects

    if hasattr(Klass, 'filter_by_ctnr'):
        return Klass.filter_by_ctnr(ctnr, objects)
    else:
        objects = objects or Klass.objects
        if hasattr(Klass, 'domain'):
            objects = objects.filter(domain__in=ctnr.domains.all())
        elif hasattr(Klass, 'reverse_domain'):
            objects = objects.filter(reverse_domain__in=ctnr.domains.all())

    return objects


def _filter(request, Klass):
    Ctnr = get_model('ctnr', 'ctnr')
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


def qd_to_py_dict(qd):
    """Django QueryDict to Python dict."""
    ret = {}
    for k in qd:
        ret[k] = qd[k]
    return ret


def model_to_post(post, obj):
    """
    Updates requests's POST dictionary with values from object, for update
    purposes.
    """
    ret = qd_to_py_dict(post)
    for k, v in model_to_dict(obj).iteritems():
        if k not in post:
            ret[k] = v
    return ret
