from django.shortcuts import redirect

from cyder.core.cyuser.views import login_session
from cyder.core.cyuser.models import User


class DevAuthenticationMiddleware(object):

    def process_request(self, request):
        # Log in as development user.
        if 'ctnr' not in request.session:
            if '_auth_user_id' in request.session:
                username = User.objects.get(pk=request.session['_auth_user_id'])
            else:
                username = 'test_superuser'
            request = login_session(request, username)

        if request.path == '/logout/':
            request.session.flush()
            return redirect('/')
