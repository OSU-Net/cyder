import json

from django.http import HttpResponse

from cyder.base.views import cy_detail
from cyder.cydns.address_record.models import AddressRecord


def address_record_detail(request, pk):
    return cy_detail(
        request, AddressRecord, 'cydns/cydns_detail.html', {}, pk=pk)
