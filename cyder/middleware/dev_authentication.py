from django.shortcuts import redirect

from cyder.core.cyuser.views import login_session


class DevAuthenticationMiddleware(object):

    def process_request(self, request):
        # Log in as development user.
        if request.user.is_anonymous():
            request = login_session(request, 'development')

        if request.path == '/logout/':
            request.session.flush()
            return redirect('/')

        return None
