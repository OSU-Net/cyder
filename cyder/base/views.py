import simplejson as json
from copy import copy

from django import forms
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, BadHeaderError
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.forms import ValidationError, ModelChoiceField, HiddenInput
from django.forms.util import ErrorDict
from django.db.models import get_model
from django.shortcuts import (get_object_or_404, redirect, render,
                              render_to_response)

from cyder.base.constants import (ACTION_CREATE, ACTION_UPDATE, ACTION_DELETE,
                                  get_klasses)
from cyder.base.helpers import do_sort
from cyder.base.utils import (_filter, make_megafilter,
                              make_paginator, tablefy)
from cyder.base.mixins import UsabilityFormMixin
from cyder.base.utils import django_pretty_type
from cyder.core.cyuser.utils import perm, perm_soft
from cyder.core.cyuser.models import User
from cyder.core.ctnr.utils import ctnr_delete_session, ctnr_update_session
from cyder.cydns.utils import ensure_label_domain
from cyder.base.forms import BugReportForm, EditUserForm
from cyder.core.cyuser.views import edit_user
from cyder.core.ctnr.models import CtnrUser

from cyder.settings import BUG_REPORT_EMAIL


def home(request):
    return render_to_response('base/index.html', {
        'read_only': getattr(request, 'read_only', False),
    })


def admin_page(request):
    if request.POST:
        if 'user' in request.POST:
            if 'action' not in request.POST:
                messages.error(request, 'Select an option')
            else:
                edit_user(request, request.POST['user'],
                          request.POST['action'])

        return redirect(request.META.get('HTTP_REFERER', ''))

    else:
        if User.objects.get(
                id=request.session['_auth_user_id']).is_superuser == 1:

            lost_users = []
            perma_delete_data = []
            superusers = []
            nonlost_users = CtnrUser.objects.values_list('user')
            for user in User.objects.all().order_by('username'):
                if (user.pk,) not in nonlost_users:
                    lost_users.append(user)

                if user.is_superuser:
                    superusers.append(user)

            extra_cols = [
                {'header': 'Actions', 'sort_field': 'user'}]

            for user in lost_users:
                perma_delete_data.append({
                    'value': ['Delete'],
                    'url': [reverse('user-delete', kwargs={
                        'user_id': user.id})],
                    'img': ['/media/img/delete.png']})

            extra_cols[0]['data'] = perma_delete_data
            user_table = tablefy(lost_users, extra_cols=extra_cols, users=True,
                                 request=request, update=False)

            superuser_table = tablefy(superusers, users=True, request=request,
                                      update=False)
            user_form = EditUserForm()

            return render(request, 'base/admin_page.html', {
                'user_table': user_table,
                'superuser_table': superuser_table,
                'users': lost_users,
                'user_form': user_form})
        else:
            return redirect(reverse('core-index'))


def send_email(request):
    if request.POST:
        form = BugReportForm(request.POST)

        if form.is_valid():
            from_email = User.objects.get(
                pk=request.session['_auth_user_id']).email
            subject = "Cyder Bug Report: " + str(request.POST.get('bug', ''))
            message = (
                "|.......User Description......|\n"
                + request.POST.get('description', '')
                + "\n\nHow to Reproduce:"
                + "\n" + request.POST.get('reproduce', '')
                + "\n\nExpected Result:"
                + "\n" + request.POST.get('expected', '')
                + "\n\nActual Result:"
                + "\n" + request.POST.get('actual', '')
                + request.POST.get('session_data', ''))
            try:
                send_mail(subject, message, from_email,
                          [BUG_REPORT_EMAIL])
                return HttpResponse(json.dumps({'success': True}))

            except BadHeaderError:
                return HttpResponse(json.dumps(
                    {'errors': {'__all__': 'Invalid header found.'}}))

        else:
            return HttpResponse(json.dumps({'errors': form.errors}))

    else:
        session_data = (
            "\n\n|................URL...............|\n\n"
            + str(request.META.get('HTTP_REFERER', ''))
            + "\n\n|.........Session data.........|\n\n"
            + str(dict(request.session))
            + "\n\n|.........Request data.........|\n\n"
            + str(request))

        form = BugReportForm(initial={'session_data': session_data})

        return render(request, 'base/email_form.html',
                      {'form': form})


