from copy import deepcopy

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import Http404
from django.db.models import Q, F

from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.mx.models import MX
from cyder.cydns.srv.models import SRV
from cyder.cydns.txt.models import TXT
from cyder.cydns.sshfp.models import SSHFP
from cyder.cydns.view.models import View


def slim_form(domain_pk=None, form=None):
    """ What is going on? We want only one domain showing up in the
    choices.  We are replacing the query set with just one object. Ther
    are two querysets. I'm not really sure what the first one does, but
    I know the second one (the widget) removes the choices. The third
    line removes the default u'--------' choice from the drop down.  """
    if not form:
        raise Http404
    if domain_pk:
        query_set = Domain.objects.filter(id=domain_pk)
        if not query_set:
            raise Http404
        if not form.fields.get('domain', False):
            raise Http404
        form.fields['domain']._queryset = query_set
        form.fields['domain'].widget.choices.queryset = query_set
        form.fields['domain'].empty_label = None
    return form


def get_clobbered(domain_name):
    classes = [MX, AddressRecord, CNAME, TXT, SRV, StaticInterface, SSHFP]
    clobber_objects = []  # Objects that have the same name as a domain
    for Klass in classes:
        objs = Klass.objects.filter(fqdn=domain_name)
        for obj in objs:
            obj_views = [view.name for view in obj.views.all()]
            new_obj = deepcopy(obj)
            new_obj.id = None
            new_obj.label = ""
            clobber_objects.append((new_obj, obj_views))
            if Klass == AddressRecord:
                kwargs = {"check_cname": False, "call_prune_tree": False}
            else:
                kwargs = {"call_prune_tree": False}
            # We have to be careful here to not delete any domains due to them
            # being pruneable and not having any records or child domains. We
            # set the call_prune_tree flag to tell the object's delete function
            # to skip calling prune_tree
            obj.delete(**kwargs)
    return clobber_objects


def ensure_domain(name, purgeable=False, inherit_soa=False, force=False):
    """
    This function will take ``domain_name`` and make sure that that domain
    with that name exists in the db. If this function creates a domain it will
    set the domain's purgeable flag to the value of the named arguement
    ``purgeable``. See the doc page about Labels and Domains for more
    information about this function
    """
    try:
        domain = Domain.objects.get(name=name)
        return domain
    except ObjectDoesNotExist:
        pass

    # Looks like we are creating some domains. Make sure the first domain we
    # create is under a domain that has a non-None SOA reference.
    parts = list(reversed(name.split('.')))

    if not force:
        domain_name = ''
        leaf_domain = None
        # Find the leaf domain.
        for i in range(len(parts)):
            domain_name = parts[i] + '.' + domain_name
            domain_name = domain_name.strip('.')
            try:
                tmp_domain = Domain.objects.get(name=domain_name)
                # It got here so we know we found a domain.
                leaf_domain = tmp_domain
            except ObjectDoesNotExist:
                continue

        if not leaf_domain:
            raise ValidationError(
                    "Creating this record would cause the creation of a new "
                    "TLD. Please contact http://www.icann.org/ for more "
                    "information.")
        if leaf_domain.delegated:
            raise ValidationError(
                "Creating this record would cause the creation of a domain "
                "that would be a child of a delegated domain.")
        if not leaf_domain.soa:
            raise ValidationError(
                "Creating this record would cause the creation of a domain "
                "that would not be in an existing DNS zone.")

    domain_name = ''
    for i in range(len(parts)):
        domain_name = parts[i] + '.' + domain_name
        domain_name = domain_name.strip('.')
        clobber_objects = get_clobbered(domain_name)
        # Need to be deleted and then recreated.
        domain, created = Domain.objects.get_or_create(name=domain_name)
        if purgeable and created:
            domain.purgeable = True
            domain.save()

        if (inherit_soa and created and domain.master_domain and
                domain.master_domain.soa is not None):
            domain.soa = domain.master_domain.soa
            domain.save()
        for object_, views in clobber_objects:
            try:
                object_.domain = domain
                object_.clean()
                object_.save()
                for view_name in views:
                    view = View.objects.get(name=view_name)
                    object_.views.add(view)
                    object_.save()
            except ValidationError:
                # this is bad
                import pdb
                pdb.set_trace()
                raise
    return domain


def ensure_label_domain(fqdn, force=False):
    """Returns a label and domain object."""
    if fqdn == '':
        raise ValidationError("FQDN cannot be the emptry string.")
    try:
        domain = Domain.objects.get(name=fqdn)
        if not domain.soa and not force:
            raise ValidationError("You must create a record inside an "
                                  "existing zones.")
        return '', domain
    except ObjectDoesNotExist:
        pass
    fqdn_partition = fqdn.split('.')
    if len(fqdn_partition) == 1:
        raise ValidationError("Creating this record would force the creation "
                              "of a new TLD '{0}'!".format(fqdn))
    else:
        label, domain_name = fqdn_partition[0], '.'.join(fqdn_partition[1:])
        domain = ensure_domain(domain_name, purgeable=True, inherit_soa=True)
        if not domain.soa and not force:
            raise ValidationError("You must create a record inside an "
                                  "existing zones.")
        return label, domain


def prune_tree(domain):
    return prune_tree_helper(domain, [])


def prune_tree_helper(domain, deleted_domains):
    if not domain:
        return deleted_domains  # Didn't delete anything.
    if domain.domain_set.all():
        return deleted_domains  # Can't delete domain. Has children.
    if domain.has_record_set():
        return deleted_domains  # Records exist for domain.
    elif not domain.purgeable:
        # This domain should not be deleted by a computer.
        return deleted_domains
    else:
        master_domain = domain.master_domain
        if not master_domain:
            return deleted_domains
        purged_domain = deepcopy(domain)
        purged_domain.id = None
        deleted_domains.append(purged_domain)
        domain.delete()
        return prune_tree_helper(master_domain, deleted_domains)


def get_zones():
    """This function returns a list of domains that are at the root of their
    respective zones."""
    return Domain.objects.filter(~Q(master_domain__soa=F('soa')),
                            soa__isnull=False)
