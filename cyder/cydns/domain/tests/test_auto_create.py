from django.core.exceptions import ValidationError

from cyder.cydns.domain.models import Domain
from cyder.cydns.utils import ensure_label_domain
from cyder.cydns.soa.models import SOA

from basedomain import BaseDomain


class AutoCreateTests(BaseDomain):
    """These tests should cover zone insurance and delegation blocking.
    Purgeable Domains
    """

    def test_delegation_block(self):
        c = Domain.objects.create(name='com')
        s = SOA.objects.create(
            primary="foo", contact="Foo", root_domain=c, description="foo")
        self.assertFalse(c.purgeable)
        f_c = Domain.objects.create(name='foo.com', delegated=True)
        self.assertFalse(f_c.purgeable)
        self.assertTrue(f_c.delegated)

        fqdn = "z.baz.foo.com"
        self.assertRaises(ValidationError, ensure_label_domain, fqdn)

    def test_no_soa_block(self):
        fqdn = "baz.bar.foo.eu"
        self.assertRaises(ValidationError, ensure_label_domain, fqdn)
        c = Domain.objects.create(name='eu')
        self.assertFalse(c.purgeable)
        f_c = Domain.objects.create(name='foo.eu')
        self.assertFalse(f_c.purgeable)

        # Even with domains there, they aren't part of a zone and should so
        # creation should fail.
        self.assertRaises(ValidationError, ensure_label_domain, fqdn)

    def test_no_soa_block2(self):
        c = Domain.objects.create(name='moo')
        f_c = Domain.objects.create(name='foo.moo')
        s = SOA.objects.create(
            primary="bar23", contact="Foo", root_domain=f_c, description="bar")

        self.assertRaises(ValidationError, ensure_label_domain, "baz.moo")
