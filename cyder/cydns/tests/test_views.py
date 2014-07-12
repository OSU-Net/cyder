from django.test.client import Client

from nose.tools import eq_

import cyder.base.tests
from cyder.base.tests.test_views_template import build, random_label
from cyder.core.ctnr.models import Ctnr
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.utils import ip_to_domain_name
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.srv.models import SRV
from cyder.cydns.txt.models import TXT
from cyder.cydns.sshfp.models import SSHFP
from cyder.cydns.view.models import View
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range

from cyder.cydns.tests.utils import create_fake_zone


def create_network_range(network_str, start_str, end_str, range_type,
                         ip_type, domain, ctnr):
    n = Network(ip_type=ip_type, network_str=network_str)
    n.full_clean()
    n.save()

    r = Range(network=n, range_type=range_type, start_str=start_str,
              end_str=end_str, domain=domain, ip_type=ip_type)
    r.full_clean()
    r.save()

    ctnr.ranges.add(r)


def do_preUp(self):
    self.client = Client()
    self.client.login(username='test_superuser', password='password')

    self.public_view = View.objects.get_or_create(name='public')[0]
    self.private_view = View.objects.get_or_create(name='private')[0]

    self.ctnr = Ctnr.objects.get(name='test_ctnr')
    self.domain = create_fake_zone(random_label(), suffix='.oregonstate.edu')
    self.ctnr.domains.add(self.domain)

    # Create forward zone.
    self.soa = self.domain.soa
    self.subdomain = Domain.objects.create(
        name=random_label() + '.' + self.domain.name, soa=self.soa)
    self.ctnr.domains.add(self.subdomain)

    self.reverse_domain = create_fake_zone('196.in-addr.arpa', suffix='')
    self.ctnr.domains.add(self.reverse_domain)
    self.soa2 = self.reverse_domain.soa


def do_postUp(self, test_class, test_data, use_ctnr=True,
              use_domain=True, use_rdomain=False):
    if use_ctnr:
        test_data['ctnr'] = self.ctnr

    self.test_class = test_class
    # Create test object.
    test_data = dict(test_data.items())
    if use_domain:
        test_data['domain'] = self.domain
    if use_rdomain:
        test_data['reverse_domain'] = self.reverse_domain
    self.test_obj, create = test_class.objects.get_or_create(**test_data)


def do_setUp(self, *args, **kwargs):
    do_preUp(self)
    do_postUp(self, *args, **kwargs)


class NoNSTests(object):

    def get_domain_and_post_data(self):
        # This is different for classes that have ips instead of fqdns
        domain_name = "{0}.{1}.{2}.{3}.com".format(
            random_label(), random_label(), random_label(), random_label()
        )
        root_domain = create_fake_zone(domain_name, suffix="")
        post_data = self.post_data()
        # Get the '_' in SRV records
        post_data['fqdn'] = post_data['fqdn'][0] + "asdf.asdf." + domain_name
        self.ctnr.domains.add(root_domain)
        return root_domain, post_data

    def test_no_ns_in_view(self):
        root_domain, post_data = self.get_domain_and_post_data()
        ns = root_domain.nameserver_set.all()[0]
        ns.views.remove(self.public_view)
        ns.views.remove(self.private_view)
        # We now have a zone with nameservers that aren't in any views. No
        # record should be allowed to be in the view

        start_obj_count = self.test_class.objects.count()
        post_data['views'] = [self.public_view.pk]

        # Create the object then get the object
        resp = self.client.post(self.test_class.get_create_url(),
                                post_data, follow=True)
        self.assertEqual(resp.status_code, 200)
        new_obj_count = self.test_class.objects.count()

        # Nothing should have been created
        self.assertEqual(start_obj_count, new_obj_count)

        ns.views.add(self.public_view)

        # Okay, we should be able to add to the public view now
        start_obj_count = self.test_class.objects.count()
        resp = self.client.post(self.test_class.get_create_url(),
                                post_data, follow=True)
        new_obj_count = self.test_class.objects.count()
        self.assertEqual(start_obj_count + 1, new_obj_count)


