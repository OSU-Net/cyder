.. _dns_views:
.. |project| replace:: cyder
.. |org| replace:: Oregon State

View
====

    The Internet Assigned Numbers Authority (IANA) has reserved the
    following three blocks of the IP address space for private internets

        10.0.0.0        -   10.255.255.255  (10/8 prefix)

        172.16.0.0      -   172.31.255.255  (172.16/12 prefix)

        192.168.0.0     -   192.168.255.255 (192.168/16 prefix)

    -- `RFC 1918 <http://www.ietf.org/rfc/rfc1918.txt>`_

    At the present time, AAAA and PTR records for locally assigned local IPv6
    addresses (fc00::/7) are not recommended to be installed in the global DNS.

    -- `RFC 4193 <http://tools.ietf.org/html/rfc4193>`_

|project| has built in support for classifying records into different views. By default |project|
supports two views ``public`` and ``private``. Records can be classified three different ways.

    1) public only

    2) private only

    3) public and private

When a record is in class 1, it is accessible from the internet, including |org|'s external facing
machines, but not accessible from inside of |org|'s internal network.

When a record is in class 2, it is accessible from within |org|'s private network but not accessible
from the internet which includes |org|'s external facing machines.

When a record is in class 3, it is accessible from within |org|'s private network and from the
internet; if you can ping the nameserver, you have access to the record and it's data.


Enforcing RFC 1918
------------------
It is important that data that is considered 'internal' not be allowed into any view with public
facing data. RFC 1918 says that certain ip's should not be allowed into public DNS space. |project|
enforces these restrictions.

If an :ref:`address_record`/:ref:`staticinterface` record points to an IP that is in a network
specified in RFC 1918, it is not allowed to be part of a public view.

If a :ref:`ptr` record points to an IP that is in a network specified in RFC 1918, it is not allowed
to be part of a public view.


.. note::
    This CNAME requirement is probably not going to be implemented right away. Since an A/PTR will
    return a NXDOMAIN in a view that they are not a part of there is not too much of an information
    leek if a CNAME resolves to a missing record.

If a :ref:`CNAME`, :ref:`SRV`, or :ref:`MX` has a canonical name that has the type :class:`A`,
:class:`PTR`, or :class:`StaticInterface` and has an IP within one of the networks specified in RFC
1918, it is not allowed to be part of a public view::

    foo CNAME bar                                   bar A 10.0.0.1

    ^                                               ^
    |                                               |
    +-- foo is tagged as a public CNAME             +-- bar is tagged as private only


All other records are allowed to be in any combination of views.

Split Horizon
-------------
Split Horizon records are when a name server returns different data for a record depending on whether
you are coming from the Internet or from the Intranet.

Here is an example of a split horizon record: assume a record has a name X. When X is queried from
the internet some data Y is returned by the name server. When X is queried from an internal network
some data Z is returned by the name server. If X != Y, then this is a split horizon record.

A common use case of split horizon records is when you want a host's name to resolve to a private
address when a query is coming from a trusted private network and a public address when the query is
coming from an untrusted public network. The split horizon record helps facilitate untrusted
public flows first going through some sort of firewall while directing queries from a trusted private
network to an internal non-firewalled ip address.

Usings Views
============

Every record that can exist in a zone file has an attribute ``views`` that can be used to manage
which views the record is in.::

    A = AddressRecord.objects.get(fqdn="somehost.example.com")
    cname = CNAME.objects.get(fqdn="www.somehost.example.com")
    ptr = PTR.objects.get(name="somehost.example.com")

Here we have retrieved a few objects from our hypothetical database. By default these objects are
not put into DNS views and will not be included in the zone file for that view.

.. note::
    If you want a record to be in the output of a zone file, you probably need to assign it to a
    view. Usually this is either the 'private' or 'public' view.

For the sake of example, let's create and then get a view from the hypothetical database::

    from mozdns.view.models import View
    private = View(name="private")
    private.save()

If the view already existed in the database we would do this::

    private = View.objects.get(name="private")

If we wanted to add some of our records to the ``private`` view, we would use the ``views`` attribute on an
object::

    A.views.add(private)
    A.save()

    cname.views.add(private)
    cname.save()

Objects can be in more than one view::

    public, _ = View.objects.get_or_create(name="public")

    A.views.add(public)
    A.save()

At this point the ``A`` record for ``somehost.example.com`` would be included in the public and
private views.

