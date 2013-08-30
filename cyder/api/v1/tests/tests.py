import json
from django.contrib.auth.models import User
from django.test.client import Client

# Cyder imports
from cyder.base.tests.test_views_template import random_label, random_byte

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
from cyder.cydhcp.interface.dynamic_intr.models import DynamicInterface
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.range.models import Range
from cyder.core.system.models import System
from cyder.cydns.txt.models import TXT
from cyder.cydns.view.models import View


API_VERSION = '1'


def build_sample_domain():
    """Build SOA, domain, view, and nameserver records for testing."""
    soa, _ = SOA.objects.get_or_create(
        primary="ns{0}.oregonstate.edu".format(random_byte()),
        contact="hostmaster{0}.oregonstate.edu".format(random_label()),
        description="Test SOA " + random_label())
    domain_name = "domain-" + random_label()
    domain, _ = Domain.objects.get_or_create(name=domain_name, soa=soa)
    view, _ = View.objects.get_or_create(name='public')
    nameserver = Nameserver(
        domain=domain, server="ns1.a" + random_label() + ".net", ttl=3600)
    nameserver.save()
    nameserver.views.add(view)
    return domain, view


def build_domain(label, domain_obj):
    """Create a domain from a label and domain object."""
    domain_name = label + "." + domain_obj.name
    domain, _ = Domain.objects.get_or_create(
        name=domain_name, soa=domain_obj.soa)
    return domain


class APITests(object):
    """Base class for API Tests. This contains a lot of helpful methods,
    the core tests to run on every object, and the code that starts off
    building the test data.

    This class shouldn't actually be run itself. Rather it serves as an
    abstract base class for the actual tests you want to run. At a minimum,
    any class that inherits from this class for the purpose of testing
    (i.e. not a further abstract class) must declare the class attribute
    ``model``, which should contain a reference to the model class for the
    record type that you are testing, and the method setup_data(), which
    must return a valid object of the type that you want to test. Here's
    a simple example:

    .. code:: python

        class XXXAPI_Test:
            model = XXX

            def setup_data(self):
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
    inherit from this class and define basic setup data, while allowing the 
    classes that inherit from it to define the case-specific data.
    """
    fixtures = ['test_users/test_users.json']

    client = Client()

    f_root_url = "/api/v{0}/"
    f_object_list_url = "/api/v{0}/{1}/"
    f_object_url = "/api/v{0}/{1}/{2}/"

    def __init__(self, *args, **kwargs):
        if hasattr(self, 'urlname'):
            urlname = getattr(self, 'urlname')
        else:
            urlname = str(self.model.__name__).lower()

        self.domain, self.view = build_sample_domain()
        self.token = Token.objects.create(
            user=User.objects.get(username="test_superuser")).key
        self.authheader = {'HTTP_AUTHORIZATION': 'Token ' + self.token}
        self.root_url = self.f_root_url.format(API_VERSION)
        self.object_list_url = self.f_object_list_url.format(
            API_VERSION, urlname)
        self.object_url = lambda n: self.f_object_url.format(
            API_VERSION, urlname, n)

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
        self.metatest_unauthorized(self.root_url)

    def test_unauthorized_list(self):
        self.metatest_unauthorized(self.object_list_url)

    def test_unauthorized_detail(self):
        self.metatest_unauthorized(self.object_url(1))

    def test_nonexistent(self):
        obj = self.setup_data()
        bad_id = obj.id
        self.model.objects.filter(id=bad_id).delete()
        resp = self.client.get(
            self.object_url(bad_id), **self.authheader)
        self.assertHttpNotFound(resp)
        assert json.loads(resp.content)['detail'] == "Not found"

    def test_existing(self):
        obj  = self.setup_data()
        resp = self.client.get(self.object_url(obj.id),
                               **self.authheader)
        self.assertHttpOK(resp)


class AddressRecordBase(APITests):
    model = AddressRecord

    def setup_data(self):
        return {
            'description': 'Address Record',
            'ttl': 420,
            'label': 'foo',
            'domain': self.domain,
        }


class AddressRecordv4API_Test(AddressRecordBase):
    def setup_data(self):
        data = super(AddressRecordv4API_Test, self).setup_data()
        data.update({
            'ip_str': "11.193.4.12",
            'ip_type': '4',
        })
        obj = self.model(**data)
        obj.save()
        obj.views.add(self.view.id)
        return obj


