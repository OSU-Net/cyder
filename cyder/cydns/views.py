import operator
import simplejson as json

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


def cydns_list_create_record(request, record_type=None, pk=None):
    """
    List, create, update view in one for a flatter heirarchy.
    """
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
                return render(request, 'cydns/cydns_list_record.html', {
                    'domain': domains,
                    'form': fqdn_form,
                    'record_type': record_type,
                    'record_pk': pk,
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
            return_form = FQDNFormKlass(instance=record)
        else:
            error = True
        if error:
            # Revert domain if not valid.
            prune_tree(domain)
            return_form = FormKlass(orig_qd)
            return_form._errors = form._errors
            form = return_form

    return render(request, 'cydns/cydns_list_record.html', {
        # TODO: ACLs
        'domains': domains,
        'form': form,
        'record_type': record_type,
        'record_pk': pk,
        'obj': record,
        'object_list': Klass.objects.all()[0:20]
    })


def cydns_update_record(request):
    """
    Update view called asynchronously from the list_create view
    """
    record_type = request.GET.get('record_type', '')
    record_pk = request.GET.get('record_pk', '')
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

    return HttpResponse(form.as_p())


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

        # Removes "Hold down the...." help texts for specified fields for form.
        remove_message = unicode(' Hold down "Control", or "Command" on a Mac,'
                                 'to select more than one.')
        for field in form.fields:
            if field in form.base_fields:
                if form.base_fields[field].help_text:
                    new_text = form.base_fields[field].help_text.replace(
                        remove_message, '')
                    new_text = new_text.strip()
                    form.base_fields[field].help_text = new_text
        return form


class CydnsUpdateView(BaseUpdateView):
    template_name = 'cydns/cydns_form.html'

    def get_form(self, form_class):
        form = super(CydnsUpdateView, self).get_form(form_class)
        # Removes "Hold down the...." help texts for specified fields for form.
        remove_message = unicode(' Hold down "Control", or "Command" on a Mac,'
                                 'to select more than one.')

        for field in form.fields:
            if field in form.base_fields:
                if form.base_fields[field].help_text:
                    new_text = form.base_fields[field].help_text.replace(
                        remove_message, '')
                    new_text = new_text.strip()
                    form.base_fields[field].help_text = new_text
        return form


class CydnsDeleteView(BaseDeleteView):
    """ """
    template_name = 'cydns/cydns_confirm_delete.html'
    succcess_url = '/cydns/'


def get_klasses(record_type):
    if record_type == 'address_record':
        Klass = AddressRecord
        FormKlass = AddressRecordForm
        FQDNFormKlass = AddressRecordFQDNForm
    elif record_type == 'cname':
        Klass = CNAME
        FormKlass = CNAMEForm
        FQDNFormKlass = CNAMEFQDNForm
    elif record_type == 'domain':
        Klass = Domain
        FormKlass = DomainForm
        FQDNFormKlass = DomainForm
    elif record_type == 'mx':
        Klass = MX
        FormKlass = MXForm
        FQDNFormKlass = FQDNMXForm
    elif record_type == 'nameserver':
        Klass = Nameserver
        FormKlass = NameserverForm
        FQDNFormKlass = NameserverForm
    elif record_type == 'ptr':
        Klass = PTR
        FormKlass = PTRForm
        FQDNFormKlass = PTRForm
    elif record_type == 'soa':
        Klass = SOA
        FormKlass = SOAForm
        FQDNFormKlass = SOAForm
    elif record_type == 'srv':
        Klass = SRV
        FormKlass = SRVForm
        FQDNFormKlass = FQDNSRVForm
    elif record_type == 'txt':
        Klass = TXT
        FormKlass = TXTForm
        FQDNFormKlass = FQDNTXTForm
    else:
        Klass, FormKlass, FQDNFormKlass = None, None, None

    return Klass, FormKlass, FQDNFormKlass
