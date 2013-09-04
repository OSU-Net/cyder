import json

from cyder.api.v1.endpoints.dns.tests import DNSAPITests
from cyder.cydns.domain.models import Domain


class DomainAPI_Test(DNSAPITests):
    model = Domain

    def create_data(self):
        data = {
            'name': 'bing.' + self.domain.name,
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
        """DomainAPI_Test.test_1_related(): Test that Domain relations work
        and make sense.
        """
        # get our test domain object
        domain = self.create_data()
        resp = self.client.get(self.object_url(domain.id), **self.authheader)

        # try to retrieve new master domain
        data = json.loads(resp.content)
        master_resp = self.client.get(data['master_domain'], **self.authheader)

        # check the response
        self.assertHttpOK(master_resp)
        master_data = json.loads(master_resp.content)
        assert master_data['name'] == self.domain.name

