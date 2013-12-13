from cyder.base.constants import (LEVEL_GUEST, LEVEL_USER, LEVEL_ADMIN,
                                  ACTION_VIEW, ACTION_UPDATE)


def has_perm(self, request, action, obj=None, obj_class=None, ctnr=None):
        return _has_perm(request.user, ctnr or request.session['ctnr'], action,
            obj, obj_class)


def _has_perm(user, ctnr, action, obj=None, obj_class=None):
    """
    Checks whether a user (``request.user``) has permission to act on a
    given object (``obj``) within the current session CTNR. Permissions will
    depend on whether the object is within the user's current CTNR and
    the user's permissions level within that CTNR. Plebs are people that don't
    have any permissions except for dynamic registrations.

    Guests of a CTNR have view access to all objects within the current CTNR.

    Users have full access to objects within the current CTNR, except
    for exceptional types of objects (domains, SOAs) and the CTNR itself.

    CTNR admins are like users except they can modify the CTNR itself
    and assign permissions to other users.

    Cyder admins are CTNR admins to every CTNR. Though the object has to
    be within the CURRENT CTNR for permissions to be granted, for purposes
    of encapsulation.

    Superusers (Uber-admins/Elders) have complete access to everything
    including the ability to create top-level domains, SOAs, and global DHCP
    objects.

    Plebs are not assigned to any CTNR.
    CTNR Guests have level 0 to a CTNR.
    CTNR Users have level 1 to a CTNR.
    CTNR Admins have level 2 to a CTNR.
    Cyder Admins have level 2 to the 'global' CTNR (``pk=1``).
    Superusers are Django superusers.

    :param request: A django request object.
    :type request: :class:`request`
    :param obj: The object being tested for permission.
    :type obj: :class:`object`
    :param action: ``0`` (view), ``1`` (create), ``2`` (update), ``3`` (delete)
    :type action: :class: `int`

    An example of checking whether a user has 'create' permission on a
        :class:`Domain` object.
        >>> perm = request.user.get_profile().has_perm(request, \'create\',
        ... obj_class=Domain)
        >>> perm = request.user.get_profile().has_perm(request, \'update\',
        ... obj=domain)
    """
    from cyder.core.ctnr.models import CtnrUser
    user_level = None

    # Get user level.
    try:
        ctnr_level = CtnrUser.objects.get(ctnr=ctnr, user=user).level
        is_ctnr_admin = ctnr_level == LEVEL_ADMIN
        is_ctnr_user = ctnr_level == LEVEL_USER
        is_ctnr_guest = ctnr_level == LEVEL_GUEST
    except CtnrUser.DoesNotExist:
        is_ctnr_admin = False
        is_ctnr_user = False
        is_ctnr_guest = False
    try:
        cyder_level = CtnrUser.objects.get(ctnr=1, user=user).level
        is_cyder_admin = cyder_level == LEVEL_ADMIN
        is_cyder_user = cyder_level == LEVEL_USER
        is_cyder_guest = cyder_level == LEVEL_GUEST
    except CtnrUser.DoesNotExist:
        is_cyder_admin = False
        is_cyder_user = False
        is_cyder_guest = False

    if user.is_superuser:
        return True
    elif is_cyder_admin:
        user_level = 'cyder_admin'
    elif is_ctnr_admin:
        user_level = 'ctnr_admin'
    elif is_cyder_user or is_ctnr_user:
        user_level = 'user'
    elif is_cyder_guest or is_ctnr_guest:
        user_level = 'guest'
    else:
        user_level = 'pleb'

    # Dispatch to appropriate permissions handler.
    if obj:
        obj_type = obj.__class__.__name__
    elif obj_class:
        if isinstance(obj_class, basestring):
            obj_type = str(obj_class)
        else:
            obj_type = obj_class.__name__
    else:
        return False

    if (obj_type and obj_type.endswith('AV')
            and obj_type != 'WorkgroupAV'):
        obj_type = obj_type[:-len('AV')]

    handling_functions = {
        # Administrative.
        'Ctnr': has_administrative_perm,
        'User': has_administrative_perm,
        'UserProfile': has_administrative_perm,
        'CtnrUser': has_ctnr_user_perm,
        'CtnrObject': has_ctnr_object_perm,

        'SOA': has_soa_perm,

        'Domain': has_domain_perm,

        # Domain records.
        'AddressRecord': has_domain_record_perm,
        'CNAME': has_domain_record_perm,
        'MX': has_domain_record_perm,
        'Nameserver': has_name_server_perm,
        'SRV': has_domain_record_perm,
        'SSHFP': has_domain_record_perm,
        'TXT': has_domain_record_perm,
        'PTR': has_reverse_domain_record_perm,

        # DHCP.
        'Network': has_network_perm,
        'Range': has_range_perm,
        'Site': has_site_perm,
        'System': has_system_perm,
        'Vlan': has_vlan_perm,
        'Vrf': has_vrf_perm,
        'Workgroup': has_workgroup_perm,
        'StaticInterface': has_static_registration_perm,
        'DynamicInterface': has_dynamic_registration_perm,

        'WorkgroupAV': has_workgroupav_perm,
    }

    handling_function = handling_functions.get(obj_type, None)

    if not handling_function:
        if '_' in obj_type:
            obj_type = obj_type.replace('_', '')
        if 'Intr' in obj_type:
            obj_type = obj_type.replace('Intr', 'interface')
        for key in handling_functions.keys():
            if obj_type.lower() == key.lower():
                handling_function = handling_functions[key]

    if handling_function:
        return handling_function(user_level, obj, ctnr, action)
    else:
        raise Exception('No handling function for {0}'.format(obj_type))


