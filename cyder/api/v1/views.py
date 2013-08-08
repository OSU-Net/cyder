from django.contrib.auth.models import User, Group
from rest_framework import viewsets

from cyder.api.serializers import UserSerializer, CNAMESerializer
from cyder.cydns.cname.models import CNAME


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CNAMEViewSet(viewsets.ModelViewSet):
    queryset = CNAME.objects.all()
    serializer_class = CNAMESerializer


