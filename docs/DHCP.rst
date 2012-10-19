.. _dhcp:
.. |intr_ref| replace:: :ref:`StaticInterface`
.. |intr| replace:: :class:`StaticInterface`
.. |range| replace:: :class:`Range`

DHCP
====

.. warning::
    DHCP is implemented for |intr_ref| objects with IPv4 addresses. |intr|'s with IPv6 addresses
    will not be included in the build output.

The core function of the DHCP build system is the :func:`build_subnet` function which accecpts a
:ref:`Network` instance as it's only input. Using the ``network``'s network address
(``network_start``) and network broadcast (``network_end``) every |intr| with an IPv4 address
greater than ``network_start`` less than ``network_end`` is used to generate a ``host`` statement::

    host {{ intr.dhcp_name() }} {
        hardware ethernet {{ intr.mac }};
        fixed-address {{ intr.ip_str }};
    }

The above example is a ``host`` statement where jinja2 syntax is used to show how data from the
|intr| is used to fill in data. The |intr| member function :func:`dhcp_name` is used as a way to
make sure no two ``host`` statements have the same ``hostname``.

.. note::

    Because we are on a tight schedule, it might be worth it to just generate the host entries and
    include them in the DHCP flat files in SVN like we are doing with current inventory. This would
    be a slight modification and would save us time. Doing this means we don't have to put pool and
    subnet options into inventory (could be time consuming sinse they are hard to parse and would
    probably need to be entered by hand).

Address Pools
---------------
There is a 1-to-1 mapping betweek address pools and :ref:`range` objects. A |range| object has a
reference back to it's containing :ref:`Network`, so :func:`build_subnet` selects all |range|
objects and passes the objects one by one into :func:`build_pool`. For each range all statements and
options are gathered and added to the build output. Finally ``range.start_lower`` and
``range.end_lower`` are used as the start and end number in the ``range`` statement (``start_upper``
and ``end_upper`` are only relevent for IPv6 addresses who have more than 64 bits of information).

DHCP Options and Statements
---------------------------

Both ranges and networks have ways of controlling what options and statements go into their
respective ``subnet`` and ``pool`` statements. These options and statements are stored in the
:class:`NetworkKeyValue` and :class:`RangeKeyValue` tables as Key Value pairs.


.. autofunction:: core.build.subnet.build_subnet
.. autofunction:: core.build.subnet.build_pool
