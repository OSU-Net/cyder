import json

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms import ChoiceField, HiddenInput
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.db.models.loading import get_model

from cyder.base.constants import LEVELS, ACTION_UPDATE
from cyder.base.utils import tablefy
from cyder.core.ctnr.forms import CtnrForm, CtnrUserForm, CtnrObjectForm
from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.core.cyuser.backends import _has_perm


class CtnrView(object):
    model = Ctnr
    queryset = Ctnr.objects.all()
    form_class = CtnrForm


def ctnr_detail(request, pk):
    ctnr = Ctnr.objects.get(id=pk)

    ctnrUsers = ctnr.ctnruser_set.select_related('user', 'user__profile')
    ctnrDomains = ctnr.domains.select_related().filter(
        is_reverse=False)
    ctnrRdomains = ctnr.domains.select_related().filter(is_reverse=True)
    ctnrRanges = ctnr.ranges.select_related()
    ctnrWorkgroups = ctnr.workgroups.select_related()

    if request.user.get_profile().has_perm(
            request, ACTION_UPDATE, obj_class='CtnrObject', ctnr=ctnr):

        extra_cols, domains = create_obj_extra_cols(
            ctnr, ctnrDomains, 'domain')
        domain_table = tablefy(domains, extra_cols=extra_cols, request=request)

        extra_cols, rdomains = create_obj_extra_cols(
            ctnr, ctnrRdomains, 'domain')
        rdomain_table = tablefy(rdomains, extra_cols=extra_cols,
                                request=request)

        extra_cols, ranges = create_obj_extra_cols(ctnr, ctnrRanges, 'range')
        range_table = tablefy(ranges, extra_cols=extra_cols, request=request)

        extra_cols, workgroups = create_obj_extra_cols(
            ctnr, ctnrWorkgroups, 'workgroup')
        workgroup_table = tablefy(workgroups, extra_cols=extra_cols,
                                  request=request)

        object_form = CtnrObjectForm(obj_perm=True)

    else:
        domain_table = tablefy(ctnrDomains, request=request)
        rdomain_table = tablefy(ctnrRdomains, request=request)
        range_table = tablefy(ctnrRanges, request=request)
        workgroup_table = tablefy(ctnrWorkgroups, request=request)
        object_form = CtnrObjectForm()
        object_form.fields['obj_type'] = ChoiceField(widget=HiddenInput,
                                                     initial='user')

    if request.user.get_profile().has_perm(
            request, ACTION_UPDATE, obj_class='CtnrUser', ctnr=ctnr):

        extra_cols, users = create_user_extra_cols(ctnr, ctnrUsers,
                                                   actions=True)
        user_table = tablefy(users, extra_cols=extra_cols, users=True,
                             request=request, update=False)
    else:
        extra_cols, users = create_user_extra_cols(ctnr, ctnrUsers)
        user_table = tablefy(users, extra_cols=extra_cols, users=True,
                             request=request, update=False)

    add_user_form = CtnrUserForm(initial={'ctnr': ctnr})

    return render(request, 'ctnr/ctnr_detail.html', {
        'obj': ctnr,
        'pretty_obj_type': ctnr.pretty_type,
        'obj_type': 'ctnr',
        'user_table': user_table,
        'domain_table': domain_table,
        'rdomain_table': rdomain_table,
        'range_table': range_table,
        'workgroup_table': workgroup_table,
        'add_user_form': add_user_form,
        'object_select_form': object_form
    })


