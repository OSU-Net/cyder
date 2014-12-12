from cyder.cydns.domain.models import Domain
from cyder.api.v1.tests.base import APITests

import json


class DomainAPI_Test(APITests):
    __test__ = True
    model = Domain

    def create_data(self):
        return Domain.objects.create(
            name='bing.' + self.domain.name, soa=self.domain.soa,
            is_reverse=False, dirty=False, purgeable=False, delegated=True)

    def test_1_related(self):
        """Test that Domain relations work and make sense."""
        # Get our test domain object.
        domain = self.create_data()
        resp = self.client.get(self.object_url(domain.id), **self.authheader)

        # Try to retrieve new master domain.
        data = json.loads(resp.content)
        master_resp = self.client.get(data['master_domain'], **self.authheader)

        # Check the response.
        self.assertHttpOK(master_resp)
        master_data = json.loads(master_resp.content)
        self.assertEqual(master_data['name'], self.domain.name)
