from gettext import gettext as _
from jinja2 import Environment, PackageLoader
import json as json

from django.shortcuts import render
from django.http import HttpResponse

from search.compiler.django_compile import compile_to_django

from cyder.base.utils import tablefy
from cyder.cydns.api.v1.api import v1_dns_api
from cyder.cydns.utils import get_zones


env = Environment(loader=PackageLoader('search', 'templates'))


def search(request):
    """Search page."""
    search = request.GET.get('search', '')
    meta, tables = _search(request)

    return render(request, 'search/search.html', {
        'search': search,
        'meta': meta,
        'tables': tables,
        'zones': [z.name for z in get_zones()]
    })


def _search(request):
    search = request_to_search(request)
    errors = handle_shady_search(search)
    if errors:
        return errors

    objs, error_resp = compile_to_django(search)
    if not objs:
        return ([], [])
    (addrs, cnames, domains, intrs, mxs, nss, ptrs, soas, srvs, sshfps, sys,
     txts, misc) = objs

    meta = [
        (addrs.count() if addrs else 0, 'address', 'Address Records'),
        (cnames.count() if cnames else 0, 'cname', 'CNAMEs'),
        (domains.count() if domains else 0, 'domain', 'Domains'),
        (intrs.count() if intrs else 0, 'interface', 'Interfaces'),
        (mxs.count() if mxs else 0, 'mx', 'MXs'),
        (nss.count() if nss else 0, 'nameserver', 'Nameservers'),
        (ptrs.count() if ptrs else 0, 'ptr', 'PTRs'),
        (srvs.count() if srvs else 0, 'srv', 'SRVs'),
        (sys.count() if srvs else 0, 'sys', 'Systems'),
        (txts.count() if txts else 0, 'txt', 'TXTs'),
    ]

    tables = [
        (tablefy(addrs, views=True), 'address', 'Address Records'),
        (tablefy(cnames, views=True), 'cname', 'CNAMEs'),
        (tablefy(domains, views=True), 'domain', 'Domains'),
        (tablefy(intrs, views=True), 'interface', 'Interfaces'),
        (tablefy(mxs, views=True), 'mx', 'MXs'),
        (tablefy(nss, views=True), 'nameserver', 'Nameservers'),
        (tablefy(ptrs, views=True), 'ptr', 'PTRs'),
        (tablefy(srvs, views=True), 'srv', 'SRVs'),
        (tablefy(sys, views=True), 'sys', 'Systems'),
        (tablefy(txts, views=True), 'txt', 'TXTs'),
    ]

    return (meta, tables)


def resource_for_request(resource_name, filters, request):
    resource = v1_dns_api.canonical_resource_for(resource_name)
    objects = resource.get_object_list(request).filter(filters)
    search_fields = resource._meta.object_class.search_fields
    return [(search_fields, resource.model_to_data(model, request))
            for model in objects]


def request_to_search(request):
    search = request.GET.get("search", None)
    adv_search = request.GET.get("advanced_search", "")

    if adv_search:
        if search:
            search += " AND " + adv_search
        else:
            search = adv_search
    return search


def handle_shady_search(search):
    if not search:
        return HttpResponse("What do you want?!?")
    dos_terms = ["10", "com", "network:10/8", "network:10.0.0.0/8"]
    if search in dos_terms:
        return HttpResponse("Search term '{0}' is too general".format(search))
    return None


def search_ajax(request):
    template = env.get_template('search/search_results.html')

    def html_response(**kwargs):
        return template.render(**kwargs)
    return _search(request, html_response)


def search_dns_text(request):

    def render_rdtype(rdtype_set, **kwargs):
        response_str = ""
        for obj in rdtype_set:
            response_str += _("{0:<6}".format(obj.pk) +
                                obj.bind_render_record(**kwargs) + "\n")
        return response_str

    def text_response(**kwargs):
        response_str = ""
        for rdtype in ['soas', 'nss', 'srvs', 'cnames', 'sshfps', 'txts',
                       'addrs', 'intrs', 'ptrs']:
            response_str += render_rdtype(kwargs[rdtype])
        response_str += render_rdtype(kwargs['intrs'], reverse=True)
        return json.dumps({'text_response': response_str})

    return _search(request, text_response)


def get_zones_json(request):
    return HttpResponse(json.dumps([z.name for z in get_zones()]))