def create_user_extra_cols(ctnr, ctnrusers, actions=False):
    level_data = []
    action_data = []
    users = []
    extra_cols = [
        {'header': 'Level to %s' % ctnr.name, 'sort_field': None}]
    if actions:
        extra_cols.append({'header': 'Remove', 'sort_field': None})

    for ctnruser in ctnrusers:
        user = ctnruser.user
        if user.is_superuser:
            val = 'Superuser'
            level = {
                'value': val,
                'url': '',
            }
        else:
            if actions:
                level = {}
                level['value'] = [LEVELS[ctnruser.level], '-', '+']
                level['url'] = [
                    '',
                    reverse('ctnr-update-user', kwargs={'ctnr_pk': ctnr.id}),
                    reverse('ctnr-update-user', kwargs={'ctnr_pk': ctnr.id})]

                level['img'] = [
                    '', '/media/img/minus.png', '/media/img/plus.png']

                level['class'] = ['', 'minus', 'plus']
                level['data'] = [
                    '',
                    [('kwargs', json.dumps({'obj_type': 'user', 'pk': user.id,
                                            'name': str(user), 'lvl': -1}))],
                    [('kwargs', json.dumps({'obj_type': 'user', 'pk': user.id,
                                            'name': str(user), 'lvl': 1}))]]

                if level['value'][0] == 'Admin':
                    del level['value'][2]
                    del level['url'][2]
                    del level['img'][2]
                    del level['class'][2]
                    del level['data'][2]

                elif level['value'][0] == 'Guest':
                    del level['value'][1]
                    del level['url'][1]
                    del level['img'][1]
                    del level['class'][1]
                    del level['data'][1]
            else:
                level = {
                    'value': [LEVELS[ctnruser.level]],
                    'url': ['']
                }

        level_data.append(level)
        users.append(user)
        if actions:
            action_data.append({
                'value': 'Remove',
                'url': reverse('ctnr-update-user',
                               kwargs={'ctnr_pk': ctnr.id}),
                'img': '/media/img/remove.png',
                'class': 'remove user',
                'data': [('kwargs', json.dumps({
                    'obj_type': 'user', 'pk': user.id, 'name': str(user)}))]
            })

    extra_cols[0]['data'] = level_data
    if actions:
        extra_cols[1]['data'] = action_data

    return extra_cols, users


def create_obj_extra_cols(ctnr, obj_set, obj_type):
    remove_data = []
    objs = []
    extra_cols = [{'header': 'Remove', 'sort_field': None}]

    for obj in obj_set:
        remove_data.append({
            'value': 'Remove',
            'url': reverse('ctnr-remove-object', kwargs={
                'ctnr_pk': ctnr.id}),
            'img': '/media/img/remove.png',
            'class': 'remove object',
            'data': [('kwargs', json.dumps({
                'obj_type': str(obj._meta.db_table), 'pk': obj.id}))]
        })
        objs.append(obj)
    extra_cols[0]['data'] = remove_data

    return extra_cols, objs


def update_user(request, ctnr_pk):
    if not request.POST:
        return redirect(request.META.get('HTTP_REFERER', ''))
    ctnr = Ctnr.objects.get(id=ctnr_pk)
    user_pk = request.POST.get('pk', None)
    return_status = {}
    if request.user.get_profile().id != int(user_pk):
        if _has_perm(request.user, ctnr, ACTION_UPDATE, obj_class=CtnrUser):
            cu_qs = CtnrUser.objects.filter(ctnr_id=ctnr_pk, user_id=user_pk)
            if cu_qs.exists():
                ctnr_user = cu_qs.get()
                if request.POST.get('action', None) == 'obj_remove':
                    ctnr_user.delete()
                else:
                    lvl = request.POST.get('lvl', None)
                    if (ctnr_user.level + int(lvl)) in range(0, 3):
                        ctnr_user.level += int(lvl)
                        ctnr_user.save()

                return_status['success'] = True
            else:
                return_status['error'] = (
                    'That user does not exist inside this container')
        else:
            return_status['error'] = (
                'You do not have permission to perform this action')
    else:
        return_status['error'] = 'You can not edit your own permissions'

    return HttpResponse(json.dumps(return_status))


def remove_object(request, ctnr_pk):
    if not request.POST:
        return redirect(request.META.get('HTTP_REFERER', ''))
    acting_user = request.user
    obj_type = request.POST.get('obj_type', None)
    obj_pk = request.POST.get('pk', None)
    ctnr = Ctnr.objects.get(id=ctnr_pk)
    return_status = {}
    if _has_perm(acting_user, ctnr, ACTION_UPDATE, obj_class=Ctnr):
        Klass = get_model('cyder', obj_type)
        obj = Klass.objects.get(id=obj_pk)
        m2m = getattr(ctnr, (obj_type + 's'), None)

        if m2m is None:
            return_status['error'] = (
                '{0} is not related to {1}'.format(obj_type, ctnr))

        else:
            if obj in m2m.all():
                m2m.remove(obj)
                return_status['success'] = True
            else:
                return_status['error'] = (
                    '{0} does not exist in {1}'.format(str(obj), ctnr))

    else:
        return_status['error'] = (
            'You do not have permission to perform this action')

    return HttpResponse(json.dumps(return_status))


