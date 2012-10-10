.. _common_record:

Common Record
=============

The common record class is inherited by common DNS record classes. ``CommonRecord`` is an abstract class meaning there is not table in the database coresponding to it's declaration. It is subclassed by the ``TXT``, ``MX``, ``CNAME``, and ``SRV`` classes.


.. automodule:: mozdns.models
    :inherited-members:

.. automodule:: mozdns.views
    :inherited-members:
