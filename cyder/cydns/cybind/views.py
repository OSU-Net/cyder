from gettext import gettext as _
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import ObjectDoesNotExist

from cyder.cydns.soa.models import SOA
from cyder.cydns.cybind.zone_builder import build_zone_data
from cyder.cydns.view.models import View

import json as json


zone_template = """\
;======= Private Data =======
{0}

;======= Public Data =======
{1}
"""


def build_debug_soa(request, soa_pk):
    soa = get_object_or_404(SOA, pk=soa_pk)
    #DEBUG_BUILD_STRING = build_zone(soa, root_domain)
    # Figure out what sort of domains are in this zone.

    try:
        public_view = View.objects.get(name='public')
        public_data = build_zone_data(public_view, soa.root_domain, soa)

        try:
            private_view = View.objects.get(name='private')
            private_data = build_zone_data(private_view, soa.root_domain, soa)
        except ObjectDoesNotExist:
            private_data = ''

        output = _(zone_template.format(private_data, public_data))

        return cy_render(request, 'cybind/sample_build.html',
                      {'data': output, 'soa': soa})

    except Exception, e:
        return HttpResponse(
            json.dumps({"error": "Could not build bind file: %s" % e}))