def add_object(request, ctnr_pk):
    """Add object to container."""
    acting_user = request.user
    ctnr = Ctnr.objects.get(id=ctnr_pk)
    pk = request.POST.get('obj_pk', '')
    name = request.POST.get('obj', '')
    obj_type = request.POST.get('obj_type', '')
    if obj_type == 'user':
        if _has_perm(acting_user, ctnr, ACTION_UPDATE, obj_class=CtnrUser):
            return add_user(request, ctnr, name)
        else:
            messages.error(request,
                           'You do not have permission to perform this action')
            return HttpResponse(json.dumps({'success': False}))

    else:
        if _has_perm(acting_user, ctnr, ACTION_UPDATE, obj_class=Ctnr):
            Klass = get_model('cyder', obj_type)
            if pk == 'null':
                try:
                    if Klass.__name__ == 'Range':
                        return HttpResponse(json.dumps({
                            'error': 'Please select a valid range'}))
                    obj = Klass.objects.get(name=name)
                except Klass.DoesNotExist:
                    return HttpResponse(
                        json.dumps({'error': '{0} is not a valid {1}'.format(
                            name, obj_type)}))
            else:
                obj = Klass.objects.get(id=pk)

            m2m = getattr(ctnr, (obj_type + 's'), None)

            if m2m is None:
                return HttpResponse(json.dumps({
                    'error': '{0} is not related to {1}'.format(
                        obj_type, ctnr)}))

            else:
                if obj in m2m.all():
                    return HttpResponse(json.dumps({
                        'error': '{0} already exists in {1}'.format(
                            name, str(ctnr))}))

            m2m.add(obj)

        else:
            messages.error(request,
                           'You do not have permission to perform this action')
    return HttpResponse(json.dumps({'success': 'true'}))


def add_user(request, ctnr, name):
    confirmation = request.POST.get('confirmation', '')
    level = request.POST.get('level', '')
    if not name:
        return HttpResponse(json.dumps({
            'error': 'Please enter a user name'}))

    if not level:
        return HttpResponse(json.dumps({
            'error': 'Please select an administrative level'}))

    if (confirmation == 'false' and
            not User.objects.filter(username=name).exists()):
        return HttpResponse(json.dumps({
            'acknowledge': 'This user is not in any other container. '
            'Are you sure you want to create this user?'}))

    user, _ = User.objects.get_or_create(username=name)
    user.save()
    if CtnrUser.objects.filter(user_id=user.id, ctnr_id=ctnr.id).exists():
        return HttpResponse(json.dumps({
            'error': 'This user already exists in this container'}))

    CtnrUser(user_id=user.id, ctnr_id=ctnr.id, level=level).save()
    return HttpResponse(json.dumps({'success': True}))


def change_ctnr(request, pk=None):
    """
    Change session container and other related session variables.
    """
    referer = request.META.get('HTTP_REFERER', '/')

    # Check if ctnr exists.
    try:
        if request.method == 'POST':
            ctnr = Ctnr.objects.get(name=request.POST['ctnr_name'])
        else:
            ctnr = Ctnr.objects.get(id=pk)
    except:
        for ctnr in request.session['ctnrs']:
            if ctnr.name == request.POST['ctnr_name']:
                request.session['ctnrs'].remove(ctnr)
        messages.error(request, "Could not change container, does not exist")
        request.session.modified = True
        return redirect(referer)

    # Check if user has access to ctnr.
    try:
        global_ctnr_user = CtnrUser.objects.get(user=request.user, ctnr=1)
    except CtnrUser.DoesNotExist:
        global_ctnr_user = None
    try:
        ctnr_user = CtnrUser.objects.get(user=request.user, ctnr=ctnr)
    except CtnrUser.DoesNotExist:
        ctnr_user = None

    prev = request.session['ctnr']
    if ctnr_user or global_ctnr_user or ctnr.pk == 1:
        # Set session ctnr and level.
        request.session['ctnr'] = ctnr

        # Higher level overrides.
        if ctnr_user:
            level = ctnr_user.level
        else:
            level = 0
        if global_ctnr_user:
            global_level = global_ctnr_user.level
        else:
            global_level = 0
        request.session['level'] = max(level, global_level)

    else:
        messages.error(request, "You do not have access to this container.")

    if ('/' + '/'.join(referer.split('/')[3:]) ==
            reverse('ctnr-detail', kwargs={'pk': prev.id})):
        referer = reverse('ctnr-detail', kwargs={'pk': ctnr.id})

    return redirect(referer)