class AddressRecordViewTests(cyder.base.tests.TestCase, NoNSTests):
    fixtures = ['test_users/test_users.json']
    name = 'address_record'

    def setUp(self):
        test_data = {
            'label': random_label(),
            'ip_type': '4',
            'ip_str': '196.168.1.1',
        }
        do_setUp(self, AddressRecord, test_data)

    def post_data(self):
        return {
            'fqdn': self.domain.name,
            'ip_type': '4',
            'ip_str': '196.168.1.2',
            'ttl': '400',
            'description': 'yo',
            'ctnr': self.ctnr.pk,
        }


class CNAMEViewTests(cyder.base.tests.TestCase, NoNSTests):
    fixtures = ['test_users/test_users.json']
    name = 'cname'

    def setUp(self):
        test_data = {
            'label': random_label(),
            'target': random_label()
        }
        do_setUp(self, CNAME, test_data)

    def post_data(self):
        return {
            'fqdn': self.subdomain.name,
            'label': random_label(),
            'target': random_label(),
            'ctnr': self.ctnr.pk,
        }


class NSViewTests(cyder.base.tests.TestCase):
    fixtures = ['test_users/test_users.json']
    name = 'nameserver'

    def setUp(self):
        self.domain = create_fake_zone("foobarbaz.com")
        test_data = {
            'server': self.domain.name
        }
        do_setUp(self, Nameserver, test_data)

    def post_data(self):
        return {
            'fqdn': self.domain.name,
            'server': self.domain.name
        }

    def test_no_ns_in_view(self):
        root_domain = create_fake_zone("asdfdjhjd")
        self.ctnr.domains.add(root_domain)
        ns = root_domain.nameserver_set.all()[0]

        cn = CNAME(label='asdf', domain=root_domain,
                   target='test.com', ctnr=self.ctnr)
        cn.full_clean()
        cn.save()
        cn.views.add(self.public_view)

        self.assertTrue(ns.domain.soa == cn.domain.soa)

        # We now should have a nameserver and a cname in the public view. The
        # nameserver should not be allowed to disable it's public view

        # Try to remove the public view
        self.assertTrue(self.public_view in ns.views.all())
        self.assertTrue(self.private_view in ns.views.all())
        post_data = self.post_data()
        post_data['fqdn'] = ns.domain.name
        post_data['views'] = [self.private_view.pk]
        resp = self.client.post(
            ns.get_update_url(), post_data, follow=True
        )
        self.assertEqual(resp.status_code, 200)
        # Make sure it's still there
        ns = Nameserver.objects.get(pk=ns.pk)  # fetch
        # Make sure the view is still there
        # The clean method should prevent it from being deleted
        self.assertTrue(self.public_view in ns.views.all())

        # Try to remove the private view
        # This should be allowed
        self.assertTrue(self.public_view in ns.views.all())
        post_data = self.post_data()
        post_data['views'] = [self.public_view.pk]
        resp = self.client.post(
            ns.get_update_url(), post_data, follow=True
        )
        self.assertEqual(resp.status_code, 200)
        # Make sure it's still there
        ns = Nameserver.objects.get(pk=ns.pk)  # fetch
        # Make sure the view is still there
        # The clean method should prevent it from being deleted
        self.assertTrue(self.private_view not in ns.views.all())


class MXViewTests(cyder.base.tests.TestCase, NoNSTests):
    fixtures = ['test_users/test_users.json']
    name = 'mx'

    def setUp(self):
        test_data = {
            'label': random_label(),
            'server': random_label(),
            'priority': 123,
            'ttl': 213
        }
        do_setUp(self, MX, test_data)

    def post_data(self):
        return {
            'fqdn': self.domain.name,
            'label': random_label(),
            'server': random_label(),
            'priority': 123,
            'ttl': 213,
            'ctnr': self.ctnr.pk,
        }


