.. _validation:

Validation
==========

Validation happens all over the place. These are validation functions that ended up in the same file.

Domain/ReverseDomain Validation
-------------------------------

Use the function ``do_zone_validation`` in model code.

.. autofunction:: mozdns.validation.do_zone_validation
.. autofunction:: mozdns.validation.check_for_master_delegation
.. autofunction:: mozdns.validation.validate_zone_soa
.. autofunction:: mozdns.validation.check_for_soa_partition
.. autofunction:: mozdns.validation.find_root_domain

Name and Label Validation
-------------------------

.. autofunction:: mozdns.validation.validate_label
.. autofunction:: mozdns.validation.validate_domain_name
.. autofunction:: mozdns.validation.validate_name
.. autofunction:: mozdns.validation.validate_reverse_name

TTL Validation
--------------

.. autofunction:: mozdns.validation.validate_ttl

SRV Validation
--------------

:class:`SRV` objects need special validation because of the ``_`` the precedes their names. They also have other fields like ``weight``, ``port`` and ``priority`` that need to be validated.

.. autofunction:: mozdns.validation.validate_srv_port
.. autofunction:: mozdns.validation.validate_srv_priority
.. autofunction:: mozdns.validation.validate_srv_weight
.. autofunction:: mozdns.validation.validate_srv_label
.. autofunction:: mozdns.validation.validate_srv_name


MX Validation
-------------

.. autofunction:: mozdns.validation.validate_mx_priority

IP type Validation
------------------

.. autofunction:: mozdns.validation.validate_ip_type
