from django.core.exceptions import ValidationError
from django.forms.util import ErrorDict, ErrorList
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from cyder.base.constants import ACTION_CREATE, get_klasses
from cyder.base.mixins import UsabilityFormMixin
from cyder.base.helpers import do_sort
from cyder.base.utils import (make_paginator, _filter, tablefy)
from cyder.base.views import (BaseCreateView, BaseDeleteView,
                              BaseDetailView, BaseListView, BaseUpdateView,
                              cy_delete, search_obj, table_update)
from cyder.core.cyuser.utils import perm

from cyder.cydns.utils import ensure_label_domain, prune_tree, slim_form

import json


def is_ajax_form(request):
    return True


def cydns_view(request, pk=None):
    """List, create, update view in one for a flatter heirarchy. """
    # Infer obj_type from URL, saves trouble of having to specify
    # kwargs everywhere in the dispatchers.
    obj_type = request.path.split('/')[2]

    Klass, FormKlass = get_klasses(obj_type)
    obj = get_object_or_404(Klass, pk=pk) if pk else None

    if request.method == 'POST':
        page_obj = None

        if obj_type == "ptr":
            qd, domain, errors = request.POST.copy(), None, None
        else:
            qd, domain, errors = _fqdn_to_domain(request.POST.copy())

        # Validate form.
        if errors:
            form = FormKlass(request.POST)
            form._errors = ErrorDict()
            form._errors['__all__'] = ErrorList(errors)
            if is_ajax_form(request):
                return HttpResponse(json.dumps({'errors': form.errors}))
        else:
            form = FormKlass(qd, instance=obj)
        try:
            if perm(request, ACTION_CREATE, obj=obj, obj_class=Klass):
                obj = form.save()
                # If domain, add to current ctnr.
                if is_ajax_form(request):
                    return HttpResponse(json.dumps({'success': True}))

                if (hasattr(obj, 'ctnr_set') and
                        not obj.ctnr_set.exists()):
                    obj.ctnr_set.add(request.session['ctnr'])
                    return redirect(obj.get_list_url())

        except (ValidationError, ValueError), e:
            form = _revert(domain, request.POST, form, FormKlass)
            if hasattr(e, 'messages'):
                e = e.messages

            if not form._errors:
                form._errors = ErrorDict()
                form._errors['__all__'] = ErrorList(e)

            if is_ajax_form(request):
                return HttpResponse(json.dumps({'errors': form.errors}))
    elif request.method == 'GET':
        form = FormKlass(instance=obj)

        object_list = _filter(request, Klass)
        page_obj = make_paginator(request, do_sort(request, object_list), 50)

    if issubclass(type(form), UsabilityFormMixin):
        form.make_usable(request)

    return render(request, 'cydns/cydns_view.html', {
        'form': form,
        'obj': obj,
        'obj_type': obj_type,
        'object_table': tablefy(page_obj, request=request),
        'page_obj': page_obj,
        'pretty_obj_type': Klass.pretty_type,
        'pk': pk,
    })


def _revert(domain, orig_qd, orig_form, FormKlass):
    """Revert domain if not valid."""
    prune_tree(domain)
    form = FormKlass(orig_qd)
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


def cydns_table_update(request, pk, object_type=None):
    return table_update(request, pk, object_type)


def cydns_search_obj(request):
    return search_obj(request)


def cydns_index(request):
    from cyder.models import AddressRecord, PTR, MX, SRV, SSHFP, TXT, CNAME
    ctnr = request.session['ctnr']
    domains = ctnr.domains.all()

    soa_list = []
    addressrecord_count = AddressRecord.objects.filter(ctnr=ctnr).count()
    ptr_count = PTR.objects.filter(ctnr=ctnr).count()
    mx_count = MX.objects.filter(ctnr=ctnr).count()
    srv_count = SRV.objects.filter(ctnr=ctnr).count()
    sshfp_count = SSHFP.objects.filter(ctnr=ctnr).count()
    txt_count = TXT.objects.filter(ctnr=ctnr).count()
    cname_count = CNAME.objects.filter(ctnr=ctnr).count()
    ns_count = 0
    for domain in domains:
        ns_count += domain.nameserver_set.count()

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