class PTRViewTests(cyder.base.tests.TestCase, NoNSTests):
    fixtures = ['test_users/test_users.json']
    name = 'ptr'

    def get_domain_and_post_data(self):
        # This is different for classes that have ips instead of fqdns
        domain_name = "9.ip6.arpa"
        root_domain = create_fake_zone(domain_name, suffix="")
        post_data = self.post_data()
        post_data['ip_str'] = '9000::df12'
        post_data['ip_type'] = '6'
        create_network_range(network_str='9000::/32',
                             start_str='9000::d000', end_str='9000::dfff',
                             range_type='st', ip_type='6', domain=self.domain,
                             ctnr=self.ctnr)

        return root_domain, post_data

    def setUp(self):
        test_data = {
            'fqdn': random_label() + '.' + random_label(),
            'ip_type': '4',
            'ip_str': '196.168.1.2',
        }
        Domain.objects.get_or_create(name='arpa')
        Domain.objects.get_or_create(name='in-addr.arpa')
        Domain.objects.get_or_create(name='196.in-addr.arpa')
        Domain.objects.get_or_create(name='168.196.in-addr.arpa')
        Domain.objects.get_or_create(name='1.168.196.in-addr.arpa')

        do_preUp(self)
        create_network_range(network_str='196.168.0.0/16',
                             start_str='196.168.1.0', end_str='196.168.1.253',
                             range_type='st', ip_type='4', domain=self.domain,
                             ctnr=self.ctnr)

        Domain.objects.create(name=ip_to_domain_name(test_data['ip_str']))
        do_postUp(self, PTR, test_data, use_domain=False, use_rdomain=True)

    def post_data(self):
        return {
            'fqdn': random_label() + '.' + random_label(),
            'ip_type': '4',
            'ip_str': '196.168.1.3',
            'description': 'yo',
            'ctnr': self.ctnr.pk,
        }

    def test_update_reverse_domain(self):
        eq_(self.test_obj.reverse_domain.name, '2.1.168.196.in-addr.arpa')
        post_data = self.post_data()

        self.client.post(self.test_obj.get_update_url(), post_data,
                         follow=True)
        updated_obj = PTR.objects.get(id=self.test_obj.id)
        eq_(updated_obj.ip_str, '196.168.1.3')


class SRVViewTests(cyder.base.tests.TestCase, NoNSTests):
    fixtures = ['test_users/test_users.json']
    name = 'srv'

    def setUp(self):
        test_data = {
            'label': '_' + random_label(),
            'target': 'foo.com',
            'priority': 2,
            'weight': 2222,
            'port': 222
        }
        do_setUp(self, SRV, test_data)

    def post_data(self):
        return {
            'fqdn': '_' + random_label() + '.' + self.domain.name,
            'target': 'foo.bar',
            'priority': 2,
            'weight': 2222,
            'port': 222,
            'ctnr': self.ctnr.pk,
        }


class TXTViewTests(cyder.base.tests.TestCase, NoNSTests):
    fixtures = ['test_users/test_users.json']
    name = 'txt'

    def setUp(self):
        test_data = {
            'label': random_label(),
            'txt_data': random_label()
        }
        do_setUp(self, TXT, test_data)

    def post_data(self):
        return {
            'fqdn': self.domain.name,
            'label': random_label(),
            'txt_data': random_label(),
            'ctnr': self.ctnr.pk,
        }


class SSHFPViewTests(cyder.base.tests.TestCase, NoNSTests):
    fixtures = ['test_users/test_users.json']
    name = 'sshfp'

    def setUp(self):
        test_data = {
            'label': random_label(),
            'algorithm_number': 1,
            'fingerprint_type': 1,
            'key': '9d97e98f8af710c7e7fe703abc8f639e0ee50222'
        }
        do_setUp(self, SSHFP, test_data)

    def post_data(self):
        return {
            'fqdn': self.domain.name,
            'label': random_label(),
            'algorithm_number': 1,
            'fingerprint_type': 1,
            'key': '9d97e98f8af710c7e7fe703abc8f639e0ee50111',
            'ctnr': self.ctnr.pk,
        }


# Build the tests.
build([AddressRecordViewTests, CNAMEViewTests, MXViewTests, NSViewTests,
       PTRViewTests, SRVViewTests, TXTViewTests, SSHFPViewTests])