class AddressRecordv6API_Test(AddressRecordBase):
    model = AddressRecord

    def setup_data(self):
        data = super(AddressRecordv6API_Test, self).setup_data()
        data.update({
            'ip_str': "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            'ip_type': '6',
        })
        obj, _ = self.model.objects.get_or_create(**data)
        obj.save()
        obj.views.add(self.view.id)
        return obj


class CNAMEAPI_Test(APITests):
    model = CNAME

    def setup_data(self):
        data = {
            'description': 'CNAME record',
            'ttl': 420,
            'label': 'foo',
            'domain': self.domain,
            'target': 'bar.' + self.domain.name,
        }
        obj, _ = self.model.objects.get_or_create(**data)
        obj.save()
        obj.views.add(self.view.id)
        return obj


class DomainAPI_Test(APITests):
    model = Domain

    def setup_data(self):
        data = {
            'name': random_label() + '.' + self.domain.name,
            'master_domain': self.domain,
            'soa': self.domain.soa,
            'is_reverse': False,
            'dirty': False,
            'purgeable': False,
            'delegated': True,
        }
        obj, _ = self.model.objects.get_or_create(**data)
        obj.save()
        return obj

    def test_1_related(self):
        """Test that Domain relations work and make sense."""
        # get our test domain object
        domain = self.setup_data()
        resp = self.client.get(self.object_url(domain.id), **self.authheader)

        # try to retrieve the master domain
        data = json.loads(resp.content)
        master_resp = self.client.get(data['master_domain'], **self.authheader)

        # check the response
        self.assertHttpOK(master_resp)
        master_data = json.loads(master_resp.content)
        assert master_data['name'] == self.domain.name


class DynamicInterfaceAPI_Test(APITests):
    # this should probably be updated to test both IPv6 and IPv4
    model = DynamicInterface

    def __init__(self, *args, **kwargs):
        Domain.objects.get_or_create(name='arpa')
        self.ctnr, _ = Ctnr.objects.get_or_create(
            name="Test")
        self.system, _ = System.objects.get_or_create(
            name="TestSystem")
        self.range, _ = Range.objects.get_or_create(
            start_str="12.12.0.0", end_str="12.12.255.255",
            is_reserved=True)
        super(DynamicInterfaceAPI_Test, self).__init__(self, *args, **kwargs)

    def setup_data(self):
        data = {
            'ctnr': self.ctnr,
            'range': self.range,
        }
        obj, _ = self.model.objects.get_or_create(**data)
        obj.save()
        return obj

    def test_keyvalues(self):
        obj = self.setup_data()
        obj.dynamicintrkeyvalue_set.get_or_create(
            key='Test Key', value='Test Value')
        resp = self.client.get(self.object_url(obj.id), **self.authheader)
        keyvalues = json.loads(resp.content)['dynamicintrkeyvalue_set'][0]
        assert keyvalues['key'] == "Test Key"
        assert keyvalues['value'] == "Test Value"


class MXAPI_Test(APITests):
    model = MX

    def setup_data(self):
        data = {
            'description': 'MX Record',
            'label': 'mail',
            'domain': self.domain,
            'server': "relay.oregonstate.edu",
            'ttl': 420,
            'priority': 420,
        }
        obj, _ = self.model.objects.get_or_create(**data)
        obj.save()
        return obj


class NameserverAPI_Test(APITests):
    model = Nameserver

    def setup_data(self):
        data = {
            'server': 'relay.oregonstate.edu',
            'description': 'Nameserver Record',
            'ttl': 420,
            'domain': self.domain
        }
        obj, _ = self.model.objects.get_or_create(**data)
        obj.save()
        return obj


class PTRBase(APITests):
    model = PTR

    def setup_data(self):
        Domain.objects.get_or_create(name='arpa')

        return {
            'description': 'PTR Record',
            'ttl': 420,
            'name': random_label()
        }


class PTRv4API_Test(PTRBase):
    model = PTR

    def setup_data(self):
        super(PTRv4API_Test, self).setup_data()
        Domain.objects.get_or_create(name='in-addr.arpa')
        Domain.objects.get_or_create(name='11.in-addr.arpa')

        data = {
            'ip_str': "11.{0}.{1}.{2}".format(
                random_byte(), random_byte(), random_byte()),
            'ip_type': '4',
        }
        obj, _ = self.model.objects.get_or_create(**data)
        obj.save()
        return obj


