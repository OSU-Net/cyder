from django.shortcuts import render
from django.http import HttpResponse

from cyder.core.search.parser import parse
from cyder.core.search.search import compile_search


def search(request):
    search = request.GET.get('search', None)
    context_dict = {'search': search}

    if search:
        dos_terms = ['10', 'com', 'mozilla.com', 'mozilla', 'network:10/8',
                     'network:10.0.0.0/8']
        if search in dos_terms:
            return HttpResponse(
                'Denial of Service attack prevented. The search '
                'term \'{0}\' is too general'.format(search))
        query = parse(search)
        print '----------------------'
        print query
        print '----------------------'

        x = compile_search(query)
        addrs, cnames, domains, intrs, mxs, nss, ptrs, srvs, txts, misc = x
        meta = {
            'counts': {
            'addr': addrs.count() if addrs else 0,
            'cname': cnames.count() if cnames else 0,
            'domain': domains.count() if domains else 0,
            'intr': intrs.count() if intrs else 0,
            'mx': mxs.count() if mxs else 0,
            'ns': nss.count() if nss else 0,
            'ptr': ptrs.count() if ptrs else 0,
            'txt': txts.count() if txts else 0,
            }
        }

        context_dict.update(**{
          'misc': misc,
          'addrs': addrs,
          'cnames': cnames,
          'domains': domains,
          'intrs': intrs,
          'mxs': mxs,
          'nss': nss,
          'ptrs': ptrs,
          'srvs': srvs,
          'txts': txts,
          'meta': meta,
        })

    return render(request, 'search/search.html', context_dict)
