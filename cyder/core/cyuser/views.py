import json

from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.db.models import Q
from django.conf import settings

from cyder.api.authtoken.models import Token
from cyder.base.utils import make_megafilter
from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.core.cyuser.models import UserProfile
from cyder.core.cyuser.forms import UserPermForm
from cyder import LEVEL_GUEST


def login_session(request, username):
    """Logs in a user and sets up the session."""
    try:
        # Authenticate / login.
        user = User.objects.get(username=username)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
    except User.DoesNotExist:
        if not settings.TESTING:
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
        if not CtnrUser.objects.filter(
                user=request.user, ctnr=new_default_ctnr).exists():
            CtnrUser(user=request.user, ctnr=new_default_ctnr, level=0).save()

    # Set session ctnr.
    default_ctnr = request.user.get_profile().default_ctnr
    if default_ctnr:
        request.session['ctnr'] = Ctnr.objects.get(id=default_ctnr.id)
    else:
        request.session['ctnr'] = Ctnr.objects.get(id=2)

    if request.session['ctnr'].name == "default":
        default_ctnr = Ctnr.objects.get(name="global")
        request.session['ctnr'] = default_ctnr

    # Set session ctnr level.
    try:
        level = CtnrUser.objects.get(user=request.user,
                                     ctnr=default_ctnr).level
    except CtnrUser.DoesNotExist:
        level = LEVEL_GUEST

    request.session['level'] = level

    try:
        CtnrUser.objects.get(user=request.user, ctnr=1)
        ctnrs = Ctnr.objects.order_by("name")

    except CtnrUser.DoesNotExist:
        # Set ctnr list (to switch between).
        ctnrs_user = CtnrUser.objects.filter(user=request.user)
        ctnrs = ctnrs_user.values_list('ctnr', flat=True)
        ctnrs = Ctnr.objects.filter(id__in=ctnrs).order_by('name')

    global_ctnr = Ctnr.objects.get(id=1)
    ctnrs = ctnrs.exclude(Q(id=2) | Q(id=1))
    ctnrs = [global_ctnr] + list(ctnrs)

    request.session['ctnrs'] = ctnrs

    return request


def clone_perms_check(request):
    if not request.POST:
        return redirect(request.META.get('HTTP_REFERER', ''))

    users = request.POST.get('users', None)
    new_users = []
    if users:
        users = users.split(',')
        for user in users:
            if not User.objects.filter(username=user).exists():
                new_users.append(user)

    confirm_str = ''
    if new_users:
        if len(new_users) > 1:
            confirm_str = 'Users: '
            for user in new_users:
                confirm_str += '{0}, '.format(user)

            confirm_str += ('do not exist. Would you like to create '
                            + 'these users?')
        else:
            confirm_str = ('User {0} does not exist. Would you like to '
                           + 'create this user?').format(user)

        return HttpResponse(json.dumps(
            {'confirm_str': confirm_str, 'users': new_users}))

    return HttpResponse(json.dumps({'success': True}))


def clone_perms(request, user_id):
    if not request.POST:
        return redirect(request.META.get('HTTP_REFERER', ''))
    acting_user = request.user.get_profile()
    if not acting_user.has_perm(request, 2, obj_class='User'):
        return HttpResponse(json.dumps(
            {'errors': {'__all__': 'You do not have permissions to perform '
                        + 'this action'}}))

    user = UserProfile.objects.get(id=user_id)
    perms_qs = CtnrUser.objects.filter(user__id=user_id)
    if not perms_qs.exists():
        perms_qs = []

    users = request.POST.get('users', None)
    if not users:
        return HttpResponse(json.dumps(
            {'errors': {'__all__': 'No users provided'}}))

    users = users.split(',')
    for user in users:
        user_qs = User.objects.filter(username=user)
        if not user_qs.exists():
            user = User(username=user)
            user.save()
        else:
            user = user_qs.get()
            CtnrUser.objects.filter(user=user).delete()

        for perm in perms_qs:
            ctnr_user_qs = CtnrUser.objects.filter(user=user, ctnr=perm.ctnr)
            if not ctnr_user_qs.exists():
                ctnr_user = CtnrUser(
                    user=user, ctnr=perm.ctnr, level=perm.level)
            else:
                ctnr_user = ctnr_user_qs.get()
                ctnr_user.level = perm.level

            ctnr_user.save()

    return HttpResponse(json.dumps({'success': True}))


