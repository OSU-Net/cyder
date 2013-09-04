import json
from django.contrib.auth.models import User
from django.test.client import Client

from cyder.api.authtoken.models import Token
from cyder.cydns.domain.models import Domain
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.soa.models import SOA
from cyder.cydns.view.models import View


API_VERSION = '1'


def build_sample_domain():
    """Build SOA, domain, view, and nameserver records for testing."""
    soa, _ = SOA.objects.get_or_create(
        primary="ns1.oregonstate.edu", contact="hostmaster.oregonstate.edu",
        description="Test SOA")
    domain, _ = Domain.objects.get_or_create(name="domain", soa=soa)
    view, _ = View.objects.get_or_create(name='public')
    nameserver, _ = Nameserver.objects.get_or_create(
        domain=domain, server="ns1.oregonstate.edu", ttl=3600)
    nameserver.views.add(view)
    return domain, view


def build_domain(label, domain_obj):
    """Create a domain from a label and domain object."""
    domain_name = label + "." + domain_obj.name
    domain, _ = Domain.objects.get_or_create(
        name=domain_name, soa=domain_obj.soa)
    return domain


class APIKVTestMixin(object):
    """Mixin to test endpoints with key-value support."""
    def test_keyvalues(self):
        """Test key-value retrieval."""
        obj = self.create_data()
        getattr(obj, self.keyvalue_attr).get_or_create(
            key='Test Key', value='Test Value')
        resp = self.http_get(self.object_url(obj.id))
        keyvalues = json.loads(resp.content)[self.keyvalue_attr][0]
        assert keyvalues['key'] == 'Test Key'
        assert keyvalues['value'] == 'Test Value'
        self.model.objects.filter(id=obj.id).delete()


class APITests(object):
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

    More complex implmentations are possible. For example, for records that
    are mostly similar except for small differences (such as address records,
    PTR records, and interfaces), I have created abstract base classes that
    inherit from this class and create basic test data, while allowing the
    classes that inherit from it to define the case-specific data.
    """
    fixtures = ['test_users/test_users.json']

    client = Client()

    f_root_url = "/api/v{0}/"
    f_object_list_url = "/api/v{0}/{1}/{2}/"
    f_object_url = "/api/v{0}/{1}/{2}/{3}/"

    def __init__(self, *args, **kwargs):
        if hasattr(self, 'urlname'):
            urlname = getattr(self, 'urlname')
        else:
            urlname = str(self.model.__name__).lower()

        root = getattr(self, 'root')

        self.domain, self.view = build_sample_domain()
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
        """Make sure unauthorized users can't access the root view."""
        self.metatest_unauthorized(self.root_url)

    def test_unauthorized_list(self):
        """Make sure unauthorized users can't access the list view."""
        self.metatest_unauthorized(self.object_list_url)

    def test_unauthorized_detail(self):
        """Make sure unauthorized users can't access the detail view."""
        self.metatest_unauthorized(self.object_url(1))

    def test_nonexistent(self):
        obj = self.create_data()
        bad_id = obj.id
        self.model.objects.filter(id=bad_id).delete()
        resp = self.client.get(
            self.object_url(bad_id), **self.authheader)
        self.assertHttpNotFound(resp)
        assert json.loads(resp.content)['detail'] == "Not found"

    def test_existing(self):
        obj = self.create_data()
        resp = self.client.get(self.object_url(obj.id),
                               **self.authheader)
        self.assertHttpOK(resp)
        self.model.objects.filter(id=obj.id).delete()

