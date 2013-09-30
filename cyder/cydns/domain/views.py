import json

from django.http import HttpResponse, Http404

from cyder.base.views import cy_detail
from cyder.base.utils import make_megafilter
from cyder.cydns.domain.models import Domain


def domain_detail(request, pk):
    return cy_detail(request, Domain, 'cydns/cydns_detail.html', {
        'Interfaces': 'staticinterface_set',
        'Address Records': 'addressrecord_set',
        'CNAMEs': 'cname_set',
        'MXs': 'mx_set',
        'Nameservers': 'nameserver_set',
        'PTRs': 'reverse_ptr_set',
        'SRVs': 'srv_set',
        'SSHFPs': 'sshfp_set',
        'TXTs': 'txt_set',
    }, pk=pk)


def domain_sort(domains):
    """
    This is soooooo slow.
    """
    roots = domains.filter(master_domain=None)
    ordered = []
    for root in roots:
        ordered += build_tree(root, domains)
    return ordered


def build_tree(root, domains):
    if len(domains) == 0:
        return root
    ordered = [root]
    children = domains.filter(master_domain=root)
    for child in children:
        ordered += build_tree(child, domains)
    return ordered


def get_all_domains(request):
    domains = [domain.name for domain in Domain.objects.all()]
    return HttpResponse(json.dumps(domains))


def search(request):
    """Returns a list of domains matching 'term'."""
    term = request.GET.get('term', '')
    if not term:
        raise Http404

    domains = Domain.objects.filter(make_megafilter(Domain, term))[:15]
    domains = [{'label': str(domain), 'pk': domain.id} for domain in domains]
    return HttpResponse(json.dumps(domains))
