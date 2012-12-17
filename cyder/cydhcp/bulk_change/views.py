from django.shortcuts import render
from django.http import HttpResponse

from cyder.core.search.parser import parse
from cyder.core.search.search import compile_search

from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('cydhcp.bulk_change', 'templates'))


def bulk_change_ajax(request):
    search = request.GET.get("search", None)
    if not search:
        return HttpResponse("What do you want?!?")
    query = parse(search)
    print "----------------------"
    print query
    print "----------------------"

    x = compile_search(query)
    addrs, cnames, domains, intrs, mxs, nss, ptrs, srvs, txts, misc = x
    template = env.get_template('bulk_change/bulk_change_form_content.html')
    return HttpResponse(template.render(
        **{
        "search": search,
        "addrs": addrs,
        "cnames": cnames,
        "intrs": intrs,
        "mxs": mxs,
        "nss": nss,
        "ptrs": ptrs,
        "srvs": srvs,
        "txts": txts
        }
    ))


def bulk_change(request):
    """Search page"""
    search = request.GET.get('search', '')
    return render(request, "bulk_change/bulk_change.html", {
        "search": search
    })
