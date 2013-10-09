from rest_framework.authentication import TokenAuthentication

from cyder.api.authtoken.models import Token


class CyderTokenAuthentication(TokenAuthentication):
    model = Token
