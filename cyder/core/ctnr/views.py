import json

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms import ChoiceField, HiddenInput
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.db.models.loading import get_model

import cyder as cy
from cyder.base.constants import LEVELS
from cyder.base.utils import tablefy
from cyder.core.ctnr.forms import CtnrForm, CtnrUserForm, CtnrObjectForm
from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.core.cyuser.backends import _has_perm
from cyder.core.views import CoreCreateView


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
            request, cy.ACTION_UPDATE, obj_class='CtnrObject'):

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
            request, cy.ACTION_UPDATE, obj_class='CtnrUser'):

        extra_cols, users = create_user_extra_cols(ctnr, ctnrUsers)
        user_table = tablefy(users, extra_cols=extra_cols, users=True,
                             request=request)
    else:
        user_table = tablefy(ctnrUsers, users=True, request=request)

    add_user_form = CtnrUserForm(initial={'ctnr': ctnr})

    return render(request, 'ctnr/ctnr_detail.html', {
        'object': ctnr,
        'obj_type': 'ctnr',
        'user_table': user_table,
        'domain_table': domain_table,
        'rdomain_table': rdomain_table,
        'range_table': range_table,
        'workgroup_table': workgroup_table,
        'add_user_form': add_user_form,
        'object_select_form': object_form
    })


def create_user_extra_cols(ctnr, ctnrusers):
    level_data = []
    action_data = []
    users = []
    extra_cols = [
        {'header': 'Level to %s' % ctnr.name, 'sort_field': 'user'},
        {'header': 'Remove', 'sort_field': 'user'}]

    for ctnruser in ctnrusers:
        user = ctnruser.user
        if user.is_superuser:
            val = 'Superuser'
            level = {
                'value': val,
                'url': '',
            }
        else:
            level = {
                'value': [LEVELS[ctnruser.level], '+', '-'],
                'url': [
                    '',
                    reverse('update-user-level', kwargs={
                        'ctnr_pk': ctnr.id, 'user_pk': user.id,
                        'lvl': -1}),
                    reverse('update-user-level', kwargs={
                        'ctnr_pk': ctnr.id, 'user_pk': user.id,
                        'lvl': 1})],
                'img': ['', '/media/img/minus.png', '/media/img/plus.png'],
                'class': ['', 'minus', 'plus']
            }

            if level['value'][0] == 'Admin':
                del level['value'][2]
                del level['url'][2]
                del level['img'][2]

            elif level['value'][0] == 'Guest':
                del level['value'][1]
                del level['url'][1]
                del level['img'][1]

        level_data.append(level)
        users.append(user)
        action_data.append({
            'value': 'Delete',
            'url': reverse('ctnr-remove-user', kwargs={
                'ctnr_pk': ctnr.id, 'user_pk': user.id}),
            'img': '/media/img/delete.png',
            'class': 'delete'
        })

    extra_cols[0]['data'] = level_data
    extra_cols[1]['data'] = action_data

    return extra_cols, users


def create_obj_extra_cols(ctnr, obj_set, obj_type):
    remove_data = []
    objs = []
    if obj_type == 'range':
        extra_cols = [
            {'header': 'Remove', 'sort_field': 'range'}]
    else:
        extra_cols = [
            {'header': 'Remove', 'sort_field': 'name'}]

    for obj in obj_set:
        remove_data.append({
            'value': 'Delete',
            'url': reverse('ctnr-remove-object', kwargs={
                'ctnr_pk': ctnr.id, 'obj_type': obj_type, 'obj_pk': obj.pk}),
            'img': '/media/img/delete.png',
            'class': 'delete'
        })
        objs.append(obj)
    extra_cols[0]['data'] = remove_data

    return extra_cols, objs


def remove_user(request, ctnr_pk, user_pk):
    acting_user = request.user

    if acting_user.get_profile().id == int(user_pk):
        messages.error(request, 'You can not edit your own permissions')
        return redirect(request.META.get('HTTP_REFERER', ''))

    if _has_perm(acting_user, Ctnr.objects.get(id=ctnr_pk), cy.ACTION_UPDATE,
                 obj_class=CtnrUser):
        try:
            CtnrUser.objects.get(ctnr_id=ctnr_pk, user_id=user_pk).delete()

        except:
            messages.error(request,
                           'That user does not exist inside this container')

        return redirect(request.META.get('HTTP_REFERER', ''))

    else:
        messages.error(
            request, 'You do not have permission to perform this action')
        return redirect(request.META.get('HTTP_REFERER', ''))


