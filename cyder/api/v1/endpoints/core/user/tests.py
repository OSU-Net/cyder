from django.contrib.auth.models import User
from cyder.api.v1.tests.base import APITests


class UserAPI_Test(APITests):
    __test__ = True
    model = User
    url = "core/user"

    def create_data(self):
        return User.objects.get(username="test_user")
