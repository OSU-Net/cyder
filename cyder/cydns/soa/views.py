from django.core.exceptions import ValidationError
from django.forms.util import ErrorList, ErrorDict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render

from cyder.cydns.soa.forms import SOAForm
from cyder.cydns.soa.models import SOA, SOAAV

import json as json


def soa_detail(request, pk):
    from cyder.base.views import cy_detail
    soa = SOA.objects.get(id=pk)
    return cy_detail(request, SOA, 'soa/soa_detail.html', {
        'domains': (soa.domain_set.filter(is_reverse=False)
                    .order_by('master_domain').select_related()),
        'rdomains': (soa.domain_set.filter(is_reverse=True)
                     .order_by('master_domain').select_related()),
        'attributes': SOAAV.objects.filter(soa=soa.id)
    }, obj=soa)


def delete_soa_attr(request, attr_pk):
    """
    A view destined to be called by ajax to remove an attr.
    """
    attr = get_object_or_404(SOAAV, pk=attr_pk)
    attr.delete()
    return HttpResponse("Attribute Removed.")


def update_soa(request, soa_pk):
    soa = get_object_or_404(SOA, pk=soa_pk)
    if request.method == 'POST':
        form = SOAForm(request.POST, instance=soa)
        try:
            if not form.is_valid():
                return render(request, 'soa/soa_edit.html', {
                    'soa': soa,
                    'form': form,
                })
            else:
                soa = form.save()
                return redirect(soa.get_update_url())
        except ValidationError, e:
            if form._errors is None:
                form._errors = ErrorDict()
            form._errors['__all__'] = ErrorList(e.messages)
            return render(request, 'soa/soa_edit.html', {
                'soa': soa,
                'form': form,
            })

    else:
        form = SOAForm(instance=soa)
        return render(request, 'soa/soa_edit.html', {
            'soa': soa,
            'form': form,
        })
