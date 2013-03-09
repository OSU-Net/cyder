import json as json

from django.core.exceptions import ValidationError
from django.forms.util import ErrorDict, ErrorList
from django.shortcuts import get_object_or_404, redirect, render

import cyder as cy
from cyder.base.utils import (do_sort, make_paginator, _filter, tablefy)
from cyder.base.views import (BaseCreateView, BaseDeleteView,
                              BaseDetailView, BaseListView, BaseUpdateView,
                              cy_delete, get_update_form, search_obj,
                              table_update)
from cyder.core.cyuser.utils import perm, perm_soft
from cyder.cydns.address_record.forms import (AddressRecordForm,
                                              AddressRecordFQDNForm)
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.forms import CNAMEForm, CNAMEFQDNForm
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.domain.forms import DomainForm
from cyder.cydns.mx.forms import FQDNMXForm, MXForm
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.forms import NameserverForm
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.ptr.forms import PTRForm
from cyder.cydns.ptr.models import PTR
from cyder.cydns.soa.forms import SOAForm
from cyder.cydns.soa.models import SOA
from cyder.cydns.sshfp.forms import FQDNSSHFPForm, SSHFPForm
from cyder.cydns.sshfp.models import SSHFP
from cyder.cydns.srv.forms import SRVForm
from cyder.cydns.srv.models import SRV
from cyder.cydns.txt.forms import FQDNTXTForm, TXTForm
from cyder.cydns.txt.models import TXT
from cyder.cydns.utils import ensure_label_domain, prune_tree, slim_form


def get_klasses(record_type):
    """
    Given record type string, grab its class and forms.
    """
    return {
        'address_record': (AddressRecord, AddressRecordForm,
                           AddressRecordFQDNForm),
        'cname': (CNAME, CNAMEForm, CNAMEFQDNForm),
        'domain': (Domain, DomainForm, DomainForm),
        'mx': (MX, MXForm, FQDNMXForm),
        'nameserver': (Nameserver, NameserverForm, NameserverForm),
        'ptr': (PTR, PTRForm, PTRForm),
        'soa': (SOA, SOAForm, SOAForm),
        'srv': (SRV, SRVForm, SRVForm),
        'sshfp': (SSHFP, SSHFPForm, FQDNSSHFPForm),
        'txt': (TXT, TXTForm, FQDNTXTForm),
    }.get(record_type, (None, None, None))


def cydns_view(request, pk=None):
    """List, create, update view in one for a flatter heirarchy. """
    # Infer record_type from URL, saves trouble of having to specify
    # kwargs everywhere in the dispatchers.
    record_type = request.path.split('/')[2]

    domains = json.dumps([domain.name for domain in
                          Domain.objects.filter(is_reverse=False)
                          if perm_soft(request, cy.ACTION_UPDATE,
                                       obj=domain)]),

    # Get the record form.
    Klass, FormKlass, FQDNFormKlass = get_klasses(record_type)

    # Get the object if updating.
    record = get_object_or_404(Klass, pk=pk) if pk else None
    form = FQDNFormKlass(instance=record)

    if request.method == 'POST':
        # Create initial FQDN form.
        form = FQDNFormKlass(request.POST, instance=record)

        qd, domain, errors = _fqdn_to_domain(request.POST.copy())
        # Validate form.
        if errors:
            fqdn_form = FQDNFormKlass(request.POST)
            fqdn_form._errors = ErrorDict()
            fqdn_form._errors['__all__'] = ErrorList(errors)
            return render(request, 'cydns/cydns_view.html', {
                'domain': domains,
                'form': fqdn_form,
                'record_type': record_type,
                'pk': pk,
                'obj': record
            })
        else:
            form = FormKlass(qd, instance=record)

        try:
            if perm(request, cy.ACTION_CREATE, obj=record):
                record = form.save()
                # If domain, add to current ctnr.
                if record_type == 'domain':
                    request.session['ctnr'].domains.add(record)
                    return redirect(record.get_list_url())
        except (ValidationError, ValueError):
            form = _revert(domain, request.POST, form, FQDNFormKlass)

    object_list = _filter(request, Klass)
    page_obj = make_paginator(
        request, do_sort(request, object_list), 50)

    return render(request, 'cydns/cydns_view.html', {
        'form': form,
        'obj': record,
        'page_obj': page_obj,
        'object_table': tablefy(page_obj, views=True),
        'domains': domains,
        'record_type': record_type,
        'pk': pk,
    })


