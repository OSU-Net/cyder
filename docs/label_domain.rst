.. _label_domain:

Label Domain Paradigm
=====================
This page only applied to forward domains.

.. |project| replace:: Cyder

All DNS records are centered around the 'label and domain' paradigm. This is a good unambiguous
underlying data structure for the system to understand but it quite unfriendly to the user.

An interesting case is this: say we only have two domains in our db, ``com`` and ``example.com``,
and we want to add the :ref:`address_record` ``foo.bar.x.y.z.example.com  A   192.168.3.3``. Four
new domains would need to be created to store this record:  ``z.example.com``, ``y.z.example.com``,
``x.y.z.example.com``, and ``bar.x.y.z.example.com``. The last domain would be the record's domain
and ``foo`` would be the value of it's label. Instead of having the user create all these domains,
just saying 'create an ``A`` record with the name ``foo.bar.x.y.z.example.com``' should be possible.

The algorithm for creating a new name::

    def ensure_label_domain(fqdn):
        """Returns a label and domain object."""
        if Domain.objects.filter(name=fqdn).exists():
            return '', Domain.objects.get(name=fqdn)
        fqdn_partition = fqdn.split('.')
        if len(fqdn_partition) == 1:
            domain = Domain(name=fqdn)
            domain.full_clean()
            domain.save()
            return '', domain
        else:
            label, domain_name = fqdn_partition[0], fqdn_partition[1:]
            domain = ensure_domain(domain_name, purgeable=True)

    def ensure_domain(domain_name, purgeable=False):
        """This function will take ``domain_name`` and make sure that that domain with that name
        exists in the db. If this function creates a domain it will set the domain's purgeable flag
        to the value of the named arguement ``purgeable``."""
        # Complicated code.

Deleting an object that caused four domains to be created should not clutter the domain table with
unused domains. *A domain is considered 'unused' when it's id, or pk (primary key), is not used in
any DNS record*. When a record is deleted the effect of the following function should be applied to the
record's domain after it is deleted::

    def prune_tree(domain):
        if domain.has_record_set():
            return False  # There are records for this domain
        elif not domain.purgeable:
            return False  # This domain should not be deleted by a computer.
        else:
            child_domains = domain.domain_set.all()
            domain.delete()
            for child_domain in child_domains:
                prune_tree(child_domain)
            return True

During the process of creating a new domain, a new domain's name could conflict with an existing
record's name.  For example, while creating the domain ``foo.example.com`` there may already be a
record with a label equal to ``foo`` and it's domain pointed at ``example.com``. To handle these
conflicts the function ``ensure_domain`` will delete conflicting records, create the new domain, and
then recreate the record in the newly created domain and set the record's label to ``''`` (the empty string).

Purgeable Domains
-----------------

The domain's ``purgeable`` attribute is set to ``True`` when it is created with the
``ensure_label_domain`` function. When a record is deleted, the ``prune_tree`` function may delete
unused domains. Some domains that are created should not be purged if they are empty, these domains
should have purgeable set to ``False``. Some example of domain types that should not be purged:

    * Any domain created in the Web UI should default to purgeable = False.
      - If a user has gone out of his way to fill out a form to create a domain, don't delete it.
    * All domains that are at the root of a SOA should default to purgeable = False.

Some examples of when a domain will be passed to the ``prune_tree`` function.

    * A record that has just been deleted will pass it's domain to ``prune_tree``.
    * When a record is saved the domain that the record had *before* the update will have
      ``prune_tree`` called on it (this doesn't happen when the record is first created).

.. note::
    When calling ``ensure_label_domain`` it is optimal to not allow domain leaks to happen. One way
    a domain leak can happen is if you call ``ensure_label_domain``, assign the returned domain to
    an object, and then back out of the creation of the object for some reason (likely an error
    during object validation). To prevent this kind of leak, you should call ``prune_tree`` on the
    domain returned by ``ensure_label_domain`` if the creation of an object fails.

Delegated Domains
-----------------
If a request is made to ``ensure_label_domain`` that would cause domains to be created under a
delegated domain, a :class:`ValidationError` is raised.

SOA Requirements
----------------
The first domain that ``ensure_label_domain`` creates must be under a domain that claims to be part
of zone (points to an SOA). This requirement is meant to ward off mass domain creation due to a
typo. For exmaple: when attempting to create ``bar.x.y.z.example.com`` a user could accidentally
write ``bar.x.y.z.example.cm`` and end up creating a stray root domain and five sub-domains.

If a request is made to ``ensure_label_domain`` that would cause the creation of a domain that isn't
in a zone, a :class:`ValidationError` is raised.
