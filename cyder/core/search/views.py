from django.shortcuts import render
from django.http import HttpResponse

from cyder.core.search.parser import parse
from cyder.core.search.search import compile_search

from cyder.base.utils import tablefy


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
        (addrs, cnames, domains, intrs, mxs,
         nss, ptrs, srvs, txts, misc) = compile_search(query)
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
          'meta': meta,
          'address_table': tablefy(addrs, views=True),
          'cname_table': tablefy(cnames, views=True),
          'domain_table': tablefy(domains, views=True),
          'intr_table': tablefy(intrs, views=True),
          'misc_table': tablefy(misc),
          'mx_table': tablefy(mxs, views=True),
          'ns_table': tablefy(nss, views=True),
          'ptr_table': tablefy(ptrs, views=True),
          'srv_table': tablefy(srvs, views=True),
          'txt_table': tablefy(txts, views=True),
        })

    return render(request, 'search/search.html', context_dict)
