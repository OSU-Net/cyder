import operator
import simplejson as json

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q
from django.forms.util import ErrorDict, ErrorList
from django.http import Http404, HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, redirect, render

from cyder.cydns.address_record.forms import (AddressRecordForm,
                                              AddressRecordFQDNForm)
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.forms import CNAMEForm, CNAMEFQDNForm
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.mx.forms import FQDNMXForm, MXForm
from cyder.cydns.mx.models import MX
from cyder.cydns.ptr.forms import PTRForm
from cyder.cydns.ptr.models import PTR
from cyder.cydns.soa.forms import SOAForm
from cyder.cydns.soa.models import SOA
from cyder.cydns.srv.forms import FQDNSRVForm, SRVForm
from cyder.cydns.srv.models import SRV
from cyder.cydns.txt.forms import FQDNTXTForm, TXTForm
from cyder.cydns.txt.models import TXT
from cyder.cydns.utils import ensure_label_domain, prune_tree
from cyder.cydns.view.models import View


def get_klasses(record_type):
    if record_type == "A":
        Klass = AddressRecord
        FormKlass = AddressRecordForm
        FQDNFormKlass = AddressRecordFQDNForm
    elif record_type == "PTR":
        Klass = PTR
        FormKlass = PTRForm
        FQDNFormKlass = PTRForm
    elif record_type == "SRV":
        Klass = SRV
        FormKlass = SRVForm
        FQDNFormKlass = FQDNSRVForm
    elif record_type == "CNAME":
        Klass = CNAME
        FormKlass = CNAMEForm
        FQDNFormKlass = CNAMEFQDNForm
    elif record_type == "TXT":
        Klass = TXT
        FormKlass = TXTForm
        FQDNFormKlass = FQDNTXTForm
    elif record_type == "MX":
        Klass = MX
        FormKlass = MXForm
        FQDNFormKlass = FQDNMXForm
    elif record_type == "SOA":
        Klass = SOA
        FormKlass = SOAForm
        FQDNFormKlass = SOAForm
    else:
        Klass, FormKlass, FQDNFormKlass = None, None, None

    return Klass, FormKlass, FQDNFormKlass


def cydns_record_search_ajax(request):
    """
    This function will return a list of records matching the 'query' of type
    'record_type'.
    """
    query = request.GET.get('term', '')
    record_type = request.GET.get('record_type', '')
    if not (query and record_type):
        raise Http404

    Klass, FormKlass, FQDNFormKlass = get_klasses(record_type)

    # Check if query matches any of the fields of the object.
    mega_filter = [Q(**{"{0}__icontains".format(field): query}) for field in
                   Klass.search_fields]
    mega_filter = reduce(operator.or_, mega_filter)

    records = Klass.objects.filter(mega_filter)[:15]
    records = [{'label': str(record), 'pk': record.pk} for record in records]

    return HttpResponse(json.dumps(records))


def cydns_record_form_ajax(request):
    """
    Gets form for updating or creating a record type.
    """
    record_type = request.GET.get('record_type', 'A')
    record_pk = request.GET.get('record_pk', '')
    if not record_type:
        raise Http404

    Klass, FormKlass, FQDNFormKlass = get_klasses(record_type)

    if record_pk:
        # Get the object if updating.
        try:
            # ACLs should be applied here.
            object_ = Klass.objects.get(pk=record_pk)
            form = FQDNFormKlass(instance=object_)
        except ObjectDoesNotExist:
            object_ = None
            form = FQDNFormKlass()
            record_pk = ''
    else:
        # Create form.
        object_ = None
        form = FQDNFormKlass()

    if record_pk:
        message = ("Change some data and press 'Commit' to update the "
                   "%s" % record_type)
    else:
        message = ("Enter some data and press 'Commit' to update the "
                   "%s" % record_type)

    return render(request, 'master_form/ajax_form.html', {
        'form': form,
        'record_type': record_type,
        'record_pk': record_pk,
        'message': message,
        'obj': object_
    })


def cydns_record(request, record_type='', record_pk=''):
    if request.method == 'GET':
        record_type = str(request.GET.get('record_type', ''))
        record_pk = str(request.GET.get('record_pk', ''))
        domains = Domain.objects.filter(is_reverse=False)
        return render(request, 'master_form/master_form.html', {
            'domains': json.dumps([domain.name for domain in domains]),
            'record_type': record_type,
            'record_pk': record_pk,
        })

    qd = request.POST.copy()  # Make qd mutable.
    orig_qd = request.POST.copy()  # If errors, use qd to populate form.

    record_type = qd.pop('record_type', '')
    if record_type:
        record_type = record_type[0]
    else:
        raise Http404

    record_pk = qd.pop('record_pk', '')
    if record_pk:
        record_pk = record_pk[0]

    Klass, FormKlass, FQDNFormKlass = get_klasses(record_type)
    if 'fqdn' in qd:
        fqdn = qd.pop('fqdn')
        fqdn = fqdn[0]

    object_ = None
    domain = None
    if record_type == 'PTR':
        pass
    else:
        try:
            # Call prune tree later if error, else domain leak.
            label, domain = ensure_label_domain(fqdn)
        except ValidationError, e:
            form = FQDNFormKlass(orig_qd)
            form._errors = ErrorDict()
            form._errors['__all__'] = ErrorList(e.messages)
            return render(request, 'master_form/ajax_form.html', {
                'form': form,
                'record_type': record_type,
                'record_pk': record_pk,
                'obj': object_
            })
        qd['label'], qd['domain'] = label, str(domain.pk)

    if record_pk:
        # ACLs here. Move up so no new domain for unauthorized users.
        object_ = get_object_or_404(Klass, pk=record_pk)
        form = FormKlass(qd, instance=object_)
    else:
        form = FormKlass(qd)

    if form.is_valid():
        # Validate form.
        try:
            object_ = form.save()
        except ValidationError, e:
            prune_tree(domain)
            error_form = FQDNFormKlass(orig_qd)
            error_form._errors = ErrorDict()
            error_form._errors['__all__'] = ErrorList(e.messages)
            return render(request, 'master_form/ajax_form.html', {
                'form': error_form,
                'record_type': record_type,
                'record_pk': record_pk,
                'obj': object_
            })

        fqdn_form = FQDNFormKlass(instance=object_)
        if record_pk:
            message = 'Record Updated!'
        else:
            message = 'Record Created!'
        return render(request, 'master_form/ajax_form.html', {
            'form': fqdn_form,
            'record_type': record_type,
            'record_pk': object_.pk,
            'message': message,
            'obj': object_
        })

    else:
        # Revert if form not valid.
        prune_tree(domain)
        error_form = FQDNFormKlass(orig_qd)
        error_form._errors = form._errors
        return render(request, 'master_form/ajax_form.html', {
            'form': error_form,
            'record_type': record_type,
            'record_pk': record_pk,
            'obj': object_
        })
