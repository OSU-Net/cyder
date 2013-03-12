import json

from django.shortcuts import get_object_or_404,  render
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.db.models import Q

from cyder.base.utils import tablefy
from cyder.base.utils import make_megafilter
from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.core.cyuser.models import UserProfile


def login_session(request, username):
    """Logs in a user and sets up the session."""
    try:
        # Authenticate / login.
        user = User.objects.get(username=username)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
    except User.DoesNotExist:
        messages.error(request, "User %s does not exist" % (username))
        return request

    try:
        # Create user profile if needed.
        request.user.get_profile()
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=user)
        profile.save()

    try:
        # Assign user to default ctnr if needed.
        CtnrUser.objects.get(user=request.user,
                             ctnr_id=request.user.get_profile().default_ctnr)
    except CtnrUser.DoesNotExist:
        new_default_ctnr = Ctnr.objects.get(id=2)
        CtnrUser(user=request.user, ctnr=new_default_ctnr, level=0).save()

    # Set session ctnr.
    default_ctnr = request.user.get_profile().default_ctnr
    if default_ctnr:
        request.session['ctnr'] = Ctnr.objects.get(id=default_ctnr.id)
    else:
        request.session['ctnr'] = Ctnr.objects.get(id=2)

    # Set session ctnr level.
    request.session['level'] = CtnrUser.objects.get(user=request.user,
                                                    ctnr=default_ctnr).level

    try:
        # Set ctnr list (to switch between).
        global_ctnr = CtnrUser.objects.get(user=request.user, ctnr=1)
        if global_ctnr:
            request.session['ctnrs'] = (list(Ctnr.objects.filter(Q(id=1) \
            | Q(id=2))) + list(Ctnr.objects.exclude(Q(id=1) \
            | Q(id=2)).order_by("name")))

    except CtnrUser.DoesNotExist:
        # Set ctnr list (to switch between).
        ctnrs_user = CtnrUser.objects.filter(user=request.user)
        ctnrs = [Ctnr.objects.get(id=ctnr_pk) for ctnr_pk in
                 ctnrs_user.values_list('ctnr', flat=True)]
        request.session['ctnrs'] = ctnrs

    return request


def search(request):
    """Returns a list of users matching 'term'."""
    term = request.GET.get('term', '')
    if not term:
        raise Http404

    users = UserProfile.objects.filter(make_megafilter(UserProfile, term))[:15]
    users = [{'label': str(user), 'pk': user.user.pk} for user in users]
    return HttpResponse(json.dumps(users))


def become_user(request, username=None):
    """Become another user with their permissions, be able to change back."""
    referer = request.META.get('HTTP_REFERER', '/')
    current_user = request.user.username

    # Don't do anything if becoming self.
    if current_user == username:
        return redirect(referer)

    # Save stack since session will be overwritten.
    if 'become_user_stack' in request.session:
        become_user_stack = [user for user in
                             request.session['become_user_stack']]
        become_user_stack.append(current_user)
    else:
        become_user_stack = [current_user]

    request = login_session(request, username)

    # Restore user stack.
    if str(request.user) == username:
        request.session['become_user_stack'] = become_user_stack

    return redirect(referer)


def unbecome_user(request):
    """If user became another user, unbecome by popping become_user_stack."""
    referer = request.META.get('HTTP_REFERER', '/')

    if ('become_user_stack' in request.session and
        len(request.session['become_user_stack']) > 0):
        become_user_stack = [user for user in
                             request.session['become_user_stack']]
        username = become_user_stack.pop()
    else:
        become_user_stack = []
        username = request.user.username

    request = login_session(request, username)

    if len(become_user_stack) > 0:
        request.session['become_user_stack'] = become_user_stack

    return redirect(referer)


def cylogin(request):
    """Not implemented."""
    return redirect('/')


def cylogout(request):
    """Not implemented. """
    return redirect('/')


def UserDetailView(request, username):
    user = User.objects.get(id=username)
    users = [user]
    user_table = tablefy(users, users=True)
    return render(request, 'cyuser/user_detail.html',
                  {'user': user, 'user_table': user_table})
