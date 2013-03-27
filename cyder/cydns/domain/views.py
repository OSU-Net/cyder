import json

from django.http import HttpResponse
from django.views.generic import DetailView

from cyder.base.utils import tablefy
from cyder.cydns.domain.models import Domain
from cyder.cydns.domain.forms import DomainForm


class DomainView(object):
    model = Domain
    queryset = Domain.objects.all().order_by('name')
    form_class = DomainForm
    extra_context = {'record_type': 'domain'}


class DomainDetailView(DomainView, DetailView):
    template_name = "domain/domain_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        domain = kwargs.get('object', False)
        if not domain:
            return context

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
            'form': self.form_class,
            'record_type': 'domain',
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
