.. _staticinterface:

Static Interface
================
A static interface allows a user to easily create an A/AAAA :class:`AddressRecord` record,
:class:`PTR` record and register the interface in the DHCP configs.

A static interface relys on having a ``hostname``, ``ip`` and a ``mac`` to
generates DNS and DHCP entries. The DNS entries are an A/AAAA record and a PTR record::

    <hostname>      A     <ip>
    <ip>            PTR   <hostname>

The DHCP entry is a host clause::

    host <hostname> {
        fixed-address <ip>;
        hardware ethernet <mac>;
    }

By choosing an ``ip`` you are in effect assigning the registration to a :class:`Range`.

Automatically Choosing an IP address for an Interface
-----------------------------------------------------

Just by looking at an Interfaces requested hostname we can determine which site
(datacenter and possible business unit) and vlan an Interface is in. Using the
names of the site and vlan we can use information stored in the :ref:`core`
core of inventory to determine which IP address to choose for the interface.
For example::


        webnode1.webops.scl3.mozilla.com


This Interface is in scl3 in the webops vlan. Since Inventory tracks both sites
and vlans getting these objects is just a matter of querying the database.::

    site_scl3 = Site.objects.get(name='scl3')
    vlan_webops = Vlan.objects.get(name='webops')

Networks are associated to vlan's so retreving which networks are in the webops
vlan is one query away.::

    webops_networks = vlan_webops.network_set.all()

Since the webops vlan can exist in multiple datacenters, we only want to look
at networks that are in the webops vlan *and* are in scl3.::

    scl3_webops_networks = []
    for network in webops_networks:
        if network.site == site_scl3:
            scl3_webops_networks.append(network)

We now look for a free IP in a range in one of the networks in ``scl3_webops_networks``.

.. note::
    In most cases there is only one network associated with a vlan in a particular datacenter.

Getting a free ip is easy.::

    network = scl3_webops_networks[0]  # Let's just choose the first one for the sake of example.
    ip = None
    for range in network.range_set.all():
        ip = range.get_next_ip()
        if ip:
            break

We just found a free ip in vlan webops in scl3.

Static Interface
----------------
.. automodule:: core.interface.static_intr.models
    :inherited-members: StaticInterface
