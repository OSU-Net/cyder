from django.contrib.auth.models import User

from cyder.api.v1.endpoints.core.tests import CoreAPITests


class UserAPI_Test(CoreAPITests):
    model = User

    def create_data(self):
        return self.model.objects.get_or_create(username='test_user')[0]
