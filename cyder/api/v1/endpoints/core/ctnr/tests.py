import json
from django.contrib.auth.models import User

from cyder.api.v1.endpoints.core.tests import CoreAPITests
from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.cydhcp.range.models import Range
from cyder.cydhcp.workgroup.models import Workgroup
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.vlan.models import Vlan
from cyder.cydhcp.vrf.models import Vrf
from cyder.cydns.domain.models import Domain


class CtnrAPI_Test(CoreAPITests):
    model = Ctnr

    def __init__(self):
        super(CoreAPITests, self).__init__()
        user_data = {
            'username': 'testuser',
        }
        self.user = User.objects.get_or_create(**user_data)[0]

        domain_data = {
            'name': 'www.' + self.domain.name,
            'master_domain': self.domain,
            'soa': self.domain.soa,
            'is_reverse': False,
            'dirty': False,
            'purgeable': False,
            'delegated': True,
        }
        self.ctnr_domain = Domain.objects.get_or_create(**domain_data)[0]

        range_network_site = Site.objects.get_or_create(name='site')[0]
        range_network_vlan = Vlan.objects.get_or_create(
            name='vlan', number=420)[0]
        range_network_vrf = Vrf.objects.get_or_create(name='vrf')[0]

        range_network_data = {
            'site': range_network_site,
            'vlan': range_network_vlan,
            'vrf': range_network_vrf,
            'ip_type': '4',
            'network_str': '10.1.0.0/8',
        }
        range_network = Network.objects.get_or_create(
            **range_network_data)[0]

        range_data = {
            'network': range_network,
            'ip_type': '4',
            'start_str': '10.1.0.0',
            'end_str': '10.1.0.255',
        }
        self.range = Range.objects.get_or_create(**range_data)[0]

        self.workgroup = Workgroup.objects.get_or_create(name='workgroup')[0]

    def create_data(self):
        self.ctnr = self.model.objects.get_or_create(name='ctnr')[0]
        self.ctnruser = CtnrUser.objects.get_or_create(
            user=self.user, ctnr=self.ctnr, level=2)[0]
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
        for u in user_data:
            if u['user']['username'] == self.user.username:
                break
        else:
            assert 1 == 0, "Could not filter users by ctnr."

    def test_domain_filter(self):
        self.create_data()

        resp = self.http_get(
            self.f_object_list_url.format(1, 'dns', 'domain')
            + '?ctnr='
            + self.ctnr.name
        )
        domain_data = json.loads(resp.content)['results']

        for d in domain_data:
            if d['name'] == self.ctnr_domain.name:
                break
        else:
            assert 1 == 0, "Could not filter domains by ctnr."

    def test_range_filter(self):
        self.create_data()

        resp = self.http_get(
            self.f_object_list_url.format(1, 'dhcp', 'range')
            + '?ctnr='
            + self.ctnr.name
        )
        range_data = json.loads(resp.content)['results']

        for r in range_data:
            if (
                    r['start_str'] == self.range.start_str
                    and r['end_str'] == self.range.end_str):
                break
        else:
            assert 1 == 0, "Could not filter ranges by ctnr."

    def test_workgroup_filter(self):
        self.create_data()

        resp = self.http_get(
            self.f_object_list_url.format(1, 'dhcp', 'workgroup')
            + '?ctnr='
            + self.ctnr.name
        )
        workgroup_data = json.loads(resp.content)['results']

        for n in workgroup_data:
            if n['name'] == self.workgroup.name:
                break
        else:
            assert 1 == 0, "Could not filter networks by ctnr."