def cy_view(request, template, pk=None, obj_type=None):
    """List, create, update view in one for a flatter heirarchy. """
    # Infer obj_type from URL, saves trouble of having to specify
    # kwargs everywhere in the dispatchers.
    obj_type = obj_type or request.path.split('/')[2]

    Klass, FormKlass = get_klasses(obj_type)
    obj = get_object_or_404(Klass, pk=pk) if pk else None
    form = None
    if request.method == 'POST':
        object_table = None
        page_obj = None

        form = FormKlass(request.POST, instance=obj)
        if form.is_valid():
            try:
                if perm(request, ACTION_CREATE, obj=obj, obj_class=Klass):
                    obj = form.save()

                    if Klass.__name__ == 'Ctnr':
                        request = ctnr_update_session(request, obj)

                    if (hasattr(obj, 'ctnr_set') and
                            not obj.ctnr_set.all().exists()):
                        obj.ctnr_set.add(request.session['ctnr'])

                    object_table = tablefy([obj], request=request)
                    return HttpResponse(
                        json.dumps({'row': object_table}))

            except (ValidationError, ValueError) as e:
                if form.errors is None:
                    form.errors = ErrorDict()
                form.errors.update(e.message_dict)
                return HttpResponse(json.dumps({'errors': form.errors}))

        else:
            return HttpResponse(json.dumps({'errors': form.errors}))
    elif request.method == 'GET':
        object_list = _filter(request, Klass)

        if 'interface' not in obj_type or object_list.exists():
            form = FormKlass(instance=obj)

        if obj_type == 'system' and not object_list.exists():
            return redirect(reverse('system-create'))

        page_obj = make_paginator(request, do_sort(request, object_list), 50)
        object_table = tablefy(page_obj, request=request)

    if isinstance(form, UsabilityFormMixin):
        form.make_usable(request)

    return render(request, template, {
        'form': form,
        'obj': obj,
        'page_obj': page_obj,
        'object_table': object_table,
        'obj_type': obj_type,
        'pretty_obj_type': Klass.pretty_type,
        'pk': pk,
    })


def static_dynamic_view(request):
    template = 'core/core_interfaces.html'
    if request.session['ctnr'].name == 'global':
        return render(request, template, {})

    StaticInterface = get_model('cyder', 'staticinterface')
    DynamicInterface = get_model('cyder', 'dynamicinterface')
    statics = _filter(request, StaticInterface).select_related('system')
    dynamics = (_filter(request, DynamicInterface)
                .select_related('system', 'range'))
    page_obj = list(statics) + list(dynamics)

    def details(obj):
        data = {}
        data['url'] = obj.get_table_update_url()
        data['data'] = []
        if isinstance(obj, StaticInterface):
            data['data'].append(('System', '1', obj.system))
            data['data'].append(('Type', '2', 'static'))
            data['data'].append(('MAC', '3', obj.mac))
            data['data'].append(('IP', '4', obj.ip_str))
        elif isinstance(obj, DynamicInterface):
            data['data'].append(('System', '1', obj.system))
            data['data'].append(('Type', '2', 'dynamic'))
            data['data'].append(('MAC', '3', obj))
            data['data'].append(('IP', '4', obj.range))

        data['data'].append(('Last seen', '5', obj.last_seen))
        return data

    from cyder.base.tablefier import Tablefier
    table = Tablefier(page_obj, request, custom=details).get_table()
    if table:
        if 'sort' not in request.GET:
            sort, order = 1, 'asc'
        else:
            sort = int(request.GET['sort'])
            order = request.GET['order'] if 'order' in request.GET else 'asc'

        sort_fn = lambda x: str(x[sort]['value'][0]).lower()
        table['data'] = sorted(table['data'], key=sort_fn,
                               reverse=(order == 'desc'))
        return render(request, template, {
            'page_obj': page_obj,
            'obj_table': table,
        })
    else:
        return render(request, template, {'no_interfaces': True})


def cy_delete(request):
    """DELETE. DELETE. DELETE."""
    if not request.POST:
        return redirect(request.META.get('HTTP_REFERER', ''))

    obj_type = request.POST.get('obj_type', None)
    pk = request.POST.get('pk', None)
    Klass, _ = get_klasses(obj_type)
    obj = Klass.objects.filter(id=pk)
    if obj.exists():
        obj = obj.get()
    else:
        messages.error(request, "Object does not exist")
        return redirect(request.META.get('HTTP_REFERER', ''))
    try:
        if perm(request, ACTION_DELETE, obj=obj):
            if Klass.__name__ == 'Ctnr':
                request = ctnr_delete_session(request, obj)
            obj.delete()
    except ValidationError as e:
        messages.error(request, ', '.join(e.messages))

    referer = request.META.get('HTTP_REFERER', obj.get_list_url())
    # if there is path beyond obj.get_list_url() remove
    try:
        referer = referer.replace(referer.split(obj.get_list_url())[1], '')
    except:
        referer = request.META.get('HTTP_REFERER', '')

    return redirect(referer)


def cy_detail(request, Klass, template, obj_sets, pk=None, obj=None, **kwargs):
    """Show bunches of related tables.

    obj_sets -- string of foreign key attribute of the obj OR
                queryset relating to the obj

    Pass in either pk or already retrieved obj.
    """
    # Get object if needed.
    obj_type = request.path.split('/')[2]
    if not obj and pk:
        obj = get_object_or_404(Klass, pk=pk)
    elif not obj and pk:
        raise Exception("pk or obj required.")

    # Build related tables and paginators.
    tables = []
    for name, obj_set in obj_sets.items():
        if isinstance(obj_set, str):
            obj_set = getattr(obj, obj_set).all()
        page_obj = make_paginator(
            request, obj_set, obj_type=name.lower().replace(' ', ''))
        if obj_type == 'user':
            table = tablefy(page_obj, request=request, update=False)
        else:
            table = tablefy(page_obj, request=request)

        tables.append({
            'name': name,
            'page_obj': page_obj,
            'table': table
        })
    if obj_type == 'user':
        table = tablefy((obj,), info=False, request=request, update=False)
    else:
        table = tablefy((obj,), info=False, request=request)

    return render(request, template, dict({
        'obj': obj,
        'obj_table': table,
        'obj_type': obj_type,
        'pretty_obj_type': (django_pretty_type(obj_type) or
                            get_klasses(obj_type)[0].pretty_type),
        'tables': tables
    }.items() + kwargs.items()))