def _revert(domain, orig_qd, orig_form, FQDNFormKlass):
    """Revert domain if not valid."""
    prune_tree(domain)
    form = FQDNFormKlass(orig_qd)
    form._errors = orig_form._errors
    return form


def _fqdn_to_domain(qd):
    """Resolve FQDN to domain and attach to record object. """
    domain = None
    if 'fqdn' in qd:
        fqdn = qd.pop('fqdn')[0]
        try:
            # Call prune tree later if error, else domain leak.
            label, domain = ensure_label_domain(fqdn)
        except ValidationError, e:
            return None, None, e.messages

        qd['label'], qd['domain'] = label, str(domain.pk)
    return qd, domain, None


def cydns_delete(request, pk):
    return cy_delete(request, pk, get_klasses)


def cydns_get_update_form(request):
    return get_update_form(request, get_klasses)


def cydns_table_update(request, pk, object_type=None):
    return table_update(request, pk, get_klasses, object_type)


def cydns_search_obj(request):
    return search_obj(request, get_klasses)


def cydns_index(request):
    domains = request.session['ctnr'].domains.all()

    addressrecord_count = 0
    cname_count = 0
    mx_count = 0
    ns_count = 0
    ptr_count = 0
    srv_count = 0
    sshfp_count = 0
    txt_count = 0

    soa_list = []
    for domain in domains:
        addressrecord_count += domain.addressrecord_set.count()
        cname_count += domain.cname_set.count()
        mx_count += domain.mx_set.count()
        ns_count += domain.nameserver_set.count()
        ptr_count += domain.ptr_set.count()
        srv_count += domain.srv_set.count()
        sshfp_count += domain.sshfp_set.count()
        txt_count += domain.txt_set.count()

        if domain.soa not in soa_list:
            soa_list.append(domain.soa)

    counts = [
        ('Domains', domains.filter(is_reverse=False).count()),
        ('Reverse Domains', domains.filter(is_reverse=True).count()),
        ('Address Records', addressrecord_count),
        ('CNAMEs', cname_count),
        ('MXs', mx_count),
        ('PTRs', ptr_count),
        ('SRVs', srv_count),
        ('SSHFPs', sshfp_count),
        ('TXTs', txt_count),
        ('SOAs', len(soa_list)),
        ('Nameservers', ns_count),
    ]

    return render(request, 'cydns/cydns_index.html', {'counts': counts})


class CydnsListView(BaseListView):
    template_name = 'cydns/cydns_list.html'


class CydnsDetailView(BaseDetailView):
    template_name = 'cydns/cydns_detail.html'


class CydnsCreateView(BaseCreateView):
    template_name = 'cydns/cydns_form.html'

    def get_form(self, form_class):
        form = super(CydnsCreateView, self).get_form(form_class)
        domain_pk = self.kwargs.get('domain', False)

        # The use of slim_form makes my eyes bleed and stomach churn.
        if domain_pk:
            form = slim_form(domain_pk=domain_pk, form=form)

        reverse_domain_pk = self.kwargs.get('reverse_domain', False)
        if reverse_domain_pk:
            slim_form(reverse_domain_pk=reverse_domain_pk, form=form)

        # Filtering domain selection here.
        # form.fields['domain'].queryset = Domain.objects.filter(name =
        # 'foo.com') will make query set controllable.
        # Permissions in self.request.

        return form


class CydnsUpdateView(BaseUpdateView):
    template_name = 'cydns/cydns_form.html'


class CydnsDeleteView(BaseDeleteView):
    template_name = 'cydns/cydns_confirm_delete.html'
    succcess_url = '/cydns/'
