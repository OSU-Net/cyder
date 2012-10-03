from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.test import TestCase

from cyder.mozdns.address_record.models import AddressRecord
from cyder.mozdns.cname.models import CNAME
from cyder.mozdns.ptr.models import PTR
from cyder.mozdns.txt.models import TXT
from cyder.mozdns.mx.models import MX
from cyder.mozdns.srv.models import SRV
from cyder.mozdns.domain.models import Domain
from cyder.mozdns.domain.models import ValidationError, _name_to_domain
from cyder.mozdns.ip.models import ipv6_to_longs, Ip
from cyder.mozdns.nameserver.models import Nameserver
from cyder.mozdns.domain.models import Domain
from cyder.mozdns.utils import ensure_label_domain, prune_tree
from cyder.mozdns.soa.models import SOA

from cyder.core.site.models import Site

import pdb


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
