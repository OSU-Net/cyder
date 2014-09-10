import json
from django.contrib.auth.models import User
from django.test.client import Client
from django.test import TestCase
from rest_framework.test import APIClient

from cyder.api.authtoken.models import Token
from cyder.base.eav.models import Attribute, EAVBase
from cyder.base.eav.constants import ATTRIBUTE_INVENTORY
from cyder.base.eav.validators import VALUE_TYPES
from cyder.core.ctnr.models import Ctnr
from cyder.cydns.domain.models import Domain
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.soa.models import SOA
from cyder.cydns.view.models import View
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range


API_VERSION = '1'


def create_network_range(network_str, start_str, end_str, range_type,
                         ip_type, domain, ctnr):
    n = Network(ip_type=ip_type, network_str=network_str)
    n.save()

    r = Range(network=n, range_type=range_type, start_str=start_str,
              end_str=end_str, domain=domain, ip_type=ip_type)
    r.save()

    ctnr.ranges.add(r)


def build_sample_domain():
    """Build SOA, domain, view, and nameserver records for testing."""
    domain, _ = Domain.objects.get_or_create(name="domain")
    soa, _ = SOA.objects.get_or_create(
        primary="ns1.oregonstate.edu", contact="hostmaster.oregonstate.edu",
        root_domain=domain, description="Test SOA")
    view, _ = View.objects.get_or_create(name='public')
    nameserver, _ = Nameserver.objects.get_or_create(
        domain=domain, server="ns1.oregonstate.edu", ttl=3600)
    nameserver.views.add(view)
    return domain, view


def build_domain(label, domain_obj):
    """Create a domain from a label and domain object."""
    domain_name = label + "." + domain_obj.name
    domain, _ = Domain.objects.get_or_create(name=domain_name)
    return domain


class APIEAVTestMixin(object):
    """Mixin to test endpoints with key-value support."""
    def test_eav(self):
        eav_attr = self.model.__name__.lower() + "av_set"

        obj = self.create_data()

        # init attribute
        attr, _ = Attribute.objects.get_or_create(
            name="Test Attribute", attribute_type=ATTRIBUTE_INVENTORY,
            value_type="string")

        getattr(obj, eav_attr).get_or_create(
            attribute=attr, value='Test Value', entity=obj)

        resp = self.http_get(self.object_url(obj.id))
        eavs = json.loads(resp.content)[eav_attr]

        for eav in eavs:
            if eav['attribute'] == 'Test Attribute':
                assert eav['value'] == 'Test Value'
                break
        else:
            assert 1 == 0, "The test attribute-value pair could not be found."
        self.model.objects.filter(id=obj.id).delete()


class APITests(TestCase):
    """Base class for API Tests. This contains a lot of helpful methods,
    the core tests to run on every object, and the code that starts off
    building the test data.

    This class shouldn't actually be run itself. Rather it serves as an
    abstract base class for the actual tests you want to run. At a minimum,
    any class that inherits from this class for the purpose of testing
    (i.e. not a further abstract class) must declare the class attribute
    ``model``, which should contain a reference to the model class for the
    record type that you are testing, and the method create_data(), which
    must return a valid object of the type that you want to test. Here's
    a simple example:

    .. code:: python

        class XXXAPI_Test:
            model = XXX

            def create_data(self):
                data = {
                    'label': 'foo',
                    'domain': self.domain,
                    # ...
                }
                obj = self.model(**data)
                obj.save()
                # further changes, such as adding views, can be done here
                return obj

    More complex implementations are possible. For example, for records that
    are mostly similar except for small differences (such as address records,
    PTR records, and interfaces), I have created abstract base classes that
    inherit from this class and create basic test data, while allowing the
    classes that inherit from it to define the case-specific data.
    """
    __test__ = False  # keep nose from trying to treat this as a test class
    fixtures = ['test_users/test_users.json']

    client = APIClient()

    f_root_url = "/api/v{0}/"
    f_object_list_url = "/api/v{0}/{1}/{2}/"
    f_object_url = "/api/v{0}/{1}/{2}/{3}/"

    def setUp(self):
        if hasattr(self, "url"):
            url = self.url
        else:
            url = self.model.get_list_url()
        root, urlname = tuple(url.strip("/").split("/"))

        self.ctnr, _ = Ctnr.objects.get_or_create(name="TestCtnr")
        self.domain, self.view = build_sample_domain()
        self.ctnr.domains.add(self.domain)
        self.token = Token.objects.create(
            user=User.objects.get(username="test_superuser")).key
        self.authheader = {'HTTP_AUTHORIZATION': 'Token ' + self.token}
        self.root_url = self.f_root_url.format(API_VERSION)
        self.object_list_url = self.f_object_list_url.format(
            API_VERSION, root, urlname)
        self.object_url = lambda n: self.f_object_url.format(
            API_VERSION, root, urlname, n)

    def http_get(self, url):
        return self.client.get(url, **self.authheader)

    def assertEqualKeys(self, a, b):
        for key in a:
            assert a[key] == b[key]

    @staticmethod
    def assertHttpOK(resp):
        assert resp.status_code == 200

    @staticmethod
    def assertHttpUnauthorized(resp):
        assert resp.status_code == 401

    @staticmethod
    def assertHttpNotFound(resp):
        assert resp.status_code == 404

    @staticmethod
    def assertHttpMethodNotAllowed(resp):
        assert resp.status_code == 405

    def metatest_unauthorized(self, url):
        resp = self.client.get(url)
        self.assertHttpUnauthorized(resp)
        assert json.loads(resp.content)['detail'] == \
            "Authentication credentials were not provided."

    def test_unauthorized_root(self):
        self.metatest_unauthorized(self.root_url)

    def test_unauthorized_list(self):
        self.metatest_unauthorized(self.object_list_url)

    def test_unauthorized_detail(self):
        self.metatest_unauthorized(self.object_url(1))

    def test_nonexistent(self):
        obj = self.create_data()
        bad_id = obj.id
        self.model.objects.filter(id=bad_id).delete()
        resp = self.client.get(
            self.object_url(bad_id), **self.authheader)
        self.assertHttpNotFound(resp)
        assert json.loads(resp.content)['detail'] == "Not found"

    def test_empty_list(self):
        obj = self.create_data()
        bad_id = obj.id
        obj.delete()
        resp = self.client.get(self.object_list_url,
                               data={'i:id__exact': bad_id},
                               **self.authheader)
        self.assertHttpOK(resp)
        data = json.loads(resp.content)
        assert 'count' in data
        assert data['count'] == 0

    def test_existing(self):
        obj = self.create_data()
        resp = self.client.get(self.object_url(obj.id),
                               **self.authheader)
        self.assertHttpOK(resp)
        self.model.objects.filter(id=obj.id).delete()
