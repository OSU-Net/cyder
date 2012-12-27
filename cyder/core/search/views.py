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
        meta = [
            (addrs.count() if addrs else 0, 'address', 'Address Records'),
            (cnames.count() if cnames else 0, 'cname', 'CNAMEs'),
            (domains.count() if domains else 0, 'domain', 'Domains'),
            (intrs.count() if intrs else 0, 'interface', 'Interfaces'),
            (misc.count() if misc else 0, 'misc', 'Misc. Results'),
            (mxs.count() if mxs else 0, 'mx', 'MXs'),
            (nss.count() if nss else 0, 'nameserver', 'Nameservers'),
            (ptrs.count() if ptrs else 0, 'ptr', 'PTRs'),
            (srvs.count() if srvs else 0, 'srv', 'SRVs'),
            (txts.count() if txts else 0, 'txt', 'TXTs'),
        ]

        context_dict.update(**{
            'meta': meta,
            'tables': [
                (tablefy(addrs, views=True), 'address', 'Address Records'),
                (tablefy(cnames, views=True), 'cname', 'CNAMEs'),
                (tablefy(domains, views=True), 'domain', 'Domains'),
                (tablefy(intrs, views=True), 'interface', 'Interfaces'),
                (tablefy(misc), 'misc', 'Misc. Results'),
                (tablefy(mxs, views=True), 'mx', 'MXs'),
                (tablefy(nss, views=True), 'nameserver', 'Nameservers'),
                (tablefy(ptrs, views=True), 'ptr', 'PTRs'),
                (tablefy(srvs, views=True), 'srv', 'SRVs'),
                (tablefy(txts, views=True), 'txt', 'TXTs'),
            ]
        })

    return render(request, 'search/search.html', context_dict)
