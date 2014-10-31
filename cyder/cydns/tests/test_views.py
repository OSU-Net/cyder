from django.test.client import Client

from nose.tools import eq_

from cyder.base.tests import TestCase
from cyder.base.tests.test_views_base import GenericViewTests, format_response
from cyder.core.ctnr.models import Ctnr
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.ip.utils import ip_to_reverse_name
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.srv.models import SRV
from cyder.cydns.tests.utils import create_zone
from cyder.cydns.txt.models import TXT
from cyder.cydns.sshfp.models import SSHFP
from cyder.cydns.view.models import View
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range

from cyder.cydns.tests.utils import create_zone


def create_network_range(network_str, start_str, end_str, range_type,
                         ip_type, domain, ctnr):
    n = Network.objects.create(ip_type=ip_type, network_str=network_str)

    r = Range.objects.create(
        network=n, range_type=range_type, start_str=start_str, end_str=end_str,
        domain=domain, ip_type=ip_type)
    ctnr.ranges.add(r)


def do_preUp(self):
    self.client = Client()
    self.client.login(username='test_superuser', password='password')

    self.public_view = View.objects.create(name='public')
    self.private_view = View.objects.create(name='private')

    self.ctnr = Ctnr.objects.get(name='test_ctnr')
    self.domain = create_zone('com')
    self.ctnr.domains.add(self.domain)

    # Create forward zone.
    self.subdomain = Domain.objects.create(name='example.com')
    self.ctnr.domains.add(self.subdomain)

    Domain.objects.create(name='arpa')
    Domain.objects.create(name='in-addr.arpa')
    self.reverse_domain = create_zone('196.in-addr.arpa')
    self.ctnr.domains.add(self.reverse_domain)


def do_postUp(self, test_data, use_ctnr=True,
              use_domain=True, use_rdomain=False):
    if use_ctnr:
        test_data['ctnr'] = self.ctnr

    # Create test object.
    test_data = dict(test_data.items())
    if use_domain:
        test_data['domain'] = self.domain
    if use_rdomain:
        test_data['reverse_domain'] = self.reverse_domain
    self.test_obj = self.model.objects.create(**test_data)


def do_setUp(self, *args, **kwargs):
    do_preUp(self)
    do_postUp(self, *args, **kwargs)


class NoNSTests(GenericViewTests):
    def get_domain_and_post_data(self):
        # This is different for classes that have IPs instead of FQDNs
        root_domain = create_zone('foo')
        post_data = self.post_data()
        bar = Domain.objects.create(name='bar.foo')
        self.ctnr.domains.add(bar)
        # Get the '_' in SRV records
        post_data['label'] = post_data['label'][0] + 'buzz'
        post_data['domain'] = bar.pk
        self.ctnr.domains.add(root_domain)
        return root_domain, post_data

    def test_no_ns_in_view(self):
        root_domain, post_data = self.get_domain_and_post_data()
        ns = root_domain.nameserver_set.all()[0]
        ns.views.remove(self.public_view)
        ns.views.remove(self.private_view)
        # We now have a zone with nameservers that aren't in any views. No
        # record should be allowed to be in the view

        start_obj_count = self.model.objects.count()
        post_data['views'] = [self.public_view.pk]

        # Create the object then get the object
        resp = self.client.post(self.model.get_create_url(),
                                post_data, follow=True)
        self.assertEqual(resp.status_code, 200)
        new_obj_count = self.model.objects.count()

        # Nothing should have been created
        self.assertEqual(start_obj_count, new_obj_count)

        ns.views.add(self.public_view)

        # Okay, we should be able to add to the public view now
        start_obj_count = self.model.objects.count()
        resp = self.client.post(self.model.get_create_url(),
                                post_data, follow=True)
        self.assertIn(
            resp.status_code, (200, 302),
            "Couldn't add to public view\n" + format_response(resp))
        new_obj_count = self.model.objects.count()
        self.assertEqual(start_obj_count + 1, new_obj_count)


class AddressRecordViewTests(TestCase, NoNSTests):
    fixtures = ['test_users/test_users.json']
    model = AddressRecord
    name = 'address_record'

    def setUp(self):
        test_data = {
            'label': 'foo',
            'ip_type': '4',
            'ip_str': '196.168.1.1',
        }
        do_setUp(self, test_data)

    def post_data(self):
        return {
            'label': 'bar',
            'domain': self.domain.pk,
            'ip_type': '4',
            'ip_str': '196.168.1.2',
            'ttl': '400',
            'description': 'yo',
            'ctnr': self.ctnr.pk,
        }


class CNAMEViewTests(TestCase, NoNSTests):
    fixtures = ['test_users/test_users.json']
    model = CNAME
    name = 'cname'

    def setUp(self):
        test_data = {
            'label': 'foo',
            'target': 'bar',
        }
        do_setUp(self, test_data)

    def post_data(self):
        return {
            'label': 'buzz',
            'domain': self.domain.pk,
            'target': 'burp',
            'ctnr': self.ctnr.pk,
        }


