.. _domain:

Domain
======

.. |project| replace:: mozinv

Domains and Reverse Domains are at the core of the DNS app.

Domains
+++++++

Every domain has a name (like ``foo.example.com``). Every domain with a name comprised of two or
more labels has a master domain. From the child's prespective, it's master domain's name is always
it's own name with the far left label removed.  For example the domain ``foo.example.com`` has a
master domain ``example.com``.

A ``domain`` with fewer than two labels is permitted to have a master domain of ``None``. In all
other cases a domain *must* have a master domain. |project|'s django models enforce this.

The ``domain`` table stores all domain objects::

    +------------------+--------------+------+-----+---------+----------------+
    | Field            | Type         | Null | Key | Default | Extra          |
    +------------------+--------------+------+-----+---------+----------------+
    | id               | int(11)      | NO   | PRI | NULL    | auto_increment |
    | name             | varchar(100) | NO   | UNI | NULL    |                |
    | master_domain_id | int(11)      | YES  | MUL | NULL    |                |
    | soa_id           | int(11)      | YES  | MUL | NULL    |                |
    +------------------+--------------+------+-----+---------+----------------+

Note that ``master_domain_id`` is a foreign key that points back to the ``domain`` table. The
``soa_id`` field is a foreign key to the ``soa`` table.

Consider ``foo.example.com`` and ``bar.example.com``. The domain tree would look like the following::

    com
    |
    example
    |      \
    foo    bar

The ``domain`` table in the database would have these entries::

    id  name                master_domain   SOA

    1   com                 None            None
    2   example.com         1               1 <--- the SOA table is not shown here
    3   foo.example.com     2               1
    4   bar.example.com     2               1

Note that the ``com`` domain is in the table even though we are not authoritative for that domain.

You are not be able to add ``foo.example.com`` without first adding ``example.com``. |project|
enforces that a full domain tree be maintained at all times.

If you agree with the idea of keeping a full domain tree, skip to _`Reverse Domains`. Else, keep reading.

Advantages of a Full Domain Tree
++++++++++++++++++++++++++++++++
Having a full tree makes things more complete. When adding a new domain, having a full tree removes any ambiguity when searching for a master domain.

Here are two examples of adding a domain. The first examples uses a partial domain tree. The second example uses a complete tree.

Using an Incomplete Tree
````````````````````````
Say we want to add ``cute.cat.com`` and assume we are *not* keeping a complete tree in the DB and that ``cute.cat.com`` is the first domain being added to the database (the ``domain`` table is empty). With an incomplete tree, ``cute.cat.com`` would have the master domain of ``None``. We are authoritative for ``cure.cat.com`` so we have an :ref:`soa` for that domain::

    id  name                    master_domain   SOA

    1   cute.cat.com            None            1 <--- the SOA table is not show here

Let's now assume we are going to add ``cat.com``. At this point *if* we were using a full tree the ``com`` domain would be ``cute.com``'s master domain. But with the partial tree, the ``com`` domain is missing so ``cute.com``'s master domain is ``None``::

    id  name                    master_domain   SOA

    1   cute.cat.com            None            1
    2   cat.com                 None            1

After we add ``cat.com``, ``cute.cat.com``'s master domain is not correct. We need to search the
domain table to change ``cute.cat.com``'s master_domain to ``cat.com``'s ``id``, which is ``2``::

    id  name                    master_domain   SOA

    1   cute.cat.com            2               1
    2   cat.com                 None            1

Even when we didn't explicitly keep a complete tree, our data was converging towards completeness.
If we had added ``com`` we would have needed to update master domains and would be left with a full
tree.

