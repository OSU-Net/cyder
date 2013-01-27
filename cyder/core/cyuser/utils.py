from django.core.exceptions import PermissionDenied


def perm_soft(request, action, obj=None, obj_class=None):
    """No exception raised."""
    if not request.user.get_profile().has_perm(request, action, obj=obj,
                                               obj_class=obj_class):
        return False
    return True


def perm(request, action, obj=None, obj_class=None):
    """Exception raised."""
    if not perm_soft(request, action, obj=obj,
                     obj_class=obj_class):
        raise PermissionDenied
    return True
