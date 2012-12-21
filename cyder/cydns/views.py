import simplejson as json

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms.models import model_to_dict
from django.forms.util import ErrorDict, ErrorList
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from cyder.base.utils import (do_sort, make_paginator,
                              make_megafilter, qd_to_py_dict, tablefy)
from cyder.base.views import (BaseCreateView, BaseDeleteView, BaseDetailView,
                              BaseListView, BaseUpdateView)
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


def cydns_view(request, pk=None):
    """
    List, create, update view in one for a flatter heirarchy.
    """
    # Infer record_type from URL, saves trouble of having to specify
    # kwargs everywhere in the dispatchers.
    record_type = request.path.split('/')[2]

    domains = json.dumps([domain.name for domain in  # TODO: ACLs
                          Domain.objects.filter(is_reverse=False)]),

    # Get the record form.
    Klass, FormKlass, FQDNFormKlass = get_klasses(record_type)

    # Get the object if updating.
    record = None
    if pk:
        record = get_object_or_404(Klass, pk=pk)  # TODO: ACLs
        form = FQDNFormKlass(instance=record)
    else:
        form = FQDNFormKlass()

    if request.method == 'POST':
        # May be mutating query dict for FQDN resolution and labels.
        qd = request.POST.copy()
        orig_qd = request.POST.copy()

        # Create initial FQDN form.
        if record:
            form = FQDNFormKlass(qd, instance=record)
        else:
            form = FQDNFormKlass(qd)

        # Resolve FQDN to domain and attach to record object.
        domain = None
        if 'fqdn' in qd:
            fqdn = qd.pop('fqdn')[0]
            try:
                # Call prune tree later if error, else domain leak.
                label, domain = ensure_label_domain(fqdn)
            except ValidationError, e:
                fqdn_form = FQDNFormKlass(orig_qd)
                fqdn_form._errors = ErrorDict()
                fqdn_form._errors['__all__'] = ErrorList(e.messages)
                return render(request, 'cydns/cydns_view.html', {
                    'domain': domains,
                    'form': fqdn_form,
                    'record_type': record_type,
                    'pk': pk,
                    'obj': record
                })
            qd['label'], qd['domain'] = label, str(domain.pk)

            # FQDN form to resolved domain form.
            if pk:
                # ACLs here.
                form = FormKlass(qd, instance=record)
            else:
                form = FormKlass(qd)

        # Validate form.
        error = False
        if form.is_valid():
            try:
                record = form.save()
                # If domain, add to current ctnr.
                if record_type == 'domain':
                    request.session['ctnr'].domains.add(record)

                return redirect(record.get_list_url())
            except ValidationError as e:
                error = True
        else:
            error = True
        if error:
            # Revert domain if not valid.
            prune_tree(domain)
            return_form = FQDNFormKlass(orig_qd)
            return_form._errors = form._errors
            form = return_form

    # Apply filters.
    object_list = Klass.objects.all()
    if request.GET.get('filter'):
        object_list = object_list.filter(
            make_megafilter(Klass, request.GET.get('filter')))

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


def cydns_delete(request, pk):
    """Delete view."""
    # Infer record_type from URL, saves trouble of having to specify
    # kwargs everywhere in the dispatchers.
    record_type = request.path.split('/')[2]

    # Get the Klass.
    Klass, FormKlass, FQDNFormKlass = get_klasses(record_type)

    record = get_object_or_404(Klass, pk=pk)
    record.delete()
    return redirect(record.get_list_url())


def cydns_get_record(request):
    """
    Update view called asynchronously from the list_create view
    """
    record_type = request.GET.get('object_type', '')
    record_pk = request.GET.get('pk', '')
    if not (record_type and record_pk):
        raise Http404

    Klass, FormKlass, FQDNFormKlass = get_klasses(record_type)

    # Get the object if updating.
    try:
        # ACLs should be applied here.
        record = Klass.objects.get(pk=record_pk)
        form = FQDNFormKlass(instance=record)
    except ObjectDoesNotExist:
        raise Http404

    return HttpResponse(json.dumps({'form': form.as_p(), 'pk': record.pk}))


def cydns_search_record(request):
    """
    Returns a list of records of 'record_type' matching 'term'.
    """
    record_type = request.GET.get('record_type', '')
    term = request.GET.get('term', '')
    if not (record_type and term):
        raise Http404

    Klass, FormKlass, FQDNFormKlass = get_klasses(record_type)

    records = Klass.objects.filter(make_megafilter(Klass, term))[:15]
    records = [{'label': str(record), 'pk': record.pk} for record in records]

    return HttpResponse(json.dumps(records))


def table_update(request, pk, object_type=None):
    """
    Called from editableGrid tables when updating a field. Try to update
    an object specified by pk with the post data.
    """
    # Infer object_type from URL, saves trouble of having to specify
    # kwargs everywhere in the dispatchers.
    object_type = object_type or request.path.split('/')[2]

    Klass, FormKlass, FQDNFormKlass = get_klasses(object_type)
    obj = get_object_or_404(Klass, pk=pk)  # TODO: ACLs

    # Put updated object into form.
    form = FQDNFormKlass(instance=obj)

    qd = request.POST.copy()
    if 'fqdn' in qd:
        fqdn = qd.pop('fqdn')[0]
        try:
            # Call prune tree later if error, else domain leak.
            label, domain = ensure_label_domain(fqdn)
        except ValidationError, e:
            return HttpResponse(json.dumps({'error': e.messages}))
        qd['label'], qd['domain'] = label, str(domain.pk)

    form = FormKlass(model_to_post(qd, obj), instance=obj)
    if form.is_valid():
        form.save()
        return HttpResponse()
    else:
        return HttpResponse(json.dumps({'error': form.errors}))


def model_to_post(post, obj):
    """
    Updates request's POST dictionary with values from object, for update
    purposes.
    """
    ret = qd_to_py_dict(post)
    # Copy model values to dict.
    for k, v in model_to_dict(obj).iteritems():
        if k not in post:
            ret[k] = v
    return ret


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
