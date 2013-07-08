from gettext import gettext as _
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from cyder.cydns.soa.models import SOA
from cyder.cydns.cybind.zone_builder import build_zone_data
from cyder.cydns.view.models import View

import json as json


def build_debug_soa(request, soa_pk):
    soa = get_object_or_404(SOA, pk=soa_pk)
    #DEBUG_BUILD_STRING = build_zone(soa, root_domain)
    # Figure out what sort of domains are in this zone.
    public_view = View.objects.get(id=1)
    if View.objects.get(id=2):
        private_view = View.objects.get(id=2)
    try:
        public_data = build_zone_data(public_view, soa.root_domain, soa)
        if private_view:
            private_data = build_zone_data(private_view, soa.root_domain, soa)

        output = _("""
                   ;======= Private Data =======
                   {0}

                   ;======= Private Data =======
                   {1}
                   """.format(private_data, public_data))
    except Exception:
        return HttpResponse(json.dumps(
                            {"error": "Could not build bind file"}))
    return render(request, 'cybind/sample_build.html',
                  {'data': output, 'soa': soa})
