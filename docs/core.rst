.. _core:

IPAM
====
A system that manages DNS and DHCP is useless without knowledge of the networks
the hosts using DNS and DHCP are located in. The core of inventory is it's
:class:`Site`\s, :class:`Network`\s, and :class:`Range`\s.

Sites
-----
A :ref:`site` represents a datacenter or a business unit. Much like
:ref:`domain`\s are organized into a hierarchy with 'master domains', a site
can have a 'parent site'.


.. figure:: images/mozcore_sites.png

Here four sites are shown. Scl3 is the parent site of Releng and Phx1 is the
Parent site of Svc. If Relenge were also in Scl2, there would be another
instance of a site called Relenge that had a parent site of Scl2.

Networks
--------
A :ref:`network` represents an IPv4/IPv6 network. Networks also related to eachother in a heirarchical way. Since networks are inherently contained within other networks, no explicit parent child relationship is stored in the database. Networks are homed in a site.


.. figure:: images/mozcore_networks.png

Here networks are laid out along their logical CIDER boundaries. Multiple networks can
be associated with one site, but a network cannot be associated with multiple
sites.

Vlans
-----

For the majority of cases, a network is associated with a :ref:`vlan`.

.. figure:: images/mozcore_all.png

Here networks are shown under vlans. A network can belong to zero or one vlan.
Many networks can belong to the same vlan.

The little red lines under the network objects are :ref:`range` objects.

Ranges
------

Range objects belong inside of a network; a range's start number is greater than or equal to the
network address and the range's end number is less than the broadcast address. Ranges are used to
help determine where free IP's lay within a network, which is useful when creating a
:ref:`staticinterface`.

Here is a beautiful depiction of a range and a network::

    Network:                    192.168.0.0/24
    |--------------------------------------------------------------|
    192.168.0.0                                                    192.168.0.255

    Range:
                |-------------------------------------------------|
                192.168.0.10                                      192.168.0.254


Ranges can be used as a pool of allocatable IP addresses. When a new :ref:`staticinterface`
(seriously, read about these things) is created it needs an IP address and a range is where the
interface will look if the interface is to have it's IP address assigned automatically.

Other Purposes
++++++++++++++

.. note::
    These features (as of 08/12/2012) are not implemented.

Ranges are multipurpose. For example a range can be used as a 'dynamic' range. A dynamic range is a
pool ip addresses where wireless clients or other clients that don't need a fixed addresses have
their IP assignment come from. In DHCP these dynamic ranges usually associated with a pool statement
that contains an ``allow`` clause. In DNS a dynamic range will usually have a long list of similar
names statically created for every ip in the range; for example ``GENERATE 4-100
dynamic-$.vlan.mozilla.com``. When you flag a range as 'dynamic' the DNS build scripts will
automatically print these records when DNS zone files are generated.













