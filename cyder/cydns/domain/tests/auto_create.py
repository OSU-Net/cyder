from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.test import TestCase

from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.ptr.models import PTR
from cyder.cydns.txt.models import TXT
from cyder.cydns.mx.models import MX
from cyder.cydns.srv.models import SRV
from cyder.cydns.domain.models import Domain
from cyder.cydns.domain.models import ValidationError, _name_to_domain
from cyder.cydns.ip.models import ipv6_to_longs, Ip
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.domain.models import Domain
from cyder.cydns.utils import ensure_label_domain, prune_tree
from cyder.cydns.soa.models import SOA

from cyder.cydhcp.site.models import Site



class AutoCreateTests(TestCase):
    """These tests should cover zone insurance and delegation blocking.
    Purgeable Domains
    """

    def test_delegation_block(self):
        s, _ = SOA.objects.get_or_create(primary="foo", contact="Foo",
                                         comment="foo")
        c = Domain(name='com')
        c.soa = s
        c.save()
        self.assertFalse(c.purgeable)
        f_c = Domain(name='foo.com')
        f_c.delegated = True
        f_c.save()
        self.assertFalse(f_c.purgeable)
        self.assertTrue(f_c.delegated)

        fqdn = "z.baz.foo.com"
        self.assertRaises(ValidationError, ensure_label_domain, fqdn)

    def test_no_soa_block(self):
        fqdn = "baz.bar.foo.eu"
        self.assertRaises(ValidationError, ensure_label_domain, fqdn)
        c = Domain(name='eu')
        c.save()
        self.assertFalse(c.purgeable)
        f_c = Domain(name='foo.eu')
        f_c.save()
        self.assertFalse(f_c.purgeable)

        # Even with domains there, they aren't part of a zone and should so
        # creation should fail.
        self.assertRaises(ValidationError, ensure_label_domain, fqdn)
