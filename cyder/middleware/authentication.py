from django.shortcuts import redirect


class AuthenticationMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated() or request.path in (u'/login/', u'/logout/'):
            pass
        else:
            return redirect('/login/')

        if not 'ctnr' in request.session:
            # Set session ctnr on login to user's default ctnr.
            default_ctnr = request.user.get_profile().default_ctnr
            if not default_ctnr:
                request.session['ctnr'] = Ctnr.objects.get(id=1)
            else:
                request.session['ctnr'] = Ctnr.objects.get(id=default_ctnr.id)
