from django.core.exceptions import ValidationError
from django.forms.util import ErrorDict, ErrorList
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from cyder.base.constants import ACTION_CREATE, get_klasses
from cyder.base.mixins import UsabilityFormMixin
from cyder.base.helpers import do_sort
from cyder.base.utils import (make_paginator, _filter, tablefy)
from cyder.base.views import search_obj, table_update
from cyder.core.cyuser.utils import perm

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

        form = FormKlass(request.POST, instance=obj)
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


def cydns_table_update(request, pk, object_type=None):
    return table_update(request, pk, object_type)


def cydns_search_obj(request):
    return search_obj(request)


def cydns_index(request):
    from cyder.models import (AddressRecord, CNAME, Domain, Nameserver, PTR,
                              MX, SOA, SRV, SSHFP, TXT)
    ctnr = request.session['ctnr']
    counts = []
    Klasses = [(AddressRecord, 'Address Records'), (PTR, 'PTRs'), (MX, 'MXs'),
        (SRV,'SRVs'), (SSHFP, 'SSHFPs'), (TXT, 'TXTs'), (CNAME, 'CNAMES')]

    if ctnr.name != 'global':
        domains = ctnr.domains.all()
        soa_list = []
        for Klass in Klasses:
            counts.append((Klass[1], Klass[0].objects.filter(ctnr=ctnr).count()))

        ns_count = 0
        for domain in domains:
            ns_count += domain.nameserver_set.count()

            if domain.soa not in soa_list:
                soa_list.append(domain.soa)

        counts.append(('SOAs', len(soa_list)))
        counts.append(('Nameservers', ns_count))

    else:
        domains = Domain.objects.all()
        Klasses.append((SOA, 'SOAs'))
        Klasses.append((Nameserver, 'Nameservers'))
        for Klass in Klasses:
            counts.append((Klass[1], Klass[0].objects.all().count()))


    counts.append(('Domains', domains.filter(is_reverse=False).count()))
    counts.append(('Reverse Domains',
               domains.filter(is_reverse=True).count()))

    return render(request, 'cydns/cydns_index.html', {'counts': counts})
