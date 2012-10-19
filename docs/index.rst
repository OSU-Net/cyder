.. |project| replace:: cyder

Welcome to |project|'s documentation!
=====================================

.. include:: cyder_intro.rst


Vocabulary (DNS Jargon)
=======================
* Name and Label: "Each node in the DNS tree has a name consisting of zero or more labels"  `RFC4343 <http://tools.ietf.org/html/rfc4343>`_ . The name ``x.y.z`` consists of the labels ``x``, ``y``, and ``z``. When talking about a name that corresponds to an actual system, the last label is sometimes referred to as the 'hostname'.

* Forward: Used to reference the part of DNS that maps names to Ip addresses.

* Reverse: Used to reverence the part of DNS that maps Ip addresses to names.

Quick Read
==========
*Read these pages for a TL;DR*

*   :ref:`core`

*   :ref:`domain`

Q: Who are these docs for?

A: People who have to read the source code of this project.

Core
====

.. toctree::
   :maxdepth: 2

   staticinterface
   core
   site
   vlan
   network
   range
   flows

DNS
===

The following dns records are supported: A, AAAA, PTR, CNAME, MX, NS, SRV, TXT, SSHFP and SOA

.. toctree::
   :maxdepth: 2

   domain
   label_domain
   BIND
   dns_views
   soa
   nameserver
   mx
   ip
   common_record
   address_record
   ptr
   cname
   srv
   txt
   sshfp
   validation

DHCP
====
.. toctree::
   :maxdepth: 2

   DHCP

Lib
===

.. toctree::
   :maxdepth: 2

   coding_standard
   rage
   lib
   api



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
