import json
from django.core import management
from django.contrib.auth.models import User
from django.test.client import Client, FakePayload

# Cyder imports
import cyder
from cyder.base.tests.test_views_template import random_label, random_byte
from cyder.cydns.tests.utils import create_fake_zone

# Model imports
from cyder.api.authtoken.models import Token
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.core.ctnr.models import Ctnr
from cyder.cydns.domain.models import Domain
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.soa.models import SOA
from cyder.cydns.srv.models import SRV
from cyder.cydns.sshfp.models import SSHFP
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.core.system.models import System
from cyder.cydns.txt.models import TXT


API_VERSION = '1'


def build_sample_domain():
    soa, _ = SOA.objects.get_or_create(
        primary="ns{0}.oregonstate.edu".format(random_byte()),
        contact="hostmaster.oregonstate.edu", description="Test SOA")
    domain_name = "domain-" + random_label()
    domain, _ = Domain.objects.get_or_create(name=domain_name, soa=soa)
    return domain


class APITests(object):
    fixtures = ['test_users/test_users.json']

    client = Client()

    f_root_url = "/api/v{0}/"
    f_object_list_url = "/api/v{0}/{1}/"
    f_object_url = "/api/v{0}/{1}/{2}/"

    def __init__(self):
        management.call_command('flush') # flush the db between tests
        self.domain = build_sample_domain()
        self.token = Token.objects.create(
            user=User.objects.get(username="test_superuser")).key
        self.authheader = {'HTTP_AUTHORIZATION': 'Token ' + self.token}
        self.root_url = self.f_root_url.format(API_VERSION)
        self.object_list_url = self.f_object_list_url.format(
            API_VERSION, str(self.model.__name__).lower())
        self.object_url = lambda n: self.f_object_url.format(
            API_VERSION, str(self.model.__name__).lower(), n)

    def setUp(self):
        """Set up the tests.

        Note for future maintainers: Do not assume like I did that setUp
        runs only once, at the start of tests. In fact, it runs between every
        test.
        """
        pass

    def assertEqualKeys(self, a, b):
        for key in a:
            assert a[key] == b[key]

    def assertHttpOK(self, resp):
        assert resp.status_code == 200

    def assertHttpUnauthorized(self, resp):
        assert resp.status_code == 401

    def assertHttpNotFound(self, resp):
        assert resp.status_code == 404

    def assertHttpMethodNotAllowed(self, resp):
        assert resp.status_code == 405

    def metatest_unauthorized(self, url):
        resp = self.client.get(url)
        self.assertHttpUnauthorized(resp)
        assert json.loads(resp.content)['detail'] == \
                "Authentication credentials were not provided."

    def test_unauthorized_root(self):
        """Test that unauthorized users can't access root."""
        self.metatest_unauthorized(self.root_url)

    def test_unauthorized_list(self):
        """Test that unauthorized users can't access the list view."""
        self.metatest_unauthorized(self.object_list_url)

    def test_unauthorized_detail(self):
        """Test that unauthorized users can't access the detail view."""
        self.metatest_unauthorized(self.object_url(1))

    def test_nonexistent(self):
        """Test that nonexistent records return 404 and are not found.

        This should probably be changed because it currently has a very low
        probability of returning a false negative.
        """
        resp = self.client.get(
            self.object_url(random_byte()), **self.authheader)
        self.assertHttpNotFound(resp)
        assert json.loads(resp.content)['detail'] == "Not found"

    def test_existing(self):
        """Check that existing records get returned properly.

        This might need to be converted into a separate test for each model.
        Checking that the data used to create the record is properly returned
        in the API is somewhat difficult and may require a bit of creativity.
        """
        obj, _ = self.model.objects.get_or_create(**self.setup_data)
        resp = self.client.get(self.object_url(obj.id),
                               **self.authheader)
        self.assertHttpOK(resp)


class AddressRecordV4API_Test(APITests):
    model = AddressRecord

    def setUp(self):
        super(AddressRecordV4API_Test, self).setUp()
        self.setup_data = {
            'description': 'IPv4 address record.',
            'ttl': 3600,
            'fqdn': 'subdomain.' + self.domain.name,
            'ip_str': "11.193.4.12",
            'ip_type': '4'
        }


class AddressRecordV6API_Test(APITests):
    model = AddressRecord

    def setUp(self):
        super(AddressRecordV6API_Test, self).setUp()
        self.setup_data = {
            'description': 'IPv6 address record.',
            'ttl': 3600,
            'fqdn': 'subdomain.' + self.domain.name,
            'ip_str': "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            'ip_type': '6'
        }


class CNAMEAPI_Test(APITests):
    model = CNAME

    def setUp(self):
        super(CNAMEAPI_Test, self).setUp()
        self.setup_data = {
            'description': 'CNAME record',
            'ttl': 3600,
            'fqdn': 'foo.' + self.domain.name,
            'target': self.domain.name
        }


class DomainAPI_Test(APITests):
    model = Domain

    def setUp(self):
        super(DomainAPI_test, self).setUp()
        self.setup_data = {
            'name': random_label() + '.' + self.domain.name,
            'master_domain': self.domain,
            'soa': self.domain.soa,
            'is_reverse': False,
            'dirty': False,
            'purgeable': False,
            'delegated': True,
        }

    def test_related(self):
        # get our test domain object
        domain = Domain.objects.create(**self.setup_data)
        resp = self.client.get(self.object_url(domain.id), **self.authheader)

        # try to retrieve the master domain
        data = json.loads(resp.content)
        master_resp = self.client.get(data['master_domain'], **self.authheader)

        # check the response
        self.assertHttpOK(master_resp)
        master_data = json.loads(master_resp.content)
        assert master_data['name'] == self.domain.name
