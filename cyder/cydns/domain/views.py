from operator import itemgetter
import simplejson as json

from django.contrib import messages
from django.forms import ValidationError
from django.http import HttpResponse
from django.shortcuts import (get_object_or_404, render,
                              render_to_response, redirect)
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.domain.forms import DomainForm, DomainUpdateForm
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.soa.models import SOA
from cyder.cydns.srv.models import SRV
from cyder.cydns.txt.models import TXT
from cyder.base.utils import tablefy
from cyder.cydns.view.models import View
from cyder.cydns.views import CydnsCreateView, CydnsDeleteView, CydnsListView


class DomainView(object):
    model = Domain
    queryset = Domain.objects.all().order_by('name')
    form_class = DomainForm
    extra_context = {'record_type': 'domain'}


class DomainListView(DomainView, CydnsListView):
    queryset = Domain.objects.filter(is_reverse=False)


class DomainDeleteView(DomainView, CydnsDeleteView):
    """ """


class DomainDetailView(DomainView, DetailView):
    template_name = "domain/domain_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        domain = kwargs.get('object', False)
        if not domain:
            return context

        # TODO this process can be generalized. Not very high priority.
        domain_table = tablefy((domain,), views=True)

        mx_objects = domain.mx_set.all().order_by('label')
        mx_table = tablefy(mx_objects, views=True)

        srv_objects = domain.srv_set.all().order_by('label')
        srv_table = tablefy(srv_objects, views=True)

        txt_objects = domain.txt_set.all().order_by('label')
        txt_table = tablefy(txt_objects, views=True)

        sshfp_objects = domain.sshfp_set.all().order_by('label')
        sshfp_table = tablefy(sshfp_objects, views=True)

        cname_objects = domain.cname_set.order_by('label')
        if cname_objects.count() > 50:
            cname_views = False
        else:
            cname_views = True
        cname_table = tablefy(cname_objects, cname_views)

        # TODO, include Static Registrations
        ptr_objects = domain.ptr_set.all().order_by('ip_str')
        ptr_table = tablefy(ptr_objects, views=True)

        # TODO, include Static Registrations
        all_static_intr = StaticInterface.objects.all()
        intr_objects = domain.staticinterface_set.all().order_by(
            'name').order_by('ip_str')
        intr_table = tablefy(intr_objects, views=True)

        # Takes too long to load more than 50.
        address_objects = domain.addressrecord_set.all().order_by('label')
        if address_objects.count() > 50:
            address_views = False
        else:
            address_views = True
        address_table = tablefy(address_objects, address_views)

        ns_objects = domain.nameserver_set.all().order_by('server')
        ns_table = tablefy(ns_objects, views=True)

        # Join the two dicts
        return dict({
            'address_views': address_views,
            'cname_views': cname_views,

            'address_table': address_table,
            'cname_table': cname_table,
            'domain_table': domain_table,
            'intr_table': intr_table,
            'mx_table': mx_table,
            'ns_table': ns_table,
            'ptr_table': ptr_table,
            'srv_table': srv_table,
            'txt_table': txt_table,
            'sshfp_table': sshfp_table,
        }.items() + context.items())


class DomainCreateView(DomainView, CreateView):
    model_form = DomainForm

    def post(self, request, *args, **kwargs):
        domain_form = DomainForm(request.POST)
        # Try to create the domain. Catch all exceptions.
        try:
            domain = domain_form.save()
        except ValueError, e:
            return render(request, "cydns/cydns_form.html", {
                'form': domain_form,
                'form_title': 'Create Domain'
            })

        try:
            if domain.master_domain and domain.master_domain.soa:
                domain.soa = domain.master_domain.soa
                domain.save()
        except ValidationError, e:
            return render(request, "cydns/cydns_form.html", {'form':
                                                               domain_form, 'form_title': 'Create Domain'})
        # Success. Redirect.
        messages.success(request, "{0} was successfully created.".
                         format(domain.name))
        return redirect(domain)

    def get(self, request, *args, **kwargs):
        domain_form = DomainForm()
        return render(request, "cydns/cydns_form.html", {'form': domain_form,
                                                           'form_title': 'Create Domain'})


class DomainUpdateView(DomainView, UpdateView):
    form_class = DomainUpdateForm
    template_name = "cydns/cydns_update.html"

    def post(self, request, *args, **kwargs):
        domain = get_object_or_404(Domain, pk=kwargs.get('pk', 0))
        try:
            domain_form = DomainUpdateForm(request.POST)
            new_soa_pk = domain_form.data.get('soa', None)
            delegation_status = domain_form.data.get('delegated', False)

            if new_soa_pk:
                new_soa = get_object_or_404(SOA, pk=new_soa_pk)
            else:
                new_soa = None

            if delegation_status == 'on':
                new_delegation_status = True
            else:
                new_delegation_status = False

            updated = False
            if domain.soa != new_soa:
                domain.soa = new_soa
                updated = True
            if domain.delegated != new_delegation_status:
                domain.delegated = new_delegation_status
                updated = True

            if updated:
                domain.save()  # Major exception handling logic goes here.
        except ValidationError, e:
            domain_form = DomainUpdateForm(instance=domain)
            messages.error(request, str(e))
            return render(request, "domain/domain_update.html", {"form":
                                                                 domain_form})

        messages.success(request, '{0} was successfully updated.'.
                         format(domain.name))

        return redirect(domain)


class ReverseDomainListView(DomainView, CydnsListView):
    extra_context = {'record_type': 'reverse_domain'}
    queryset = Domain.objects.filter(is_reverse=True).order_by('name')


def domain_sort(domains):
    """
    This is soooooo slow.
    """

    roots = domains.filter(master_domain=None)
    ordered = []
    for root in roots:
        ordered += build_tree(root, domains)
    return ordered


def build_tree(root, domains):
    if len(domains) == 0:
        return root
    ordered = [root]
    children = domains.filter(master_domain=root)
    for child in children:
        ordered += build_tree(child, domains)
    return ordered


def get_all_domains(request):
    domains = [domain.name for domain in Domain.objects.all()]
    return HttpResponse(json.dumps(domains))
