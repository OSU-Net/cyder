from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from cyder.core.ctnr.models import Ctnr
from cyder.core.cyuser.views import login_session


class AuthenticationMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated() and not request.user.is_anonymous():
            pass
        elif request.path in (reverse('login'), reverse('logout')):
            return
        else:
            return redirect(reverse('login'))

        if not 'ctnr' in request.session:
            request = login_session(request, request.user.username)
