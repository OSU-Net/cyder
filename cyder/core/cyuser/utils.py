from django.contrib import messages

from cyder.base.constants import ACTIONS, LEVELS


def perm_soft(request, action, obj=None, obj_class=None):
    """No exception raised, just returns boolean"""
    if not request.user.get_profile().has_perm(request, action, obj=obj,
                                               obj_class=obj_class):
        return False
    return True


def perm(request, action, obj=None, obj_class=None):
    """Message raised."""
    name = ''
    if obj:
        name = obj.__class__.__name__
    elif obj_class:
        name = obj_class.__name__

    if not perm_soft(request, action, obj=obj, obj_class=obj_class):
        messages.error(request, "Not allowed to %s %s as %s on %s" % (
            ACTIONS[action].lower(), name, LEVELS[request.session['level']],
            request.session['ctnr']))
        return False
    return True
