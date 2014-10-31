from cyder.core.system.models import System
from cyder.core.ctnr.models import Ctnr
from cyder.core.task.models import Task
from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range
from cyder.cydns.domain.models import Domain
from cyder.cydns.soa.models import SOA
from cyder.cydns.srv.models import SRV
from cyder.cydns.txt.models import TXT
from cyder.cydns.ptr.models import PTR
from cyder.cydns.mx.models import MX
from cyder.cydns.cname.models import CNAME
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.tests.utils import create_zone, DNSTest


class DirtySOATests(DNSTest):
    def setUp(self):
        super(DirtySOATests, self).setUp()

        self.r1 = create_zone(name='10.in-addr.arpa')
        self.sr = self.r1.soa
        self.sr.dirty = False
        self.sr.save()

        Domain.objects.create(name='bgaz')
        self.dom = create_zone('azg.bgaz')
        self.soa = self.dom.soa
        self.soa.dirty = False
        self.soa.save()
        Domain.objects.create(name='com')
        Domain.objects.create(name='bar.com')
        create_zone('foo.bar.com')

        self.rdom = create_zone('123.in-addr.arpa')
        self.rsoa = self.r1.soa
        self.rsoa.dirty = False
        self.rsoa.save()

        self.ctnr.domains.add(self.dom, self.rdom)

        self.s = System.objects.create(name='test_system')

        self.net = Network.objects.create(network_str='10.2.3.0/30')
        self.range = Range.objects.create(
            network=self.net, range_type=STATIC, start_str='10.2.3.1',
            end_str='10.2.3.2')
        self.ctnr.ranges.add(self.range)

    def test_print_soa(self):
        self.assertNotIn(self.soa.bind_render_record(), ('', None))
        self.assertNotIn(self.rsoa.bind_render_record(), ('', None))

    def generic_dirty(self, Klass, create_data, update_data, local_soa,
                      tdiff=1):
        create_data['ctnr'] = self.ctnr
        Task.dns.all().delete()  # Delete all tasks
        local_soa.dirty = False
        local_soa.save()
        rec = Klass.objects.create(**create_data)
        self.assertNotIn(rec.bind_render_record(), ('', None))
        local_soa = SOA.objects.get(pk=local_soa.pk)
        self.assertTrue(local_soa.dirty)
        self.assertLessEqual(tdiff, Task.dns.count())

        # Now try updating
        Task.dns.all().delete()  # Delete all tasks
        local_soa.dirty = False
        local_soa.save()
        local_soa = SOA.objects.get(pk=local_soa.pk)
        self.assertFalse(local_soa.dirty)
        for k, v in update_data.iteritems():
            setattr(rec, k, v)
        rec.save()
        local_soa = SOA.objects.get(pk=local_soa.pk)
        self.assertTrue(local_soa.dirty)
        self.assertLessEqual(tdiff, Task.dns.count())

        # Now delete
        Task.dns.all().delete()  # Delete all tasks
        local_soa.dirty = False
        local_soa.save()
        local_soa = SOA.objects.get(pk=local_soa.pk)
        self.assertFalse(local_soa.dirty)
        rec.delete()
        local_soa = SOA.objects.get(pk=local_soa.pk)
        self.assertTrue(local_soa.dirty)
        self.assertLessEqual(tdiff, Task.dns.count())

    def test_dirty_a(self):
        create_data = {
            'label': 'asdf',
            'domain': self.dom,
            'ip_str': '10.2.3.1',
            'ip_type': '4'
        }
        update_data = {
            'label': 'asdfx',
        }
        self.generic_dirty(AddressRecord, create_data, update_data, self.soa)

    def test_dirty_intr(self):
        create_data = {
            'label': 'asdf1',
            'domain': self.dom,
            'ip_str': '10.2.3.1',
            'ip_type': '4',
            'system': self.s,
            'mac': '11:22:33:44:55:66',
            'ctnr': self.ctnr,
        }
        update_data = {
            'label': 'asdfx1',
        }
        self.generic_dirty(StaticInterface, create_data, update_data, self.soa,
                           tdiff=2)

    def test_dirty_cname(self):
        create_data = {
            'label': 'asdf2',
            'domain': self.dom,
            'target': 'foo.bar.com',
        }
        update_data = {
            'label': 'asdfx2',
        }
        self.generic_dirty(CNAME, create_data, update_data, self.soa)

    def test_dirty_ptr(self):
        create_data = {
            'ip_str': '10.2.3.1',
            'ip_type': '4',
            'fqdn': 'foo.bar.com',
        }
        update_data = {
            'label': 'asdfx2',
        }
        self.generic_dirty(PTR, create_data, update_data, local_soa=self.sr)

    def test_dirty_mx(self):
        create_data = {
            'label': '',
            'domain': self.dom,
            'priority': 10,
            'server': 'foo.bar.com',
        }
        update_data = {
            'label': 'asdfx3',
        }
        self.generic_dirty(MX, create_data, update_data, self.soa)

    def test_dirty_ns(self):
        create_data = {
            'domain': self.dom,
            'server': 'foo.bar.com',
        }
        update_data = {
            'label': 'asdfx4',
        }
        self.generic_dirty(Nameserver, create_data, update_data, self.soa)

    def test_dirty_soa(self):
        self.soa.dirty = False
        self.soa.refresh = 123
        self.soa.save()
        self.assertTrue(self.soa.dirty)

    def test_dirty_srv(self):
        create_data = {
            'label': '_asdf7',
            'domain': self.dom,
            'priority': 10,
            'port': 10,
            'weight': 10,
            'target': 'foo.bar.com',
        }
        update_data = {
            'label': '_asdfx4',
        }
        self.generic_dirty(SRV, create_data, update_data, self.soa)

    def test_dirty_txt(self):
        create_data = {
            'label': 'asdf8',
            'domain': self.dom,
            'txt_data': 'some stuff',
        }
        update_data = {
            'label': 'asdfx5',
        }
        self.generic_dirty(TXT, create_data, update_data, self.soa)
