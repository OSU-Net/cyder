`Cyder <https://github.com/uberj/Cyder>`_ is an `IPAM <http://en.wikipedia.org/wiki/IP_address_management>`_ solution. It is split up into two logically separate apps; ``cydns`` (DNS) and ``cydhcp`` (DHCP). The goal is two have the two apps be standalone and have less generic code 'glue' them together.

The 'glue' (not to be confused with DNS glue records) is found in ``core/``.

Maintain
--------
Cyder is designed to replace `Maintain <http://maintainproject.osuosl.org/>`_. Maintain 2.5 was the
last version released. Maintain 3 was written in purely in PHP and didn't work too well.
Aside from initially being written almost a decade ago, Maintain has been used in production at OSU
for over 10 years.

Taken from Maintain's README, here are the abridged requirements of Maintain:

* Web-based interface
* Ability to delegate authority of zone information to individual users/groups
* Quick updates (changes need to be reflected within 10 minutes)
* Advanced error reporting for zone transfers and DHCP server problems
* Generate zone files and DHCP configurations for primary and secondary DNS & DHCP servers
* Edit host information including MAC address, hostname, domain name, etc.
* Zone statistics such as total bandwidth used and bandwidth history for individual hosts
* Support for automatic registration on public networks (using authentication)
* Search by hostname, domain, zone, IP address and any other DNS type
* Ability to develop additional features through a module interface

Cyder will have all of these features and more.

Maintain Bugs
+++++++++++++
* DNSSEC is not supported.
* Certain DNS records that were at domain level were not supported (they have been hacked in).
* No support of other DNS output types. Only ``tinydns`` is supported.
* The following DNS record types are not supported ``SRV``, ``TXT``, (more)?
* DNS Zone delegation is broken.
* When a (maintain) zone administrator wants to manually assign an IP address to a client, DHCP needs to be bypassed.
  Maintian does this by providing a mac with all zeroes. It's a kludge.
* There can be several different ``defualt_domains`` assigned to the same range.
* Poor searching capabilities.
* Maintain was not built with a web framework. Ironically, this makes the code very hard to maintain.
* Written in PHP.

Maintain has it's weaknesses, but overall it does get the job done. It has already been shown that
Maintain's existing DNS scheme *does* `support building bind files
<https://github.com/uberj/maintain-bindbuilds>`_ (some modification to data in the database was
required due to poor data validation). Cyder is Maintain with a more formal structure. Cyder uses
many core concepts from Maintain.