For more information see `Django Many to Many Fields <https://docs.djangoproject.com/en/dev/topics/db/examples/many_to_many/>`_.

.. note::
    The rest of this page is mostly notes.

DNS Views
---------
It is highly likely that some records should be viewable from one network and
not visable from another. To do this use bind DNS views.

The nameserver conf file::

    view "internal-view" {
      match-clients { 128.193.0.0/16; 10.0.0.0/8 };
      zone "foo.com" IN {
        type master;
        file "zones/db.foo.com.internal";
     };
    };

    view "external-view" {
      match-clients { any; };
      zone "foo.com" IN {
        type master;
        file "zones/db.foo.com.external";
      };
      ...
      ... (More zone statements)
      ...
    };

The zone files::

    FILE: db.foo.com.soa
    @   1D  IN  SOA ns1.foo.com hostmaster.foo.com (
                    1;
                    2;
                    3;
                    4;
                    5;
                )

    FILE: db.foo.com.data.external

    @       IN  NS  ns1.foo.com
    @       MX  10  mail.foo.com
    ns1     A   128.193.1.4
    mail    A   128.193.1.5

    FILE: db.foo.com.data.internal

    bob     A   10.0.0.2
    mary    A   10.0.0.3

The external zone file::

    FILE: db.foo.com.external

    $INCLUDE db.foo.com.soa
    $INCLUDE db.foo.com.external

The internal zone file::

    FILE: db.foo.com.internal

    $INCLUDE db.foo.com.soa
    $INCLUDE db.foo.com.data.external
    $INCLUDE db.foo.com.data.internal

Questions:

.. note::
    Views are being introduced later in the design of the DNS side of cyder.

`How will views be represented in the database?`

A new table called 'views' will be created. This table will have entries that
represent different views. Here is the planed scheme::

    +------------------+--------------+------+-----+---------+----------------+
    | Field            | Type         | Null | Key | Default | Extra          |
    +------------------+--------------+------+-----+---------+----------------+
    | id               | int(11)      | NO   | PRI | NULL    | auto_increment |
    | name             | varchar(100) | NO   | UNI | NULL    |                |
    | comment          | varchar(255) | NO   | UNI | NULL    |                |
    +------------------+--------------+------+-----+---------+----------------+

`Who/How will you create/delete a View?`

Only super admins should be able to create/delete views. To create a view an
admin would add en entry to the view table. To a delete a view no objects can
reference that view.

`Changes to models.`

Models that belong to views will need to be tied to views in the database.
This should be done with a many-to-many table between views and records::

    +-----+--------+     +-----+------+     +----+-------------+
    | id  | Record |     | Rec | View |     | id |   View      |
    +-----+--------+     +-----+------+     +----+-------------+
    | 1   |  A     |     |  1  |  1   |     | 1  | Public      |
    | 2   |  A     |     |  1  |  2   |     | 2  | Private     |
    | 3   |  A     |     |  1  |  3   |     | 3  | DataCenter  |
    | 4   |  A     |     |  2  |  1   |     +----+-------------+
    +-----+--------+     |  3  |  3   |
                         |  4  |  3   |
                         +-----+------+

Here four :class:`AddressRecord` objects are being used to show how records relate
to views. Instead of keeping which view a record belongs to in the table that
the record is defined, a second intermediate table is used to link the records
to a view. In this example there are three views: `Public`, `Private`, and
`DataCenter`. The first A record is in all three of the views. The second A
record is in just the `Public` view and the third and fourth A records are only
in the `DataCenter` View.

The above example illustrated how the :class:`AddressRecord` type would be
linked to a view. Because the intermediate table relies on an object's primary
key, two different objects types cannot share the same intermediate table. `Each
record type will need it's own intermediate table`.

`How does a record 'belong' to a certain View? Can a record 'belong' to
multiple views?`

A record will be in a view because it will have an entry in it's intermediate
table linking it to a particular view. A record can be in multiple views at the
same time by having multiple entries in it's intermediate table.


`How will views be used during the build process?`

Views add a new complexity to building DNS zone file.

DNS builds and views
--------------------
Forward zone files::

    for all SOAs
        get all the domains in that soa
        for each domain
            for each section
                generate a file contain all records in that domain and section

Reverse zone files::

    for all SOAs
        get all the reverse domains in that soa
        for each reverse domain
            for each view
                generate a file contain all records in that domain and view

Right now there are files for a zone's soa and domains. Views will introduce
more files (`(# domains - 1) *  # views` more files).

