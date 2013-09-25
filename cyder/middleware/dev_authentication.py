from django.shortcuts import redirect

from cyder.core.cyuser.views import login_session
from cyder.core.cyuser.models import User


class DevAuthenticationMiddleware(object):

    def process_request(self, request):
        # Log in as development user.
        if (not request.user.is_authenticated()
                or 'ctnr' not in request.session):
            user = 'test_superuser'
            if '_auth_user_id' in request.session:
                try:
                    user = User.objects.get(
                        pk=request.session['_auth_user_id'])
                except User.DoesNotExist:
                    pass
            request = login_session(request, user)

        if request.path == '/logout/':
            request.session.flush()
            return redirect('/')
