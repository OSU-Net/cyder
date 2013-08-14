from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def home(request):
    # list the user's api keys
    pass

def request_key(request):
    # tell the user their responsibilities and confirm key generation
    pass

def revoke_key(request):
    # confirm key revocation, then remove it
    pass