class NSViewTests(TestCase, GenericViewTests):
    fixtures = ['test_users/test_users.json']
    model = Nameserver
    name = 'nameserver'

    def setUp(self):
        self.domain = create_zone('foo')
        test_data = {
            'server': 'foo',
        }
        do_setUp(self, test_data)

    def post_data(self):
        return {
            'domain': self.domain.pk,
            'server': 'bar',
        }

    def test_no_ns_in_view(self):
        root_domain = create_zone('asdfdjhjd')
        self.ctnr.domains.add(root_domain)
        ns = root_domain.nameserver_set.all()[0]
        ns.views.add(self.public_view, self.private_view)

        cn = CNAME.objects.create(
            label='asdf', domain=root_domain, target='test.com',
            ctnr=self.ctnr)
        cn.views.add(self.public_view)

        self.assertEqual(ns.domain.soa, cn.domain.soa)

        # We now should have a nameserver and a CNAME in the public view. The
        # nameserver should not be allowed to disable its public view

        # Try to remove the public view
        self.assertIn(self.public_view, ns.views.all())
        self.assertIn(self.private_view, ns.views.all())
        post_data = self.post_data()
        post_data['domain'] = ns.domain.pk
        post_data['views'] = [self.private_view.pk]
        resp = self.client.post(
            ns.get_update_url(), post_data, follow=True
        )
        self.assertEqual(resp.status_code, 200)
        # Make sure it's still there
        ns = ns.reload()
        # Make sure the view is still there
        # The clean method should prevent it from being deleted
        self.assertIn(self.public_view, ns.views.all())

        # Try to remove the private view
        # This should be allowed
        self.assertIn(self.public_view, ns.views.all())
        post_data = self.post_data()
        post_data['views'] = [self.public_view.pk]
        resp = self.client.post(
            ns.get_update_url(), post_data, follow=True
        )
        self.assertEqual(resp.status_code, 200)
        # Make sure it's still there
        ns = ns.reload()
        # Make sure the view is still there
        # The clean method should prevent it from being deleted
        self.assertNotIn(self.private_view, ns.views.all())


class MXViewTests(TestCase, NoNSTests):
    fixtures = ['test_users/test_users.json']
    model = MX
    name = 'mx'

    def setUp(self):
        test_data = {
            'label': 'foo',
            'server': 'bar',
            'priority': 123,
            'ttl': 213
        }
        do_setUp(self, test_data)

    def post_data(self):
        return {
            'domain': self.domain.pk,
            'label': 'buzz',
            'server': 'burp',
            'priority': 123,
            'ttl': 213,
            'ctnr': self.ctnr.pk,
        }


class PTRViewTests(TestCase, NoNSTests):
    fixtures = ['test_users/test_users.json']
    model = PTR
    name = 'ptr'

    def get_domain_and_post_data(self):
        # This is different for classes that have ips instead of fqdns
        root_domain = Domain.objects.get(name='9.ip6.arpa')
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
            'fqdn': 'foo.bar',
            'ip_type': '4',
            'ip_str': '196.168.1.2',
        }
        do_preUp(self)
        Domain.objects.create(name='ip6.arpa')
        root_domain = create_zone('9.ip6.arpa')
        Domain.objects.create(name='168.196.in-addr.arpa')
        Domain.objects.create(name='1.168.196.in-addr.arpa')

        create_network_range(network_str='196.168.0.0/16',
                             start_str='196.168.1.0', end_str='196.168.1.253',
                             range_type='st', ip_type='4', domain=self.domain,
                             ctnr=self.ctnr)

        Domain.objects.create(name=ip_to_reverse_name(test_data['ip_str']))
        do_postUp(self, test_data, use_domain=False, use_rdomain=True)

    def post_data(self):
        new_domain = Domain.objects.create(name='boop')
        self.ctnr.domains.add(new_domain)
        return {
            'label': 'buzz',
            'domain': new_domain.pk,
            'ip_type': '4',
            'ip_str': '196.168.1.3',
            'description': 'yo',
            'ctnr': self.ctnr.pk,
        }

    def test_update_reverse_domain(self):
        eq_(self.test_obj.reverse_domain.name, '196.in-addr.arpa')
        post_data = self.post_data()

        self.client.post(self.test_obj.get_update_url(), post_data,
                         follow=True)
        updated_obj = PTR.objects.get(id=self.test_obj.id)
        eq_(updated_obj.ip_str, '196.168.1.3')


class SRVViewTests(TestCase, NoNSTests):
    fixtures = ['test_users/test_users.json']
    model = SRV
    name = 'srv'

    def setUp(self):
        test_data = {
            'label': '_foo',
            'target': 'bar',
            'priority': 2,
            'weight': 2222,
            'port': 222
        }
        do_setUp(self, test_data)

    def post_data(self):
        new_domain = Domain.objects.create(name='boop')
        self.ctnr.domains.add(new_domain)
        return {
            'label': '_buzz',
            'domain': new_domain.pk,
            'target': 'burp',
            'priority': 2,
            'weight': 2222,
            'port': 222,
            'ctnr': self.ctnr.pk,
        }


class TXTViewTests(TestCase, NoNSTests):
    fixtures = ['test_users/test_users.json']
    model = TXT
    name = 'txt'

    def setUp(self):
        test_data = {
            'label': 'foo',
            'txt_data': 'foo foo foo',
        }
        do_setUp(self, test_data)

    def post_data(self):
        return {
            'label': 'bar',
            'domain': self.domain.pk,
            'txt_data': 'bar bar bar',
            'ctnr': self.ctnr.pk,
        }


class SSHFPViewTests(TestCase, NoNSTests):
    fixtures = ['test_users/test_users.json']
    model = SSHFP
    name = 'sshfp'

    def setUp(self):
        test_data = {
            'label': 'foo',
            'algorithm_number': 1,
            'fingerprint_type': 1,
            'key': '9d97e98f8af710c7e7fe703abc8f639e0ee50222'
        }
        do_setUp(self, test_data)

    def post_data(self):
        return {
            'label': 'bar',
            'domain': self.domain.pk,
            'algorithm_number': 1,
            'fingerprint_type': 1,
            'key': '9d97e98f8af710c7e7fe703abc8f639e0ee50111',
            'ctnr': self.ctnr.pk,
        }
