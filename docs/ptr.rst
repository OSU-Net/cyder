.. _ptr:

PTR
===

.. |ptr| replace:: :class:`PTR`

A |ptr| instance represents a reverse ip maping. Because in BIND |ptr| recrods need to go into a reverse zone file that contain an SOA, every |ptr| must be under a domain that the system is authoritative for.

Some examples: Let's assume we are authoritative for the network 192.168.0.0/16 and that we want to create a ptr for the name ``foo.example.com`` to ``192.168.1.9``. If we were to try to add the |ptr| without first makeing a reverse domain for that ptr, a :class:`ValidationError` would be raises::

    >>> from mozdns.ptr.models import PTR
    >>> ptr = PTR(ip_str="192.168.1.9", name="foo.example.com", ip_type='4')
    >>> ptr.full_clean()
    Traceback (most recent call last):
      File "<console>", line 1, in <module>
      File "/var/www/inventory/mozdns/ptr/models.py", line 83, in clean
        self.clean_ip(update_reverse_domain=urd)
      File "/var/www/inventory/mozdns/ip/models.py", line 94, in clean_ip
        ip_type='4'))
      File "/var/www/inventory/vendor/src/django/django/db/models/fields/related.py", line 327, in __set__
        (instance._meta.object_name, self.field.name))
    ValueError: Cannot assign None: "PTR.reverse_domain" does not allow null values.

:func:`full_clean` looks for a reverse domain for ``192.128.1.9``. In the code shown above, no reverse domain is found and a :class:`ValidationError` is raised (admittedly, the error message could be a little more descriptive). Adding an appropriate reverse domain will resolve the traceback::

    >>> domain, _ = Domain.objects.get_or_create("192.in-addr.arpa")
    >>> ptr = PTR(ip_str="192.168.1.9", name="foo.example.com", ip_type='4')
    >>> ptr.full_clean()
    >>> ptr.save()

If we look at the reverse domain of the ptr we created, it will be the reverse domain we just created::

    >>> ptr.reverse_domain
    <Domain '192.in-addr.arpa'>

If we add a new reverse domain that is a better fit for our PTR, the PTR will be assigned that reverse domain::

    >>> domain, _ = Domain.objects.get_or_create("168.192.in-addr.arpa")
    >>> domain.master_domain
    <Domain '192.in-addr.arpa'>
    >>> ptr.reverse_domain
    <Domain '168.192.in-addr.arpa'>



.. automodule:: mozdns.ptr.models
    :inherited-members:
