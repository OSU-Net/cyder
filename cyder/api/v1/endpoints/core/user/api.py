from django.contrib.auth.models import User
from rest_framework import serializers

from cyder.api.v1.endpoints.core import api
from cyder.core.cyuser.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    default_ctnr = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-core-ctnr-detail')

    class Meta:
        model = UserProfile
        fields = ['user', 'default_ctnr', 'phone_number']


class UserProfileViewSet(api.CommonCoreViewSet):
    model = UserProfile
    serializer_class = UserProfileSerializer