def get_update_form(request):
    """
    Update view called asynchronously from the list_create view
    """
    obj_type = request.GET.get('obj_type', '')
    record_pk = request.GET.get('pk', '')
    related_type = request.GET.get('related_type', '')
    related_pk = request.GET.get('related_pk', '')
    kwargs = json.loads(request.GET.get('data', '{}').replace("'", "\""))
    if kwargs:
        print kwargs

    if not obj_type:
        raise Http404

    Klass, FormKlass = get_klasses(obj_type)
    try:
        # Get the object if updating.
        if record_pk:
            record = Klass.objects.get(pk=record_pk)
            if perm(request, ACTION_UPDATE, obj=record):
                form = FormKlass(instance=record)
        else:
            #  Get form to create a new object and prepopulate
            if related_type and related_pk:

                # This try-except is faster than
                # `'entity' in ...get_all_field_names()`.
                try:
                    # test if the model has an 'entity' field
                    FormKlass._meta.model._meta.get_field('entity')
                    # autofill the 'entity' field
                    kwargs['entity'] = related_pk
                except:     # no 'entity' field
                    pass

                initial = copy(kwargs)
                initial[related_type] = related_pk
                if 'ctnr' in FormKlass.base_fields:
                    initial['ctnr'] = request.session['ctnr']
                form = FormKlass(initial=initial)
                if 'ctnr' in FormKlass.base_fields and \
                        request.session['ctnr'].name != 'global':
                    form.fields['ctnr'].widget = forms.HiddenInput()

                if related_type == 'range' and not obj_type.endswith('_av'):
                    for field in ['vrf', 'site', 'next_ip']:
                        form.fields[field].widget = forms.HiddenInput()
                    form.fields['ip_str'].widget.attrs['readonly'] = True
                    form.fields['ip_type'].widget.attrs['readonly'] = True
                    ip_type = form.fields['ip_type'].initial
                    form.fields['ip_type'].choices = [
                        (str(ip_type), "IPv{0}".format(ip_type))]

                if FormKlass.__name__ == 'RangeForm':
                    Network = get_model('cyder', 'network')
                    network = Network.objects.get(id=related_pk)
                    network_str = network.network_str.split('/')
                    initial = '.'.join(
                        network_str[0].split('.')[:int(network_str[1])/8])
                    if int(network_str[1]) < 32:
                        initial += '.'
                    form = FormKlass(initial=dict(
                        {'start_str': initial,
                         'end_str': initial,
                         related_type: related_pk}.items() + kwargs.items()))

            else:
                form = FormKlass(initial=kwargs)

    except ObjectDoesNotExist:
        raise Http404

    if related_type in form.fields:
        RelatedKlass, _ = get_klasses(related_type)
        form.fields[related_type] = ModelChoiceField(
            widget=HiddenInput, empty_label=None,
            queryset=RelatedKlass.objects.filter(pk=int(related_pk)))

    if isinstance(form, UsabilityFormMixin):
        form.make_usable(request)

    return HttpResponse(
        json.dumps({'form': form.as_p(), 'pk': record_pk or ''}))


def search_obj(request):
    """
    Returns a list of objects of 'obj_type' matching 'term'.
    """
    obj_type = request.GET.get('obj_type', '')
    term = request.GET.get('term', '')
    if not (obj_type and term):
        raise Http404

    Klass, FormKlass = get_klasses(obj_type)

    records = Klass.objects.filter(make_megafilter(Klass, term))[:15]
    records = [{'label': str(record), 'pk': record.pk} for record in records]

    return HttpResponse(json.dumps(records))


def table_update(request, pk, obj_type=None):
    """
    Called from editableGrid tables when updating a field. Try to update
    an object specified by pk with the post data.
    """
    # Infer obj_type from URL, saves trouble of having to specify
    # kwargs everywhere in the dispatchers.
    obj_type = obj_type or request.path.split('/')[2]

    Klass, FormKlass = get_klasses(obj_type)
    obj = get_object_or_404(Klass, pk=pk)

    if not perm_soft(request, ACTION_UPDATE, obj=obj):
        return HttpResponse(json.dumps({'error': 'You do not have appropriate'
                                                 ' permissions.'}))

    # DNS specific.
    qd = request.POST.copy()
    if 'fqdn' in qd:
        fqdn = qd.pop('fqdn')[0]
        try:
            # Call prune tree later if error, else domain leak.
            label, domain = ensure_label_domain(fqdn)
        except ValidationError, e:
            return HttpResponse(json.dumps({'error': e.messages}))
        qd['label'], qd['domain'] = label, str(domain.pk)

    form = FormKlass(qd, instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponse()
    return HttpResponse(json.dumps({'error': form.errors}))
