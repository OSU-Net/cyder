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
        'attributes': SOAAV.objects.filter(entity=soa.id)
    }, obj=soa)