def has_administrative_perm(user_level, obj, ctnr, action):
    """Permissions for ctnrs or users. Not related to DNS or DHCP objects."""
    return {
        'cyder_admin': action in (ACTION_VIEW, ACTION_UPDATE),
        'admin': action in (ACTION_VIEW, ACTION_UPDATE),
        'user': action == ACTION_VIEW,
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_ctnr_object_perm(user_level, obj, ctnr, action):
    """Permissions for ctnr object relationships."""
    return {
        'cyder_admin': action in (ACTION_VIEW, ACTION_UPDATE),
        'ctnr_admin': action == ACTION_VIEW,
        'admin': action in (ACTION_VIEW, ACTION_UPDATE),
        'user': action == ACTION_VIEW,
        'guest': action == (ACTION_VIEW),
    }.get(user_level, False)


def has_ctnr_user_perm(user_level, obj, ctnr, action):
    """Permissions for ctnr users."""
    return {
        'cyder_admin': action in (ACTION_VIEW, ACTION_UPDATE),
        'ctnr_admin': action in (ACTION_VIEW, ACTION_UPDATE),
        'admin': action in (ACTION_VIEW, ACTION_UPDATE),
        'user': action == ACTION_VIEW,
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_soa_perm(user_level, obj, ctnr, action):
    """
    Permissions for SOAs.
    SOAs are global, related to domains and reverse domains.
    """
    return {
        'cyder_admin': True,  # ?
        'ctnr_admin': action == ACTION_VIEW,
        'user': action == ACTION_VIEW,
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_domain_perm(user_level, obj, ctnr, action):
    """Permissions for domains. Ctnrs have domains."""
    # TODO: can have create permissions for subdomains.
    if obj and not obj in ctnr.domains.all():
        return False

    return {
        'cyder_admin': action in (ACTION_VIEW, ACTION_UPDATE),  # ?
        'ctnr_admin': action == ACTION_VIEW,
        'user': action == ACTION_VIEW,
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_domain_record_perm(user_level, obj, ctnr, action):
    """
    Permissions for domain records (or objects linked to a domain).
    Domain records are assigned a domain.
    """
    if obj and obj.domain not in ctnr.domains.all():
        return False

    return {
        'cyder_admin': True,
        'ctnr_admin': True,
        'user': True,
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_name_server_perm(user_level, obj, ctnr, action):
    if obj and obj.domain not in ctnr.domains.all():
        return False

    return {
        'cyder_admin': True,
        'ctnr_admin': action == ACTION_VIEW,
        'user': action == ACTION_VIEW,
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_reverse_domain_record_perm(user_level, obj, ctnr, action):
    """
    Permissions for reverse domain records (or objects linked to a reverse
    domain). Reverse domain records are assigned a reverse domain.
    """
    if obj and obj.reverse_domain not in ctnr.domains.all():
        return False

    return {
        'cyder_admin': True,
        'ctnr_admin': action == ACTION_VIEW,
        'user': True,
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_subnet_perm(user_level, obj, ctnr, action):
    """Permissions for subnet. Ranges have subnets."""
    if obj and not obj in [ip_range.subnet for ip_range in ctnr.ranges.all()]:
        return False

    return {
        'cyder_admin': True,  # ?
        'ctnr_admin': action == ACTION_VIEW,
        'user': action == ACTION_VIEW,
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_range_perm(user_level, obj, ctnr, action):
    """Permissions for ranges. Ctnrs have ranges."""
    if obj and not obj in ctnr.ranges.all():
        return False
    return {
        'cyder_admin': True,  # ?
        'ctnr_admin': action == ACTION_VIEW,
        'user': action == ACTION_VIEW,
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_workgroup_perm(user_level, obj, ctnr, action):
    """Permissions for groups. Groups are assigned a subnet."""
    # if obj and not obj.network in [ip_range.network for ip_range in
    #                                ctnr.ranges.all()]:
    #    return False

    return {
        'cyder_admin': True,  # ?
        'ctnr_admin': action == ACTION_VIEW,  # ?
        'user': action == ACTION_VIEW,  # ?
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_workgroupav_perm(user_level, obj, ctnr, action):
    """Permissions for group options."""
    return {
        'cyder_admin': True,  # ?
        'ctnr_admin': True,  # ?
        'user': action == ACTION_VIEW,  # ?
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_system_perm(user_level, obj, ctnr, action):
    """Permissions for systems. Systems are assigned a ctnr."""
    # if obj and obj.ctnr != ctnr:
    #    return False

    return {
        'cyder_admin': True,
        'ctnr_admin': True,
        'user': True,
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_generic_dhcp_perm(user_level, obj, ctnr, action):
    """
    Generic DHCP perm where users can do anything and guests can only view.
    """
    return {
        'cyder_admin': True,
        'ctnr_admin': True,
        'user': True,
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_vrf_perm(user_level, obj, ctnr, action):
    return {
        'cyder_admin': True,
        'ctnr_admin': action == ACTION_VIEW,
        'user': action == ACTION_VIEW,
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_site_perm(user_level, obj, ctnr, action):
    return {
        'cyder_admin': True,
        'ctnr_admin': action == ACTION_VIEW,
        'user': action == ACTION_VIEW,
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_vlan_perm(user_level, obj, ctnr, action):
    return {
        'cyder_admin': True,
        'ctnr_admin': action == ACTION_VIEW,
        'user': action == ACTION_VIEW,
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_network_perm(user_level, obj, ctnr, action):
    return {
        'cyder_admin': True,
        'ctnr_admin': action == ACTION_VIEW,
        'user': action == ACTION_VIEW,
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_static_registration_perm(user_level, obj, ctnr, action):
    """Permissions for static registrations."""
    return {
        'cyder_admin': True,  # ?
        'ctnr_admin': True,  # ?
        'user': True,  # ?
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)


def has_dynamic_registration_perm(user_level, obj, ctnr, action):
    """Permissions for static registrations."""
    return {
        'cyder_admin': True,  # ?
        'ctnr_admin': True,  # ?
        'user': True,  # ?
        'guest': action == ACTION_VIEW,
    }.get(user_level, False)