class PTRv6API_Test(PTRBase):
    model = PTR

    def setup_data(self):
        super(PTRv6API_Test, self).setup_data()
        Domain.objects.get_or_create(name='ip6.arpa')
        Domain.objects.get_or_create(name='1.ip6.arpa')

        data = {
            'ip_str': "1000:{0}:{1}:{2}:{3}:{4}:{5}:{6}".format(
                random_byte(), random_byte(), random_byte(), random_byte(),
                random_byte(), random_byte(), random_byte()),
            'ip_type': '6',
        }
        obj, _ = self.model.objects.get_or_create(**data)
        obj.save()
        return obj


class SRVAPI_Test(APITests):
    model = SRV

    def setup_data(self):
        data = {
            'description': 'SRV Record',
            'ttl': 420,
            'label': '_' + random_label(),
            'domain': self.domain,
            'target': random_label(),
            'priority': 420,
            'weight': 420,
            'port': 420,
        }
        obj, _ = self.model.objects.get_or_create(**data)
        obj.save()
        return obj


class SSHFPAPI_Test(APITests):
    model = SSHFP

    def setup_data(self):
        data = {
            'description': 'SSHFP Record',
            'ttl': 420,
            'label': 's' + random_label(),
            'domain': self.domain,
            'algorithm_number': 1,
            'fingerprint_type': 1,
            'key': '0123456789abcdef0123456789abcdef01234567'
        }
        obj, _ = self.model.objects.get_or_create(**data)
        obj.save()
        return obj


class StaticInterfaceBase(APITests):
    model = StaticInterface

    def __init__(self, *args, **kwargs):
        Domain.objects.get_or_create(name='arpa')
        self.ctnr, _ = Ctnr.objects.get_or_create(
            name="Test")
        self.system, _ = System.objects.get_or_create(
            name="TestSystem")
        super(StaticInterfaceBase, self).__init__(self, *args, **kwargs)

    def setup_data(self):
        return {
            'ctnr': self.ctnr,
            'description': 'm' + random_label(),
            'ttl': random_byte(),
            'mac': '11:22:33:44:55:00',
            'system': self.system,
            'label': 'x' + random_label(),
            'domain': self.domain,
            'dhcp_enabled': False,
            'dns_enabled': True,
        }

    def test_keyvalues(self):
        obj = self.setup_data()
        obj.staticintrkeyvalue_set.get_or_create(
            key='domain-name', value='foo.oregonstate.edu')
        resp = self.client.get(self.object_url(obj.id), **self.authheader)
        keyvalues = json.loads(resp.content)['staticintrkeyvalue_set'][0]
        assert keyvalues['key'] == 'domain-name'
        assert keyvalues['value'] == 'foo.oregonstate.edu'



class StaticInterfaceV4API_Test(StaticInterfaceBase):
    def __init__(self, *args, **kwargs):
        super(StaticInterfaceV4API_Test, self).__init__(self, *args, **kwargs)
        Domain.objects.get_or_create(name='in-addr.arpa')
        Domain.objects.get_or_create(name='11.in-addr.arpa')

    def setup_data(self):
        data = super(StaticInterfaceV4API_Test, self).setup_data()
        data.update({
            'ip_str': "11.12.14.255",
            'ip_type': '4'
        })
        obj, _ = self.model.objects.get_or_create(**data)
        obj.save()
        return obj


class StaticInterfaceV6API_Test(StaticInterfaceBase):
    def __init__(self, *args, **kwargs):
        super(StaticInterfaceV6API_Test, self).__init__(self, *args, **kwargs)
        Domain.objects.get_or_create(name='ip6.arpa')
        Domain.objects.get_or_create(name='2.ip6.arpa')

    def setup_data(self):
        data = super(StaticInterfaceV6API_Test, self).setup_data()
        data.update({
            'ip_str': "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            'ip_type': '6',
        })
        obj, _ = self.model.objects.get_or_create(**data)
        obj.save()
        return obj


class SystemAPI_Test(APITests):
    model = System

    def setup_data(self):
        data = {
            'name': 'test_system',
        }
        obj, _ = self.model.objects.get_or_create(**data)
        obj.save()
        return obj

    def test_keyvalues(self):
        obj = self.setup_data()
        obj.systemkeyvalue_set.get_or_create(
            key='Test Key', value='Test Value')
        resp = self.client.get(self.object_url(obj.id), **self.authheader)
        keyvalues = json.loads(resp.content)['systemkeyvalue_set'][0]
        assert keyvalues['key'] == 'Test Key'
        assert keyvalues['value'] == 'Test Value'


class TXTAPI_Test(APITests):
    model = TXT

    def setup_data(self):
        data = {
            'label': 'foo',
            'domain': self.domain,
            'txt_data': random_label(),
        }
        obj, _ = self.model.objects.get_or_create(**data)
        obj.save()
        return obj
