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
        domain_headers, domain_matrix, domain_urls = tablefy((domain,),
                                                             views=True)

        mx_objects = domain.mx_set.all().order_by('label')
        mx_headers, mx_matrix, mx_urls = tablefy(mx_objects, views=True)

        srv_objects = domain.srv_set.all().order_by('label')
        srv_headers, srv_matrix, srv_urls = tablefy(srv_objects, views=True)

        txt_objects = domain.txt_set.all().order_by('label')
        txt_headers, txt_matrix, txt_urls = tablefy(txt_objects, views=True)

        sshfp_objects = domain.sshfp_set.all().order_by('label')
        sshfp_headers, sshfp_matrix, sshfp_urls = tablefy(sshfp_objects,
                                                          views=True)

        cname_objects = domain.cname_set.order_by('label')
        if cname_objects.count() > 50:
            cname_views = False
        else:
            cname_views = True
        cname_headers, cname_matrix, cname_urls = tablefy(cname_objects,
                                                          cname_views)

        # TODO, include Static Registrations
        ptr_objects = domain.ptr_set.all().order_by('ip_str')
        ptr_headers, ptr_matrix, ptr_urls = tablefy(ptr_objects, views=True)

        # TODO, include Static Registrations
        all_static_intr = StaticInterface.objects.all()
        intr_objects = domain.staticinterface_set.all().order_by(
            'name').order_by('ip_str')
        intr_headers, intr_matrix, intr_urls = tablefy(intr_objects, views=True)

        address_objects = domain.addressrecord_set.all().order_by('label')

        # Takes too long to load more than 50.
        if address_objects.count() > 50:
            adr_views = False
        else:
            adr_views = True
        adr_headers, adr_matrix, adr_urls = tablefy(address_objects, adr_views)

        ns_objects = domain.nameserver_set.all().order_by('server')
        ns_headers, ns_matrix, ns_urls = tablefy(ns_objects, views=True)

        # Join the two dicts
        context = dict({
            "address_headers": adr_headers,
            "address_matrix": adr_matrix,
            "address_urls": adr_urls,
            "address_views": adr_views,

            "cname_headers": cname_headers,
            "cname_matrix": cname_matrix,
            "cname_urls": cname_urls,
            "cname_views": cname_views,

            "domain_headers": domain_headers,
            "domain_matrix": domain_matrix,
            "domain_urls": domain_urls,

            "intr_headers": intr_headers,
            "intr_matrix": intr_matrix,
            "intr_urls": intr_urls,

            "mx_headers": mx_headers,
            "mx_matrix": mx_matrix,
            "mx_urls": mx_urls,

            "ns_headers": ns_headers,
            "ns_matrix": ns_matrix,
            "ns_urls": ns_urls,

            "ptr_headers": ptr_headers,
            "ptr_matrix": ptr_matrix,
            "ptr_urls": ptr_urls,

            "srv_headers": srv_headers,
            "srv_matrix": srv_matrix,
            "srv_urls": srv_urls,

            "txt_headers": txt_headers,
            "txt_matrix": txt_matrix,
            "txt_urls": txt_urls,

            "sshfp_headers": sshfp_headers,
            "sshfp_matrix": sshfp_matrix,
            "sshfp_urls": sshfp_urls,
        }.items() + context.items())

        return context


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
