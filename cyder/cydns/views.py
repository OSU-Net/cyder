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
from cyder.cydns.utils import ensure_label_domain, prune_tree, slim_form
from cyder.cydns.view.models import View


class CydnsListView(BaseListView):
    """ """
    template_name = 'cydns/cydns_list.html'


def cydns_list_create_record(request, record_type=None, record_pk=None):
    """
    Gets form for updating or creating a record type.
    """
    if request.method == 'GET':
        domains = Domain.objects.filter(is_reverse=False)

        # Get the record type's form.
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
            object_ = None
            form = FQDNFormKlass()

        return render(request, 'cydns/cydns_list_record.html', {
            'domains': json.dumps([domain.name for domain in domains]),
            'form': form,
            'record_type': record_type,
            'record_pk': record_pk,
            'obj': object_
        })

    qd = request.POST.copy()  # Make qd mutable.
    orig_qd = request.POST.copy()  # If errors, use qd to populate form.

    Klass, FormKlass, FQDNFormKlass = get_klasses(record_type)
    if 'fqdn' in qd:
        fqdn = qd.pop('fqdn')
        fqdn = fqdn[0]

    object_ = None
    domain = None
    if record_type is not 'PTR':
        try:
            # Call prune tree later if error, else domain leak.
            label, domain = ensure_label_domain(fqdn)
        except ValidationError, e:
            form = FQDNFormKlass(orig_qd)
            form._errors = ErrorDict()
            form._errors['__all__'] = ErrorList(e.messages)
            return render(request, 'cydns/cydns_list_record.html', {
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

    # Validate form.
    return_form = None
    if form.is_valid():
        try:
            object_ = form.save()
        except ValidationError, e:
            # Revert domain if not valid.
            prune_tree(domain)
            return_form = FQDNFormKlass(orig_qd)
            return_form._errors = ErrorDict()
            return_form._errors['__all__'] = ErrorList(e.messages)

        return_form = FQDNFormKlass(instance=object_)
    else:
        # Revert domain if not valid.
        prune_tree(domain)
        return_form = FQDNFormKlass(orig_qd)
        return_form._errors = form._errors

    return render(request, 'cydns/cydns_list_record.html', {
        'form': return_form,
        'record_type': record_type,
        'record_pk': record_pk,
        'obj': object_
    })


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
    elif record_type == 'ptr':
        Klass = PTR
        FormKlass = PTRForm
        FQDNFormKlass = PTRForm
    elif record_type == 'srv':
        Klass = SRV
        FormKlass = SRVForm
        FQDNFormKlass = FQDNSRVForm
    elif record_type == 'cname':
        Klass = CNAME
        FormKlass = CNAMEForm
        FQDNFormKlass = CNAMEFQDNForm
    elif record_type == 'txt':
        Klass = TXT
        FormKlass = TXTForm
        FQDNFormKlass = FQDNTXTForm
    elif record_type == 'mx':
        Klass = MX
        FormKlass = MXForm
        FQDNFormKlass = FQDNMXForm
    elif record_type == 'soa':
        Klass = SOA
        FormKlass = SOAForm
        FQDNFormKlass = SOAForm
    else:
        Klass, FormKlass, FQDNFormKlass = None, None, None

    return Klass, FormKlass, FQDNFormKlass


def cydns_record_search_ajax(request):
    """
    Returns a list of records matching the 'query' of type 'record_type'.
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
