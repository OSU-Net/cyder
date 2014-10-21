import json
from django.contrib.auth.models import User

from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.workgroup.models import Workgroup
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydns.domain.models import Domain
from cyder.api.v1.tests.base import APITests


class CtnrAPI_Test(APITests):
    __test__ = True
    model = Ctnr

    def setUp(self):
        super(CtnrAPI_Test, self).setUp()

        self.user = User.objects.create(username='testuser')

        domain_data = {
            'name': 'www.' + self.domain.name,
            'delegated': True,
        }
        self.ctnr_domain = Domain.objects.create(
            name=('www.' + self.domain.name), delegated=True)

        range_network_site = Site.objects.create(name='site')
        range_network_vlan = Vlan.objects.create(name='vlan', number=420)
        range_network_vrf = Vrf.objects.create(name='vrf')

        range_network = Network.objects.create(
            site=range_network_site, vlan=range_network_vlan,
            vrf=range_network_vrf, ip_type='4', network_str='10.1.0.0/8')

        self.range = Range.objects.create(
            network=range_network, ip_type='4', start_str='10.1.0.0',
            end_str='10.1.0.255')

        self.workgroup = Workgroup.objects.create(name='workgroup')

    def create_data(self):
        self.ctnr = Ctnr.objects.create(name='ctnr')
        self.ctnruser = CtnrUser.objects.create(
            user=self.user, ctnr=self.ctnr, level=2)
        self.ctnr.domains.add(self.ctnr_domain)
        self.ctnr.ranges.add(self.range)
        self.ctnr.workgroups.add(self.workgroup)
        return self.ctnr

    def test_user_filter(self):
        self.create_data()

        resp = self.http_get(
            self.f_object_list_url.format(1, 'core', 'user')
            + '?ctnr=' + self.ctnr.name
        )
        user_data = json.loads(resp.content)['results']

        matches = filter(
            lambda user: user['user']['username'] == self.user.username,
            user_data)
        self.assertEqual(len(matches), 1, 'Could not filter users by ctnr.')

    def test_domain_filter(self):
        self.create_data()

        resp = self.http_get(
            self.f_object_list_url.format(1, 'dns', 'domain') +
            '?ctnr=' + self.ctnr.name)
        domain_data = json.loads(resp.content)['results']

        matches = filter(
            lambda domain: domain['name'] == self.ctnr_domain.name,
            domain_data)
        self.assertEqual(len(matches), 1, 'Could not filter domains by ctnr.')

    def test_range_filter(self):
        self.create_data()

        resp = self.http_get(
            self.f_object_list_url.format(1, 'dhcp', 'range') +
            '?ctnr=' + self.ctnr.name)
        range_data = json.loads(resp.content)['results']

        matches = filter(
            lambda range: (range['start_str'] == self.range.start_str and
                           range['end_str'] == self.range.end_str),
            range_data)
        self.assertEqual(len(matches), 1, 'Could not filter ranges by ctnr.')

    def test_workgroup_filter(self):
        self.create_data()

        resp = self.http_get(
            self.f_object_list_url.format(1, 'dhcp', 'workgroup') +
            '?ctnr=' + self.ctnr.name)
        workgroup_data = json.loads(resp.content)['results']

        matches = filter(
            lambda workgroup: workgroup['name'] == self.workgroup.name,
            workgroup_data)
        self.assertEqual(len(matches), 1, 'Could not filter networks by ctnr.')
