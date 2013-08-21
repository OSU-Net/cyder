import cyder as cy
from cyder.core.ctnr.models import CtnrUser


def has_perm(self, request, action, obj=None, obj_class=None):
    return _has_perm(request.user, request.session['ctnr'], action, obj,
                     obj_class)


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
    :param action: ``view``, ``create, ``update``, ``delete``
    :type action: :class: `string`

    An example of checking whether a user has 'create' permission on a
        :class:`Domain` object.
        >>> perm = request.user.get_profile().has_perm(request, \'create\',
        ... obj_class=Domain)
        >>> perm = request.user.get_profile().has_perm(request, \'update\',
        ... obj=domain)
    """
    user_level = None

    # Get user level.
    try:
        ctnr_level = CtnrUser.objects.get(ctnr=ctnr, user=user).level
        is_ctnr_admin = ctnr_level == cy.LEVEL_ADMIN
        is_ctnr_user = ctnr_level == cy.LEVEL_USER
        is_ctnr_guest = ctnr_level == cy.LEVEL_GUEST
    except CtnrUser.DoesNotExist:
        is_ctnr_admin = False
        is_ctnr_user = False
        is_ctnr_guest = False
    try:
        cyder_level = CtnrUser.objects.get(ctnr=1, user=user).level
        is_cyder_admin = cyder_level == cy.LEVEL_ADMIN
        is_cyder_user = cyder_level == cy.LEVEL_USER
        is_cyder_guest = cyder_level == cy.LEVEL_GUEST
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
        obj_type = obj_class.__name__
    else:
        return False

    if obj_type and 'KeyValue' in obj_type:
        obj_type = obj_type.split('KeyValue')[0]

    handling_function = {
        # Administrative.
        'Ctnr': has_administrative_perm,
        'User': has_administrative_perm,
        'CtnrUser': has_ctnruser_perm,

        'SOA': has_soa_perm,

        # Top-level ctnr objects.
        'Domain': has_domain_perm,

        # Domain records.
        'AddressRecord': has_domain_record_perm,
        'CNAME': has_domain_record_perm,
        'MX': has_domain_record_perm,
        'Nameserver': has_domain_record_perm,
        'SRV': has_domain_record_perm,
        'SSHFP': has_domain_record_perm,
        'TXT': has_domain_record_perm,

        # Reverse domain records.
        'PTR': has_reverse_domain_record_perm,
        'ReverseNameserver': has_reverse_domain_record_perm,

        # DHCP.
        'Network': has_generic_dhcp_perm,
        'Range': has_range_perm,
        'Site': has_generic_dhcp_perm,
        'System': has_system_perm,
        'Vlan': has_generic_dhcp_perm,
        'Vrf': has_generic_dhcp_perm,
        'Workgroup': has_workgroup_perm,

        # Options.
        'SubnetOption': has_generic_dhcp_perm,
        'ClassOption': has_generic_dhcp_perm,
        'PoolOption': has_generic_dhcp_perm,
        'GroupOption': has_generic_dhcp_perm,

        'StaticInterface': has_static_registration_perm,
        'DynamicInterface': has_dynamic_registration_perm,
    }.get(obj_type, False)
    return handling_function(user_level, obj, ctnr, action)


def has_administrative_perm(user_level, obj, ctnr, action):
    """Permissions for ctnrs or users. Not related to DNS or DHCP objects."""
    return {
        'cyder_admin': action in [cy.ACTION_VIEW, cy.ACTION_UPDATE],
        'admin': action in [cy.ACTION_VIEW, cy.ACTION_UPDATE],
        'user': action in [cy.ACTION_VIEW],
        'guest': action in [cy.ACTION_VIEW],
    }.get(user_level, False)


def has_ctnruser_perm(user_level, obj, ctnr, action):
    """Permissions for ctnrs or users. Not related to DNS or DHCP objects."""
    return {
        'cyder_admin': action in [cy.ACTION_VIEW, cy.ACTION_UPDATE],
        'ctnr_admin': action in [cy.ACTION_VIEW, cy.ACTION_UPDATE],
        'admin': action in [cy.ACTION_VIEW, cy.ACTION_UPDATE],
        'user': action in [cy.ACTION_VIEW],
        'guest': action in [cy.ACTION_VIEW],
    }.get(user_level, False)


def has_soa_perm(user_level, obj, ctnr, action):
    """
    Permissions for SOAs.
    SOAs are global, related to domains and reverse domains.
    """
    return {
        'cyder_admin': True,  # ?
        'ctnr_admin': action in [cy.ACTION_VIEW],
        'user': action in [cy.ACTION_VIEW],
        'guest': action in [cy.ACTION_VIEW],
    }.get(user_level, False)


def has_domain_perm(user_level, obj, ctnr, action):
    """Permissions for domains. Ctnrs have domains."""
    # TODO: can have create permissions for subdomains.
    if obj and not obj in ctnr.domains.all():
        return False

    return {
        'cyder_admin': action in [cy.ACTION_VIEW, cy.ACTION_UPDATE],  # ?
        'ctnr_admin': action in [cy.ACTION_VIEW, cy.ACTION_UPDATE],
        'user': action in [cy.ACTION_VIEW, cy.ACTION_UPDATE],
        'guest': action in [cy.ACTION_VIEW],
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
        'guest': action in [cy.ACTION_VIEW],
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
        'ctnr_admin': True,
        'user': True,
        'guest': action in [cy.ACTION_VIEW],
    }.get(user_level, False)


def has_subnet_perm(user_level, obj, ctnr, action):
    """Permissions for subnet. Ranges have subnets."""
    if obj and not obj in [ip_range.subnet for ip_range in ctnr.ranges.all()]:
        return False

    return {
        'cyder_admin': True,  # ?
        'ctnr_admin': action in [cy.ACTION_VIEW],
        'user': action in [cy.ACTION_VIEW],
        'guest': action in [cy.ACTION_VIEW],
    }.get(user_level, False)


def has_range_perm(user_level, obj, ctnr, action):
    """Permissions for ranges. Ctnrs have ranges."""
    if obj and not obj in ctnr.ranges.all():
        return False

    return {
        'cyder_admin': True,  # ?
        'ctnr_admin': action in [cy.ACTION_VIEW],
        'user': action in [cy.ACTION_VIEW],
        'guest': action in [cy.ACTION_VIEW],
    }.get(user_level, False)


def has_workgroup_perm(user_level, obj, ctnr, action):
    """Permissions for groups. Groups are assigned a subnet."""
    # if obj and not obj.network in [ip_range.network for ip_range in
    #                                ctnr.ranges.all()]:
    #    return False

    return {
        'cyder_admin': True,  # ?
        'ctnr_admin': action in [cy.ACTION_VIEW],  # ?
        'user': action in [cy.ACTION_VIEW],  # ?
        'guest': action in [cy.ACTION_VIEW],
    }.get(user_level, False)


def has_system_perm(user_level, obj, ctnr, action):
    """Permissions for systems. Systems are assigned a ctnr."""
    # if obj and obj.ctnr != ctnr:
    #    return False

    return {
        'cyder_admin': True,
        'ctnr_admin': True,
        'user': True,
        'guest': action in [cy.ACTION_VIEW],
    }.get(user_level, False)


def has_generic_dhcp_perm(user_level, obj, ctnr, action):
    """
    Generic DHCP perm where users can do anything and guests can only view.
    """
    return {
        'cyder_admin': True,
        'ctnr_admin': True,
        'user': True,
        'guest': action in [cy.ACTION_VIEW],
    }.get(user_level, False)


def has_static_registration_perm(user_level, obj, ctnr, action):
    """Permissions for static registrations."""
    return {
        'cyder_admin': True,  # ?
        'ctnr_admin': True,  # ?
        'user': True,  # ?
        'guest': action in [cy.ACTION_VIEW],
    }.get(user_level, False)


def has_dynamic_registration_perm(user_level, obj, ctnr, action):
    """Permissions for static registrations."""
    return True
