import json

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render

from cyder.base.constants import LEVELS
from cyder.base.utils import qd_to_py_dict, tablefy
from cyder.core.ctnr.forms import CtnrForm, CtnrUserForm
from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.core.views import (CoreCreateView, CoreDetailView, CoreDeleteView,
                              CoreListView, CoreUpdateView)


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

        # Add user levels of ctnr to user table.
        users = ctnr.users.all()
        extra_cols = [{'header': 'Level to %s' % ctnr.name}]
        extra_cols[0]['data'] = [
            {'value': LEVELS[CtnrUser.objects.get(user=user, ctnr=ctnr).level],
             'url': ''} for user in users]
        user_table = tablefy(users, users=True, extra_cols=extra_cols)

        domains = ctnr.domains.filter(is_reverse=False)
        domain_table = tablefy(domains)

        rdomains = ctnr.domains.filter(is_reverse=True)
        rdomain_table = tablefy(rdomains)

        add_user_form = CtnrUserForm(initial={'ctnr': ctnr})
        return dict({
            'user_table': user_table,
            'domain_table': domain_table,
            'rdomain_table': rdomain_table,
            'add_user_form': add_user_form
        }.items() + context.items())


def add_user(request, pk):
    """Add user to container."""
    form = CtnrUserForm(qd_to_py_dict(request.POST))
    if form.is_valid():
        form.save()
        return HttpResponse()
    else:
        return HttpResponse(
            json.dumps({'error': [form.errors[err] for err in form.errors]}))


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


class CtnrDeleteView(CtnrView, CoreDeleteView):
    """"""


class CtnrUpdateView(CtnrView, CoreUpdateView):
    """"""


class CtnrListView(CtnrView, CoreListView):
    """"""
    template_name = 'ctnr/ctnr_list.html'


class CtnrUserView(object):
    model = CtnrUser
    queryset = CtnrUser.objects.all()
    form_class = CtnrUserForm


class CtnrUserCreateView(CtnrUserView, CoreCreateView):
    """"""
    def get_queryset(self):
        return Ctnr.objects.get(id=self.args[0])


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

    return redirect(referer)
