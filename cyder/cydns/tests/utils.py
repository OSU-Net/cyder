from gettext import gettext as gt
import random
import simplejson as json
import string
import time

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.test import RequestFactory

from cyder.cydns.domain.models import Domain
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.soa.models import SOA
from cyder.cydns.view.models import View
from cyder.cydns.utils import ensure_domain, prune_tree
from cyder.cydhcp.vrf.models import Vrf


def get_post_data(random_str, suffix):
    """Return a valid set of data"""
    return {
        'root_domain': '{0}{1}'.format(random_str, suffix),
        'soa_primary': 'ns1.mozilla.com',
        'soa_contact': 'noc.mozilla.com',
        'nameserver_1': 'ns1.mozilla.com',
        'ttl_1': '1234'
    }


def create_fake_zone(random_str, suffix=".mozilla.com"):
    factory = RequestFactory()
    post_data = get_post_data(random_str, suffix=suffix)
    request = factory.post("/dont/matter", post_data)
    response = create_zone_ajax(request)
    if response.status_code == 500:
        raise ValidationError(json.loads(response.content)['error'])
    return Domain.objects.get(name=post_data['root_domain'])


def create_zone_ajax(request):
    """
    This view tries to create a new zone and returns an JSON with either
    'success' = True or 'success' = False and some errors. By default all
    records are created and added to the public view.

    Throughout this function note that objects that are created are recorded,
    and if an error is caught, the previously created objects are deleted. This
    backing-out *may* be better handling by a transaction. Django has this sort
    of thing (middleware and decorators), but I'm in a time crunch so this
    manual deletetion will have to do.
    """

    qd = request.POST.copy()
    # See if the domain exists.
    # Fail if it already exists or if it's under a delegated domain.
    root_domain = qd.get('root_domain', None)
    response_error = lambda error: HttpResponse(
        json.dumps({'success': False, 'error': error}), status=500)

    if not root_domain:
        error = "Please specify a root_domain"
        return response_error(error)

    if Domain.objects.filter(name=root_domain).exists():
        error = gt("<b>{0}</b> is already a domain. To make it a new zone, "
                   "assign it a newly created SOA.".format(root_domain))
        return HttpResponse(json.dumps({'success': False, 'error': error}),
                            status=400)

    primary = qd.get('soa_primary', None)
    if not primary:
        error = "Please specify a primary nameserver for the SOA record."
        return response_error(error)
    contact = qd.get('soa_contact', None)
    if not contact:
        error = "Please specify a contact address for the SOA record."
        return response_error(error)
    contact.replace('@', '.')

    # Find all the NS entries
    nss = []
    for k, v in request.POST.iteritems():
        if k.startswith('nameserver_'):
            ttl = qd.get('ttl_{0}'.format(k[-1:]), 3600)
            server = v
            nss.append(Nameserver(server=server, ttl=ttl))

    if not nss:
        # They must create at least one nameserver
        error = gt("You must choose an authoritative nameserver to serve this "
                   "zone")
        return response_error(error)

    # We want all domains created up to this point to inherit their
    # master_domain's soa. We will override the return domain's SOA.
    # Everything under this domain can be purgeable becase we will set this
    # domain to non-purgeable. This will also allow us to call prune tree.
    domain = ensure_domain(
        root_domain, purgeable=True, inherit_soa=False, force=True)

    private_view, _ = View.objects.get_or_create(name='private')
    public_view, _ = View.objects.get_or_create(name='public')
    saved_nss = []  # If these are errors, back out
    for i, ns in enumerate(nss):
        ns.domain = domain
        try:
            ns.save()
            ns.views.add(private_view)
            if not domain.name.endswith('10.in-addr.arpa'):
                ns.views.add(public_view)
            saved_nss.append(ns)
        except ValidationError, error:
            suffixes = ["th", "st", "nd", "rd", ] + ["th"] * 16
            suffixed_i = str(i + 1) + suffixes[i + 1 % 100]
            error_field, error_val = error.message_dict.items()[0]
            error = gt("When trying to create the {0} nameserver entry, the "
                       "nameserver field '{1}' returned the error "
                       "'{2}'".format(suffixed_i, error_field, error_val[0]))

            for s_ns in saved_nss:
                s_ns.delete()
            _clean_domain_tree(domain)
            return response_error(error)

    soa = SOA(primary=primary, contact=contact, serial=int(time.time()),
              description="SOA for {0}".format(root_domain),
              root_domain=domain)

    try:
        soa.save()
    except ValidationError, e:
        error = e.messages[0]
        _clean_domain_tree(domain)
        for s_ns in saved_nss:
            s_ns.delete()
        return response_error(error)
    domain.purgeable = False
    domain.save()

    try:
        domain.soa = soa
        domain.save()
    except ValidationError, error:
        for s_ns in saved_nss:
            s_ns.delete()
        _clean_domain_tree(domain)
        soa.delete()
        return response_error(error)

    return HttpResponse(json.dumps(
        {
            'success': True,
            'success_url': '/core/?search=zone=:{0}'.format(domain.name)
        }))


def _clean_domain_tree(domain):
    if not domain.master_domain:
        # They tried to create a TLD, prune_tree will not delete it.
        domain.delete()
    else:
        domain.purgeable = True
        prune_tree(domain)  # prune_tree will delete this domain


def random_label():
    """
    Utility function to generate a random *valid* label.
    """
    label = ''
    for i in range(random.randint(5, 30)):
        label += string.letters[random.randint(0, len(string.letters) - 1)]
    return label


def random_byte():
    """
    Utility function to generate a random byte for random IPs
    """
    return random.randint(1, 255)


def create_basic_dns_data(dhcp=False):
    for name in ('arpa', 'in-addr.arpa', 'ip6.arpa'):
        d = Domain(name=name)
        d.save()

    if dhcp:
        v = Vrf(name='test_vrf')
        v.save()


def create_zone(name):
    domain = Domain.objects.create(name=name)
    return make_root(domain)

def make_root(domain):
    Nameserver.objects.create(domain=domain, server='ns1.unused')
    SOA.objects.create(
        primary='ns1.unused', contact='webmaster.unused', root_domain=domain)
    return Domain.objects.get(pk=domain.pk)  # Reload it.
