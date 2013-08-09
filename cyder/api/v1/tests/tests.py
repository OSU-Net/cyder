# Cyder imports
import cyder
from cyder.api.v1.tests.base import CyderAPITestClient, HttpAssertsMixin
from cyder.core.cyuser.backends import _has_perm
from cyder.cydns.tests.utils import create_fake_zone

# Model imports
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.core.ctnr.models import Ctnr
from cyder.cydns.domain.models import Domain
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.srv.models import SRV
from cyder.cydns.sshfp.models import SSHFP
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.core.system.models import System
from cyder.cydns.txt.models import TXT


API_VERSION = '1'


class APITests(object, HttpAssertsMixin):
    fixtures = ['test_users/test_users.json']

    object_list_url = "/api/v{0}/{1}/"
    object_url = "/api/v{0}/{1}/{2}/"

    def setUp(self):
        self.client = CyderAPITestClient(self.serializer)
        self.object_list_url = self.object_list_url.format(
            API_VERSION, str(self.test_type.__name__).lower())
        self.object_url = lambda n: self.object_url.format(
            API_VERSION, str(self.test_type.__name__).lower(), n)

    def generic_create(self, post_data):
        obj_count = self.test_type.objects.count()
        resp = self.client.post(self.object_list_url, data=post_data)
        self.assertHttpCreated(resp)
        assert self.test_type.objects.count() == obj_count + 1
        return resp, post_data

    def assertEqualKeys(self, a, b):
        for key in a:
            assert a[key] == b[key]

    def test1_nonexistent(self):
        resp = self.client.get(self.object_url('1'))
        self.assertHttpNotFound(resp)

    def test2_create(self):
        resp, post_data = self.generic_create(
            self.post_data(), user, creds)
        new_object_url = resp.items()[2][1]

