Inventory DNS API
=================

A high level view of how the API works::

    +------+
    | User |
    +------+
        |
    +------------------------+
    | Command Line Interface |   <----------- See page on CLI for this
    +------------------------+
        |
    +---------------+
    | HTTP POST/GET |   <----------- This document defines what is happening here.
    +---------------+
        |
    +----------+
    | Iventory |
    +----------+
        |
    +----------+
    | Database |
    +----------+

DNS Objects
-----------
The following DNS objects can be created, updated, and deleted via HTTP API requests.

    * A records
    * AAAA records
    * CNAME records
    * TXT records
    * MX records
    * SRV records
    * NS records
    * SSHFP records

The following cannot be created, updated, or deleted via HTTP API requests.

    * SOA records
    * Certain Domain objects
        - see :ref:`label_domain`. Only purgeable domains can be created via the API.

Views and Key Value
-------------------
View objects need their associated object to exist before they can be created. Underneath the hood,
these objects are validated and saved *after* their associtated object is saved or updated.

Currently, updating views is done by supplying the desired objects' state. For example, if you
want to add an object to the public view and the object was already in the private view, you would
post the list::

    'views': ['public', 'private']

If you were to send an emtry list::

    'views': []

Any views the object was associated with would be deleted.

The best way to update an object is to first GET the object, modify the JSON returned by the API,
and then PATCH it back.

Key Value Pairs
---------------
Updating key value (kv) pairs that are associated with an object is done just like any other
attribute on the object except it must be done with only the 'key' and 'value' parameters in the
request. This means that updating a field, like 'comment', and a key value pair is not allowed::

    {'key': 'foo', 'value': 'bar', 'comment': 'a new comment'}

The above is not allowed because 'key' and 'value' must be the only elements in the JSON.

You should post kv pairs to the end point of the object is associated to the kv pair.
