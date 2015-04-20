from gettext import gettext as _
from jinja2 import Environment, PackageLoader
import json as json

from django.http import HttpResponse

from search.compiler.django_compile import compile_to_django

from cyder.base.utils import tablefy
from cyder.base.views import cy_render
from cyder.base.helpers import strip_if_mac_with_colons
from cyder.cydns.utils import get_zones


env = Environment(loader=PackageLoader('search', 'templates'))


def search(request):
    """Search page."""
    search = request.GET.get('search', '')
    if search:
        meta, tables = _search(request)
    else:
        meta, tables = [], []

    return cy_render(request, 'search/search.html', {
        'search': search,
        'meta': meta,
        'tables': tables,
        'zones': [z.name for z in get_zones()]
    })


def _search(request):
    search = request_to_search(request).split(' ')
    search = ' '.join([strip_if_mac_with_colons(word) for word in search])

    objs, error_resp = compile_to_django(search)
    if not objs:
        return ([], [])
    (addrs, cnames, domains, static, dynamic, mxs, nss, ptrs, soas, srvs,
     sshfps, sys, txts, misc) = (
         objs['A'],
         objs['CNAME'],
         objs['DOMAIN'],
         objs['STATIC'],
         objs['DYNAMIC'],
         objs['MX'],
         objs['NS'],
         objs['PTR'],
         objs['SOA'],
         objs['SRV'],
         objs['SSHFP'],
         objs['SYSTEM'],
         objs['TXT'],
         [])

    meta = [
        (soas.count() if soas else 0, 'soa', 'SOA Records'),
        (addrs.count() if addrs else 0, 'address', 'Address Records'),
        (cnames.count() if cnames else 0, 'cname', 'CNAMEs'),
        (domains.count() if domains else 0, 'domain', 'Domains'),
        (static.count() if static else 0, 'static', 'Static Interfaces'),
        (dynamic.count() if dynamic else 0, 'dynamic', 'Dynamic Interfaces'),
        (mxs.count() if mxs else 0, 'mx', 'MXs'),
        (nss.count() if nss else 0, 'nameserver', 'Nameservers'),
        (ptrs.count() if ptrs else 0, 'ptr', 'PTRs'),
        (srvs.count() if srvs else 0, 'srv', 'SRVs'),
        (sys.count() if srvs else 0, 'sys', 'Systems'),
        (txts.count() if txts else 0, 'txt', 'TXTs'),
    ]

    tables = [
        (tablefy(soas, request=request), 'soa', 'SOA Records'),
        (tablefy(addrs, request=request), 'address', 'Address Records'),
        (tablefy(cnames, request=request), 'cname', 'CNAMEs'),
        (tablefy(domains, request=request), 'domain', 'Domains'),
        (tablefy(static, request=request), 'static', 'Static Interfaces'),
        (tablefy(dynamic, request=request), 'dynamic', 'Dynamic Interfaces'),
        (tablefy(mxs, request=request), 'mx', 'MXs'),
        (tablefy(nss, request=request), 'nameserver', 'Nameservers'),
        (tablefy(ptrs, request=request), 'ptr', 'PTRs'),
        (tablefy(srvs, request=request), 'srv', 'SRVs'),
        (tablefy(sys, request=request), 'sys', 'Systems'),
        (tablefy(txts, request=request), 'txt', 'TXTs'),
    ]

    return (meta, tables)


def request_to_search(request):
    search = request.GET.get("search", None)
    adv_search = request.GET.get("advanced_search", "")

    if adv_search:
        if search:
            search += " AND " + adv_search
        else:
            search = adv_search
    return search


def get_zones_json(request):
    return HttpResponse(json.dumps([z.name for z in get_zones()]))