Using a Full Tree Example
`````````````````````````
If we had to create all domains before we add a domain, adding the ``cute.cat.com`` domain would have resulted with the following records in the ``domain`` table::

    id  name                    master_domain   SOA

    1   com                     None            None
    2   cat.com                 1               None
    3   cute.cat.com            2               1

When we now add ``cat.com``, all we need to do is change the SOA field to signal that we are
authoritative for the domain::

    id  name                    master_domain   SOA

    1   com                     None            None
    2   cat.com                 1               1
    3   cute.cat.com            2               1

Reverse Domains
+++++++++++++++

Reverse Domains are stored in the same table as Forward Domains.

Reverse Domains have the same domain/master domain relationship as Forward Domains. Consider
the reverse domain ``0.168.192.in-addr.arpa``::

    arpa
    |
    in-addr
    |
    192
    |
    168
    |
    0

If we added the reverse domain ``1.168.192.in-addr.arpa``, the tree would look like this::

    arpa
    |
    in-addr
    |
    192
    |
    168
    |  \
    0   1

The ``domain`` table would have the records::

    id  name            master_domain      SOA

    1   arpa            None               None
    2   in-addr.arpa    1                  None
    3   192             2                  None
    4   192.168         3                  1 <--- the SOA table is not shown here
    5   192.168.0       4                  1
    6   192.168.1       4                  1

Reverse Domains that you are not authoritative for should not have a
relationship back to an SOA.

Reason For Reverse Domains
``````````````````````````
Reverse domains are used for DNS reverse mapping. In |project|, every IP that ends up in a reverse
zone file is mapped to an appropriate reverse domain. See the :ref:`ptr` documentation for more on
Reverse Domains.

Adding Reverse Domains
``````````````````````
Adding IPv4 reverse domains is easy to do by hand. It is not easy to do add IPv6 reverse domains by
hand. IPv6 reverse domain names are very long and it is tedious to add them one by one. There is a
function, :func:`bootstap_ipv6_reverse_domain`, that can aid in the construction of IPv6 reverse domains.


DNS Records
+++++++++++
Most DNS records in |project| have similar structure. In general, a record (like TXT, A, AAAA, etc.)
consists of a label, domain, and some data. A *record's* label can be thought as a leaf node on the
DNS tree, while the label's that compose domain names can be leaf node's *or* core nodes in the
tree.

.. figure:: images/label_domain1.png

The full name of any node is the sequence of labels from a node to the root of the DNS tree with dot's separating each label.

Records that 'hang off' and are attached to domains.

.. figure:: images/label_domain2.png

In the figure above, the domain ``example.com`` is shown with record sets hanging off.

*Every DNS record (except :ref:`soa`) in |project| has a Foriegn Key back to a domain.*

Domain Level Records
````````````````````
Sometimes the name of a DNS record has to be the same as the name of a domain. To have a DNS record
like this, set the record's label to the empty string '' and it's domain to the domain with a name
that is equal to desired name for the record.

Example: Assume we have two domains::

    example.com
    foo.example.com

Also, assume we are authoritative for both domains.

The ``domain`` table would have the following data::

    id  name                    master_domain   SOA
    1   com                     None            None
    2   example.com             1               1
    3   foo.example.com         2               1

With this configuration an A record like ``foo.example.com   A  192.168.0.3`` would have a label
equal to the empty string '', and it's domain set to ``foo.example.com``::

    (A Record table)
    id  name    domain   ip
    1   ''      3        192.168.0.3

The entry shown above is the correct way::

    (A Record table)
    id  name    domain   ip
    1   foo     2        192.168.0.3

The entry shown above is the wrong way and is not allowed.

This policy applies to all DNS records that have the label and domain fields.

.. note::

    The DNS build scripts are smart enough not to emit '.foo.example.com' as the A record's name.

Changing from Record to Domain
``````````````````````````````

When an existing DNS record has a name that needs to become a domain's name (for example
``bar.example.com`` is an A record, but then it is decided that the domain ``bar.example.com``
should be made) the consistent thing to do would be to shuffle any records that have the name
'bar.example.com'. An admin will have to delete the DNS records that conflict with the new domain's
name, make the new domain, and then create a `Domain Level Record` for the records that were
deleted.

.. note::
    Eventually, it might be nice to have a feature in the UI that does the record shuffling
    automatically.

SOA Records, Domains, and Zones
```````````````````````````````
An ``SOA`` record can only exist in one zone. It is critical that no two domains point to the same ``SOA`` record *and* be in different zones.

.. note::

    The rest of this page is not important if you are just here for the TL;DR

Domain Delegation
-----------------

.. warning::

    *This feature is incomplete*

Records in a delegated domain abide by different rules than records in a non delegated domain.

 * The name of an A record in a delegated domain must be the same as the server attribute of the :ref:`nameserver` that is serving the delegated domain.

 * Only A and NS records can be created in a delegated domain.

Because a `Nameserver` cannot exist without a glue record (if the glue
record is whithin the `Nameserver`\s domain) and an `AddressRecord` cannot
exist in a delegated domain without a `Nameserver` pointing too it, a special
form will need to be used to create `Nameserver`/`AddressRecord` pairs.
Underneath the hood, the form will:

    1. Undelegate the domain.
    2. Create the `AddressRecord`
    3. Create the `Nameserver`
    4. Re-delegate the domain.


The UI should *only* have a link to the create address record form and to the
form that creates an NS record and an A record in one submit.

When an admin creates a domain, the UI should prompt to configure it
as one of three types:

    * Subdomain - :ref:`soa` exists at a higher level; e.g. you are creating
      ``foo.example.com`` as a subdomain of ``example.com``, and ``example.com`` already exists
      with an SOA. This should be the default behavior.

    * Top-level domain, not delegated - "top-level" as in "at the top of a
      new zone" - UI should require you to create an :ref:`soa` and :ref:`nameserver` records.

    * Top-level domain, delegated - UI should require :ref:`nameserver` records (and glue)
      but not require nor allow an :ref:`soa`. Also, the restrictions above should be
      followed.

Domain
======

.. automodule:: mozdns.domain.models
    :inherited-members: Domain, boot_strap_ipv6_reverse_domain