def set_default_ctnr(request):
    if not request.POST:
        return redirect(request.META.get('HTTP_REFERER', ''))

    user = request.user.get_profile()
    user.default_ctnr = request.session['ctnr']
    user.save()

    return redirect(request.META.get('HTTP_REFERER', ''))


def delete(request, user_id):
    acting_user = User.objects.get(id=request.session['_auth_user_id'])

    if acting_user.is_superuser is False:
        messages.error(request, 'You do not have superuser permissions')
        return redirect(reverse('core-index'))

    if acting_user.id == user_id:
        messages.error(
            request, 'You cannot delete yourself')
        return redirect(request.META.get('HTTP_REFERER', ''))

    try:
        User.objects.get(id=user_id).delete()
    except:
        messages.error(request, 'That user does not exist')

    return redirect(request.META.get('HTTP_REFERER', ''))


def edit_user(request, username, action):
    acting_user = User.objects.get(id=request.session['_auth_user_id'])

    if acting_user.is_superuser is False:
        return HttpResponse(json.dumps(
            {'errors': {'__all__': 'You do not have superuser permissions'}}))

    if acting_user.username == username:
        return HttpResponse(json.dumps(
            {'errors': {'__all__': 'You do not have permission to perform ' +
                        'this action'}}))

    if action == 'Create':
        user, _ = User.objects.get_or_create(username=username)
        if _ is False:
            return HttpResponse(json.dumps(
                {'errors': {'__all__': 'A user with that username already ' +
                            'exists'}}))

        user.save()

    else:
        try:
            user = User.objects.get(username=username)
            if action == 'Promote':
                user.is_superuser = True
                user.save()

                try:
                    ctnruser = CtnrUser.objects.get(
                        user_id=user.id,
                        ctnr_id=Ctnr.objects.get(name='global').id)
                    ctnruser.level = 0
                    ctnruser.full_clean()
                    ctnruser.save()
                except CtnrUser.DoesNotExist:
                    ctnruser = CtnrUser(
                        user_id=user.id,
                        ctnr_id=Ctnr.objects.get(name='global').id,
                        level=0)
                    ctnruser.full_clean()
                    ctnruser.save()

            elif action == 'Demote':
                user.is_superuser = False
                user.save()

            elif action == 'Delete':
                ctnrs = CtnrUser.objects.filter(user_id=user.id)
                for ctnr in ctnrs:
                    ctnr.delete()
                user.delete()

            else:
                return HttpResponse(json.dumps(
                    {'errors': {'__all__': 'Unknown action'}}))
        except:
            return HttpResponse(json.dumps(
                {'errors': {'__all__': 'An error occurred'}}))

    return HttpResponse(json.dumps({'success': True}))


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

    # Don't do anything if not a superuser or becoming self.
    if not request.user.is_superuser or current_user == username:
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

    if not settings.TESTING:
        messages.error(request, "You are now logged in as %s" % username)
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


def user_detail(request, pk):
    from cyder.base.views import cy_detail

    user = UserProfile.objects.get(id=pk)
    email = User.objects.get(id=pk).email
    contacts = []
    form = UserPermForm()
    if email:
        contacts = (Ctnr.objects.filter(email_contact__contains=email))
    else:
        contacts = []

    ctnrs = CtnrUser.objects.filter(user_id=user)

    tables = {
        'Containers': ctnrs,
        'Contact For': contacts,
    }

    if request.user.id == user.id or request.user.is_superuser:
        tokens = Token.objects.filter(user=user)
        tables.update({'API Tokens': tokens})

    return cy_detail(request, UserProfile, 'cyuser/user_detail.html',
                     tables, obj=user, user_perm_form=form)
