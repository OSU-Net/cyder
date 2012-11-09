import operator
import simplejson as json

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q
from django.forms.util import ErrorDict, ErrorList
from django.http import Http404, HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, redirect, render

from cyder.base.views import BaseListView, BaseDetailView, BaseCreateView
from cyder.base.views import BaseUpdateView, BaseDeleteView
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
from cyder.cydns.srv.forms import FQDNSRVForm, SRVForm
from cyder.cydns.srv.models import SRV
from cyder.cydns.txt.forms import FQDNTXTForm, TXTForm
from cyder.cydns.txt.models import TXT
from cyder.cydns.utils import ensure_label_domain, prune_tree, slim_form
from cyder.cydns.view.models import View


def cydns_record_view(request, record_type=None):
    """
    List, create, update view in one for a flatter heirarchy.
    """
    # Infer record_type from URL, saves trouble of having to specify
    # kwargs everywhere in the dispatchers.
    record_type = record_type or request.path.split('/')[2]

    domains = json.dumps([domain.name for domain in  # TODO: ACLs
                          Domain.objects.filter(is_reverse=False)]),

    # Get the record form.
    Klass, FormKlass, FQDNFormKlass = get_klasses(record_type)

    # Get the object if updating.
    record = None
    action = request.GET.get('action', None)
    pk = request.GET.get('pk', None)
    if pk:
        record = get_object_or_404(Klass, pk=pk)  # TODO: ACLs
        form = FQDNFormKlass(instance=record)
    else:
        form = FQDNFormKlass()

    if request.method == 'POST':
        # May be mutating query dict for FQDN resolution and labels.
        qd = request.POST.copy()
        orig_qd = request.POST.copy()

        if action == 'delete':
            record.delete()
            return redirect(record.get_list_url())

        # Create initial FQDN form.
        if record:
            form = FQDNFormKlass(qd, instance=record)
        else:
            form = FQDNFormKlass(qd)

        # Resolve fqdn to domain and attach to record object.
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
                return render(request, 'cydns/cydns_record_view.html', {
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
            except ValidationError as e:
                error = True
            return redirect(record.get_list_url())
        else:
            error = True
        if error:
            # Revert domain if not valid.
            prune_tree(domain)
            return_form = FQDNFormKlass(orig_qd)
            return_form._errors = form._errors
            form = return_form

    paginator = Paginator(Klass.objects.all(), 3)
    page = request.GET.get('page')
    try:
        object_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        object_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        object_list = paginator.page(paginator.num_pages)

    return render(request, 'cydns/cydns_record_view.html', {
        'form': form,
        'obj': record,
        'object_list': object_list,
        'domains': domains,
        'record_type': record_type,
        'pk': pk,
    })


def cydns_get_record(request):
    """
    Update view called asynchronously from the list_create view
    """
    record_type = request.GET.get('record_type', '')
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
    query = request.GET.get('term', '')
    if not (record_type and query):
        raise Http404

    Klass, FormKlass, FQDNFormKlass = get_klasses(record_type)

    # Try to match query to records.
    mega_filter = [Q(**{"{0}__icontains".format(field): query}) for field in
                   Klass.search_fields]
    mega_filter = reduce(operator.or_, mega_filter)

    records = Klass.objects.filter(mega_filter)[:15]
    records = [{'label': str(record), 'pk': record.pk} for record in records]

    return HttpResponse(json.dumps(records))


class CydnsListView(BaseListView):
    """ """
    template_name = 'cydns/cydns_list.html'


class CydnsDetailView(BaseDetailView):
    """ """
    template_name = 'cydns/cydns_detail.html'


class CydnsCreateView(BaseCreateView):
    """ """
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
    """ """
    template_name = 'cydns/cydns_confirm_delete.html'
    succcess_url = '/cydns/'


def get_klasses(record_type):
    """
    Given record type string, grab its class and forms.
    """
    return {
        'address_record': (AddressRecord, AddressRecordForm, AddressRecordFQDNForm),
        'cname': (CNAME, CNAMEForm, CNAMEFQDNForm),
        'domain': (Domain, DomainForm, DomainForm),
        'mx': (MX, MXForm, FQDNMXForm),
        'nameserver': (Nameserver, NameserverForm, NameserverForm),
        'ptr': (PTR, PTRForm, PTRForm),
        'soa': (SOA, SOAForm, SOAForm),
        'srv': (SRV, SRVForm, FQDNSRVForm),
        'txt': (TXT, TXTForm, FQDNTXTForm),
    }.get(record_type, (None, None, None))
