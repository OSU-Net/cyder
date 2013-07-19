import json

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render

from cyder.base.constants import LEVELS
from cyder.base.utils import qd_to_py_dict, tablefy
from cyder.core.ctnr.forms import CtnrForm, CtnrUserForm
from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.core.views import CoreCreateView, CoreDetailView


class CtnrView(object):
    model = Ctnr
    queryset = Ctnr.objects.all()
    form_class = CtnrForm


class CtnrDetailView(CtnrView, CoreDetailView):
    """
    Shows users, domains, and reverse domains within ctnr.
    """
    template_name = 'ctnr/ctnr_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CoreDetailView, self).get_context_data(**kwargs)
        ctnr = kwargs.get('object', False)
        if not ctnr:
            return context

        ctnrusers = ctnr.ctnruser_set.select_related('user', 'user__profile')
        extra_cols, users = create_user_extra_cols(ctnr, ctnrusers)
        user_table = tablefy(users, extra_cols=extra_cols, users=True)

        domains = ctnr.domains.filter(is_reverse=False)
        domain_table = tablefy(domains)

        rdomains = ctnr.domains.filter(is_reverse=True)
        rdomain_table = tablefy(rdomains)

        ranges = ctnr.ranges.all()
        range_table = tablefy(ranges)

        workgroups = ctnr.workgroups.all()
        workgroup_table = tablefy(workgroups)

        add_user_form = CtnrUserForm(initial={'ctnr': ctnr})
        return dict({
            'obj_type': 'ctnr',
            'user_table': user_table,
            'domain_table': domain_table,
            'rdomain_table': rdomain_table,
            'range_table': range_table,
            'workgroup_table': workgroup_table,
            'add_user_form': add_user_form
        }.items() + context.items())


def create_user_extra_cols(ctnr, ctnrusers):
    level_data = []
    action_data = []
    users = []
    extra_cols = [
        {'header': 'Level to %s' % ctnr.name, 'sort_field': 'user'},
        {'header': 'Actions', 'sort_field': 'user'}]

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
                'img': ['', '/media/img/minus.png', '/media/img/plus.png']
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
            'img': '/media/img/delete.png'
        })

    extra_cols[0]['data'] = level_data
    extra_cols[1]['data'] = action_data

    return extra_cols, users


def remove_user(request, ctnr_pk, user_pk):
    if request.session['level'] == 2:
        CtnrUser.objects.get(ctnr_id=ctnr_pk, user_id=user_pk).delete()
        return redirect(request.META.get('HTTP_REFERER', ''))
    else:
        messages.error(
            request, 'You do not have permission to perform this action')
        return redirect(request.META.get('HTTP_REFERER', ''))


def update_user_level(request, ctnr_pk, user_pk, lvl):
    if request.session['level'] == 2:
        ctnr_user = CtnrUser.objects.get(ctnr_id=ctnr_pk, user_id=user_pk)
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


def add_user(request, pk):
    """Add user to container."""
    ctnr = Ctnr.objects.get(id=pk)
    form = CtnrUserForm(qd_to_py_dict(request.POST))
    user = request.POST['user']
    if form.is_valid():
        # Create table so client can inside new row into user table.
        form.save()
        ctnrusers = [CtnrUser.objects.select_related().get(
            ctnr_id=ctnr.id, user_id=user)]
        extra_cols, users = create_user_extra_cols(ctnr, ctnrusers)
        user_table = tablefy(users, users=True, extra_cols=extra_cols)

        return HttpResponse(json.dumps({'user': user_table}))
    else:
        if request.POST['confirmation'] == 'true':
            user, _ = User.objects.get_or_create(username=request.POST['name'])
            user.save()

            ctnruser, _ = CtnrUser.objects.get_or_create(
                user_id=user.id, ctnr_id=ctnr.id, level=request.POST['level'])
            ctnruser.save()

            ctnrusers = [CtnrUser.objects.select_related().get(
                ctnr_id=ctnr.id, user_id=user.id)]
            extra_cols, users = create_user_extra_cols(ctnr, ctnrusers)
            user_table = tablefy(users, users=True, extra_cols=extra_cols)

            return HttpResponse(json.dumps({'user': user_table}))

        if [u'Select a valid choice. That choice is not one of the available '
                'choices.'] in [form.errors[err] for err in form.errors]:

            return HttpResponse(json.dumps({
                'acknowledge': 'This user is not in any other container. Are '
                'you sure you want to create this user?'}))

        else:
            return HttpResponse(json.dumps({
                'error': [form.errors[err] for err in form.errors]}))


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
        messages.error(request, "Could not change container, does not exist")
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

    if ctnr_user or global_ctnr_user:
        # Set session ctnr and level.
        prev = request.session['ctnr']
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
