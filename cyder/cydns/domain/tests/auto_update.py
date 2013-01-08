from django.test import TestCase

from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.txt.models import TXT
from cyder.cydns.mx.models import MX
from cyder.cydns.srv.models import SRV
from cyder.cydns.domain.models import Domain
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.utils import ensure_label_domain
from cyder.cydns.soa.models import SOA


class UpdateRecordDeleteDomainTests(TestCase):

    def generic_check(self, obj, do_label=True, label_prefix=""):
        # Make sure all record types block
        c, _ = Domain.objects.get_or_create(name='foo22')
        self.assertFalse(c.purgeable)
        f_c, _ = Domain.objects.get_or_create(name='foo.foo22')
        s, _ = SOA.objects.get_or_create(primary="foo", contact="foo",
                                         description="foo.foo22")
        f_c.soa = s
        f_c.save()
        self.assertFalse(f_c.purgeable)
        fqdn = "bar.x.y.z.foo.foo22"
        label, the_domain = ensure_label_domain(fqdn)
        if do_label:
            # NS records don't like labels
            label = label_prefix + label
            obj.label = label
        obj.domain = the_domain
        obj.save()

        fqdn = "bar.x.y.xx.foo.foo22"
        label, new_domain = ensure_label_domain(fqdn)
        obj.domain = new_domain
        obj.save()

        # The original domain should have been deleted.
        self.assertFalse(Domain.objects.filter(name="x.y.z.foo.foo22"))
        # Make sure no objects were harmed.
        self.assertTrue(obj.__class__.objects.get(pk=obj.pk))
        obj.delete()
        # The new domain should now have been deleted.
        self.assertFalse(Domain.objects.filter(name="x.y.xx.foo.foo22"))

    def test_txt_update(self):
        txt = TXT(txt_data="Nthing")
        self.generic_check(txt)

    def test_addrees_record_update(self):
        addr = AddressRecord(ip_type='4', ip_str="10.2.3.4")
        self.generic_check(addr)

    def test_mx_update(self):
        mx = MX(server="foo", priority=4)
        self.generic_check(mx)

    def test_ns_update(self):
        ns = Nameserver(server="asdfasffoo")
        self.generic_check(ns, do_label=False)

    def test_srv_update(self):
        srv = SRV(target="foo", priority=4,
                  weight=4, port=34)
        self.generic_check(srv, label_prefix="_")

    def test_cname_update(self):
        cname = CNAME(target="foo")
        self.generic_check(cname)