def update_user_level(request, ctnr_pk, user_pk, lvl):
    acting_user = request.user

    if acting_user.get_profile().id == int(user_pk):
        messages.error(request, 'You can not edit your own permissions')
        return redirect(request.META.get('HTTP_REFERER', ''))

    if _has_perm(acting_user, Ctnr.objects.get(id=ctnr_pk), cy.ACTION_UPDATE,
                 obj_class=CtnrUser):
        try:
            ctnr_user = CtnrUser.objects.get(ctnr_id=ctnr_pk, user_id=user_pk)

        except:
            messages.error(request,
                           'That user does not exist inside this container')

        if (ctnr_user.level + int(lvl)) not in range(0, 3):
            return redirect(request.META.get('HTTP_REFERER', ''))

        else:
            ctnr_user.level += int(lvl)
            ctnr_user.save()
            return redirect(request.META.get('HTTP_REFERER', ''))

    else:
        messages.error(
            request, 'You do not have permission to perform this action')
        return redirect(request.META.get('HTTP_REFERER', ''))


def remove_object(request, ctnr_pk, obj_type, obj_pk):
    acting_user = request.user
    ctnr = Ctnr.objects.get(id=ctnr_pk)
    if _has_perm(acting_user, ctnr, cy.ACTION_UPDATE, obj_class=Ctnr):
        Klass = get_model(obj_type, obj_type)
        obj = Klass.objects.get(id=obj_pk)
        m2m = getattr(ctnr, (obj_type + 's'), None)

        if m2m is None:
            messages.error(
                request, '{0} is not related to {1}'.format(obj_type, ctnr))

        else:
            if obj in m2m.all():
                m2m.remove(obj)
            else:
                messages.error(
                    request, '{0} does not exist in {1}'.format(
                        str(obj), ctnr))

    else:
        messages.error(request,
                       'You do not have permission to perform this action')

    return redirect(reverse('ctnr-detail', args=[ctnr.id]))


def add_object(request, ctnr_pk):
    """Add object to container."""
    acting_user = request.user
    ctnr = Ctnr.objects.get(id=ctnr_pk)
    pk = request.POST.get('obj_pk', '')
    name = request.POST.get('obj_name', '')
    obj_type = request.POST.get('obj_type', '')
    if obj_type == 'user':
        if _has_perm(acting_user, ctnr, cy.ACTION_UPDATE, obj_class=CtnrUser):
            return add_user(request, ctnr, name, pk)
        else:
            messages.error(request,
                           'You do not have permission to perform this action')
            return HttpResponse(json.dumps({'redirect': 'yup'}))

    else:
        if _has_perm(acting_user, ctnr, cy.ACTION_UPDATE, obj_class=Ctnr):
            Klass = get_model(obj_type, obj_type)
            if pk == 'null':
                try:
                    if Klass.__name__ == 'Range':
                        return HttpResponse(json.dumps({
                            'error': 'Please select ranges from the '
                            'dropdown'}))
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
    return HttpResponse(json.dumps({'redirect': 'yup'}))


def add_user(request, ctnr, name, pk):
        confirmation = request.POST.get('confirmation', '')
        level = request.POST.get('level', '')
        user, newUser = User.objects.get_or_create(username=name)
        if newUser is True:
            if confirmation == 'false':
                return HttpResponse(json.dumps({
                    'acknowledge': 'This user is not in any other container. '
                    'Are you sure you want to create this user?'}))
            else:
                user.save()

        ctnruser, newCtnrUser = CtnrUser.objects.get_or_create(
            user_id=user.id, ctnr_id=ctnr.id, level=level)

        if newCtnrUser is False:
            return HttpResponse(json.dumps({
                'error': 'This user already exists in this container'}))

        ctnruser.save()
        ctnrusers = [CtnrUser.objects.select_related().get(
            ctnr_id=ctnr.id, user_id=user)]
        extra_cols, users = create_user_extra_cols(ctnr, ctnrusers)
        user_table = tablefy(users, users=True, extra_cols=extra_cols,
                             request=request)

        return HttpResponse(json.dumps({'user': user_table}))


class CtnrCreateView(CtnrView, CoreCreateView):
    def post(self, request, *args, **kwargs):
        ctnr_form = CtnrForm(request.POST)

        # Try to save the ctnr.
        try:
            # TODO: ACLs
            ctnr = ctnr_form.save(commit=False)
        except ValueError:
            return render(request, 'ctnr/ctnr_form.html', {'form': ctnr_form})

        ctnr.save()

        # Update ctnr-related session variables.
        request.session['ctnrs'].append(ctnr)
        ctnr_names = json.loads(request.session['ctnr_names_json'])
        ctnr_names.append(ctnr.name)
        request.session['ctnr_names_json'] = json.dumps(ctnr_names)

        return redirect(reverse('ctnr-detail', args=[ctnr.id]))

    def get(self, request, *args, **kwargs):
        return super(CtnrCreateView, self).get(request, *args, **kwargs)


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
