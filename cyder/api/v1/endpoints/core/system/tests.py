import json

from cyder.api.v1.endpoints.core.tests import CoreAPITests
from cyder.core.system.models import System


class SystemAPI_Test(CoreAPITests):
    model = System

    def create_data(self):
        data = {
            'name': 'test_system',
        }
        obj, _ = self.model.objects.get_or_create(**data)
        return obj

    def test_keyvalues(self):
        obj = self.create_data()
        obj.systemkeyvalue_set.get_or_create(
            key='Test Key', value='Test Value')
        resp = self.http_get(self.object_url(obj.id))
        keyvalues = json.loads(resp.content)['systemkeyvalue_set'][0]
        assert keyvalues['key'] == 'Test Key'
        assert keyvalues['value'] == 'Test Value'
