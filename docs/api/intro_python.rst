=========================================
Introduction to The Cyder API with Python
=========================================


:Version: 0.2 (draft)
:API Version: 1

.. contents::

-----------------------------
Introduction to the Cyder API
-----------------------------
The Cyder API currently allows read-only access to DNS records, systems, and static interfaces stored in the database. In the future, it will also provide read-write access to these resources.

This document's examples are written in Python, using version 2.7.4, and make use of the urllib_ and urllib2_ standard Python libraries, but anything that can make HTTP requests may also be used. If you prefer to use command line utilities, there is a version of this tutorial that makes use of curl. While this tutorial is fairly elementary, some understanding of urllib2 is expected. You may want to read the Python HOWTO `"Fetch Internet Resources Using urllib2"`_ before starting this tutorial.

.. _urllib: http://docs.python.org/2/library/urllib.html
.. _urllib2: http://docs.python.org/2/library/urllib2.html
.. _"Fetch Internet Resources Using urllib2": http://docs.python.org/2/howto/urllib2.html

Recommended Reading
-------------------
Before reading this tutorial, it is recommended that you read the following:

* `"urllib -- Open arbitrary resources by URL -- Python 2.7.5 documentation"`_
* `"urllib2 -- extensible library for opening URLs -- Python 2.7.5 documentation"`_
* `"Fetch Internet Resources Using urllib2"`_

.. _"urllib -- Open arbitrary resources by URL -- Python 2.7.5 documentation": http://docs.python.org/2/library/urllib.html
.. _"urllib2 -- extensible library for opening URLs -- Python 2.7.5 documentation": http://docs.python.org/2/library/urllib2.html
.. _"Fetch Internet Resources Using urllib2": http://docs.python.org/2/howto/urllib2.html

Document Conventions
--------------------
The following conventions are used throughout this document:

+---------------------------------+-----------------------------------------------------------------------+
|Convention                       | Meaning                                                               |
+=================================+=======================================================================+
| **bold text**                   | Key words or the beginning of important paragraphs.                   |
+---------------------------------+-----------------------------------------------------------------------+
|*italic text*                    | Interface text.                                                       |
+---------------------------------+-----------------------------------------------------------------------+
| ``monospace text``              | | Inline: Names from code or serialized data.                         |
|                                 | | Paragraph: Example code or code output.                             |
+---------------------------------+-----------------------------------------------------------------------+

For readability, all API responses in this tutorial will be formatted with linebreaks and indentation, and some may be abbreviated. Actual API responses may differ. If you want your API responses to look as pretty as mine do, pipe the output of your Python script to ``python -mjson.tool``.

---------------
Getting Started
---------------
This section covers some basic features and terminology of the Cyder API. You'll learn how to get API access, structure a basic request, authenticate to the server, differentiate between the endpoints provided by the API, and traverse relations between records.

Requesting Your API Token
-------------------------
API access is restricted to those with a **token**. A token is a randomly-generated 40 character hex string that is associated with your username. All API requests must be accompanied by a valid token or the request will be ignored.

Generating your token is simple:

1. Log into Cyder.

2. Go to your user profile (click your username at the top of the screen).

3. Click *Request API Token*.

4. Enter the token's intended purpose.

You will now see a page with your token's key, purpose, and date of creation. From this page you can also revoke your token, should it be compromised or no longer needed.

**Note:** It is strongly recommended that you generate a new key for each application that will be accessing the API.

Through this tutorial, the placeholder ``MY_TOKEN`` will be used instead of an actual API token. Anywhere you see ``MY_TOKEN`` used, you should replace it with your own token.

API Basics
----------
In this section, we'll do a low level overview of the data provided by the API using only Python and the urllib2 library.

~~~~~~~~~~~~~~~
Request Objects
~~~~~~~~~~~~~~~
First, let's look at a basic function to submit requests to the API:

.. code:: python

    import urllib2

    def api_connect(url, token):
        req = urllib2.Request(url)
        req.add_header('Authorization', 'Token ' + token)
        return urllib2.urlopen(req).read()

This function illustrates the structure of a very basic **request object** used to access the Cyder API. A request object is used by urllib2 to structure your request to the server. In order to access the API, you must include an HTTP ``Authorization`` header with a valid API token.

~~~~~~~~~~~~~
API Root View
~~~~~~~~~~~~~
 If the API root URL and a valid token are passed to the function, it returns the following as a string:

.. code:: json

    {
        "core/ctnr": "http://127.0.0.1:8000/api/v1/core/ctnr/",
        "core/system": "http://127.0.0.1:8000/api/v1/core/system/",
        "core/system/keyvalues": "http://127.0.0.1:8000/api/v1/core/system/keyvalues/",
        "core/user": "http://127.0.0.1:8000/api/v1/core/user/",
        "dhcp/dynamic_interface": "http://127.0.0.1:8000/api/v1/dhcp/dynamic_interface/",
        "dhcp/dynamic_interface/keyvalues": "http://127.0.0.1:8000/api/v1/dhcp/dynamic_interface/keyvalues/",
        "dhcp/network": "http://127.0.0.1:8000/api/v1/dhcp/network/",
        "dhcp/network/keyvalues": "http://127.0.0.1:8000/api/v1/dhcp/network/keyvalues/",
        "dhcp/range": "http://127.0.0.1:8000/api/v1/dhcp/range/",
        "dhcp/range/keyvalues": "http://127.0.0.1:8000/api/v1/dhcp/range/keyvalues/",
        "dhcp/site": "http://127.0.0.1:8000/api/v1/dhcp/site/",
        "dhcp/site/keyvalues": "http://127.0.0.1:8000/api/v1/dhcp/site/keyvalues/",
        "dhcp/static_interface": "http://127.0.0.1:8000/api/v1/dhcp/static_interface/",
        "dhcp/static_interface/keyvalues": "http://127.0.0.1:8000/api/v1/dhcp/static_interface/keyvalues/",
        "dhcp/vlan": "http://127.0.0.1:8000/api/v1/dhcp/vlan/",
        "dhcp/vlan/keyvalues": "http://127.0.0.1:8000/api/v1/dhcp/vlan/keyvalues/",
        "dhcp/vrf": "http://127.0.0.1:8000/api/v1/dhcp/vrf/",
        "dhcp/vrf/keyvalues": "http://127.0.0.1:8000/api/v1/dhcp/vrf/keyvalues/",
        "dhcp/workgroup": "http://127.0.0.1:8000/api/v1/dhcp/workgroup/",
        "dhcp/workgroup/keyvalues": "http://127.0.0.1:8000/api/v1/dhcp/workgroup/keyvalues/",
        "dns/address_record": "http://127.0.0.1:8000/api/v1/dns/address_record/",
        "dns/cname": "http://127.0.0.1:8000/api/v1/dns/cname/",
        "dns/domain": "http://127.0.0.1:8000/api/v1/dns/domain/",
        "dns/mx": "http://127.0.0.1:8000/api/v1/dns/mx/",
        "dns/nameserver": "http://127.0.0.1:8000/api/v1/dns/nameserver/",
        "dns/ptr": "http://127.0.0.1:8000/api/v1/dns/ptr/",
        "dns/soa": "http://127.0.0.1:8000/api/v1/dns/soa/",
        "dns/soa/keyvalues": "http://127.0.0.1:8000/api/v1/dns/soa/keyvalues/",
        "dns/srv": "http://127.0.0.1:8000/api/v1/dns/srv/",
        "dns/sshfp": "http://127.0.0.1:8000/api/v1/dns/sshfp/",
        "dns/txt": "http://127.0.0.1:8000/api/v1/dns/txt/"
    }

This response contains no information from the database, but it is immediately useful because it provides us with information about the API itself. First, it tells us the types of data that we can access, and second, it tells us where this data can be found. This also shows a common trend in the Cyder API: where appropriate, URLs to related records are provided in place of data from the records themselves. This allows you to traverse relations in the Cyder database without constructing URLs or even knowing the structure of the API in advance.

~~~~~~~~~~
List Views
~~~~~~~~~~
Let's see what happens when we pass one of these URLs to ``api_connect``:

.. code:: python

    print api_connect("http://127.0.0.1:8000/api/v1/dns/domain/",  MY_TOKEN)

This returns a **list view** of Domain records. List views allow you to navigate through sets of records and are automatically paginated to lessen the load on the server and client. Here is a truncated version of a possible response to the above query:

.. code:: json

    {
        "count": 2068,
        "next": "http://127.0.0.1:8000/api/v1/dns/domain/?page=2",
        "previous": null,
        "results": [
            {
                "delegated": false,
                "dirty": false,
                "id": 1,
                "is_reverse": true,
                "master_domain": null,
                "name": "arpa",
                "purgeable": false,
                "soa": null
            },
            {
                "delegated": false,
                "dirty": false,
                "id": 2,
                "is_reverse": true,
                "master_domain": "http://127.0.0.1:8000/api/v1/dns/domain/1/",
                "name": "in-addr.arpa",
                "purgeable": false,
                "soa": null
            },
            ...
        ]
    }

There are a few important things to note here:

1. ``count``, ``next``, and ``previous`` all provide data that can help simplify API interaction.

   - ``count`` gives the number of records of the requested type. This makes it easy to iterate through records without making additional requests to check when you've reached the end.
   - ``next`` and ``previous`` each contain URLs to the next and previous page of results. These are constructed dynamically by the API, so they will always contain any query parameters you have passed. Because these values will be ``null`` if no such page exists, you can also use them to iterate through multi-page lists of results without having to count. This is also safer than counting, because changes made to the database in the middle of a large batch of API requests may cause there to be a different number of pages than there were at the beginning of the operation.

2. As stated before, where appropriate, related records are pointed to with URLs for easy navigation. In this case, if you wanted to check the master domain of the domain name ``in-addr.arpa``, you could simply pass the value of ``master_domain`` to api_connect and retrieve the appropriate record.

~~~~~~~~~~~~
Detail Views
~~~~~~~~~~~~
Now we know how to retrieve general lists of objects, but what if we want to access a specific record? Since our previous response contained a URL pointing directly to a record, let's see what happens when we follow that URL.

.. code:: python

    print api_connect("http://127.0.0.1:8000/api/v1/dns/domain/2/",  MY_TOKEN)

This returns a **detail view** of the Domain record with an ``id`` of 2.

.. code:: json

    {
        "delegated": false,
        "dirty": false,
        "id": 2,
        "is_reverse": true,
        "master_domain": "http://127.0.0.1:8000/api/v1/dns/domain/1/",
        "name": "in-addr.arpa",
        "purgeable": false,
        "soa": null
    }

You can see that the structure of this record is the same as it was in the list view. Once again, the ``master_domain`` field contains a hyperlink to the related record.

---------
Diving In
---------
This section covers more advanced API topics. You'll learn how to filter results in a variety of ways, including by basic fields, related fields, container, and key-value pairs.

Filtering
---------
Most of the time, you will be using the API to find records matching different search queries. The Cyder API has very powerful search functionality that allows you to query the database by passing your search parameters in the query string. Here's an updated version of our ``api_connect`` function with added support for query parameters:

.. code:: python

    import urllib
    import urllib2

    def api_connect(url, token, params=None):
        if params:
            url += "?" + urllib.urlencode(params)
        req = urllib2.Request(url)
        req.add_header('Authorization', 'Token ' + token)
        return urllib2.urlopen(req).read()

This function is very simple and doesn't support adding query parameters to a URL which already has them, but it is sufficient for our purposes.

~~~~~~~~~~~~~~~~~~~
Filtering by Fields
~~~~~~~~~~~~~~~~~~~
Let's say we want to query for every CNAME that aliases a non ``orst.edu`` domain to ``www.orst.edu``. First, we need to determine the structure of CNAME records, so let's look at the CNAME list view.

.. code:: python

    print api_connect("http://127.0.0.1:8000/api/v1/dns/cname/", MY_TOKEN)

Here's the first record we get back:

.. code:: json

    {
        "description": "",
        "fqdn": "www.emt.orst.edu",
        "id": 1,
        "target": "www.orst.edu",
        "ttl": 3600,
        "views": [
            "public"
        ]
    }

Any of the fields listed here can be queried. Let's try building our query. Cyder API queries are very powerful and support a variety of flexible matching based on Django's `field lookups`_.

.. _field lookups: https://docs.djangoproject.com/en/1.5/topics/db/queries/#field-lookups

~~~~~~~~~~~~~~~
Querying Fields
~~~~~~~~~~~~~~~
Before we can write our query, however, we need to know the basic structure of each filter. Each filter must contain a selection mode, the field to query, and the field lookup type. The exact structure can be easily described with Extended Backus-Naur Form:

.. code::

    mode         = "i:" | "e:"

    field        = ? any valid field name ?

    field lookup = "exact" | "iexact" | "contains" | "icontains" | "gt"
                 | "gte" | "lt" | "lte" | "startswith" | "istartswith"
                 | "endswith" | "iendswith" | "isnull"

    filter       = mode, "_", field, "__", field lookup

Here, ``mode`` sets whether records matching the query should be included (``i:``) or excluded (``e:``). ``field`` must contain the name of a field in the record, including related fields. ``field lookup`` is used to decide how records should be matched. Each of the supported query types is described in Django's `field lookups reference`_ and this document's `Summary of Field Lookups`_. Note that the field lookups ``in``, ``range``, ``year``, ``month``, ``day``, ``week_day``, ``regex``, and ``iregex`` are not supported.

.. _field lookups reference: https://docs.djangoproject.com/en/1.4/ref/models/querysets/#field-lookups

Multiple filters can be combined in a single query to further refine the results.

With this basic format, let's write our query. Remember, we want every CNAME that aliases a non ``orst.edu`` domain to ``www.orst.edu``. This means that we want all records where ``target`` equals ``www.orst.edu``, but where ``fqdn`` doesn't contain ``orst.edu``. First, let's only retrieve results matching the first critera, so we have a baseline to compare our results against.

.. code:: python

    query = {'i:target__exact': 'www.orst.edu'}
    print api_connect("http://127.0.0.1:8000/api/v1/cname/", MY_TOKEN, query)

.. code:: json

    {
        "count": 233,
        "next": "http://127.0.0.1:8000/api/v1/cname/?i:target__exact=www.orst.edu&page=2",
        "previous": null,
        "results": [
            {
                "description": "",
                "fqdn": "www.emt.orst.edu",
                "id": 1,
                "target": "www.orst.edu",
                "ttl": 3600,
                "views": [
                    "public"
                ]
            },
            {
                "description": "",
                "fqdn": "emt.orst.edu",
                "id": 7,
                "target": "www.orst.edu",
                "ttl": 3600,
                "views": [
                    "public"
                ]
            },
            {
                "description": "",
                "fqdn": "diversity.oregonstate.edu",
                "id": 56,
                "target": "www.orst.edu",
                "ttl": 3600,
                "views": [
                    "public"
                ]
            },
            ...
        ]
    }

Here we can see the first two results are both domains under ``orst.edu``. Let's try filtering them out. We know we don't want any domain including ``orst.edu``, so let's use an exclusion filter to remove any result where the field ``fqdn`` has ``orst.edu`` in it.

.. code:: python

    query = {'i:target__exact': 'www.orst.edu', 'e:fqdn__contains': 'orst.edu'}
    print api_connect("http://127.0.0.1:8000/api/v1/dns/cname/", MY_TOKEN, query)

.. code:: json

    {
        "count": 182,
        "next": "http://127.0.0.1:8000/api/v1/cname/?i:target__exact=www.orst.edu&e:fqdn__contains=orst.edu&page=2",
        "previous": null,
        "results": [
            {
                "description": "",
                "fqdn": "diversity.oregonstate.edu",
                "id": 56,
                "target": "www.orst.edu",
                "ttl": 3600,
                "views": [
                    "public"
                ]
            },
            ...
        ]
    }

Now we've got exactly what we're looking for. We can see that the extra filter caused 51 records to be excluded from the results, and that the API conveniently includes our filter terms in its ``next`` field. This sort of querying can easily be done on any record type and with any field.

~~~~~~~~~~~~~~~~~~~~~~~
Querying Related Fields
~~~~~~~~~~~~~~~~~~~~~~~
Basic queries are not only limited to top-level fields. Sometime it is desirable to search based on related fields. For example, let's say we wanted to find all MX records for the domain ``orst.edu``. First, let's see what the MX records look like.

.. code:: python

    print api_connect("http://127.0.0.1:8000/api/v1/dns/mx/", MY_TOKEN)

.. code:: json

    {
        "count": 521,
        "next": "http://127.0.0.1:8000/api/v1/dns/mx/?page=2",
        "previous": null,
        "results": [
            {
                "label": "rattusdev",
                "domain": "http://127.0.0.1:8000/api/v1/dns/domain/2727/",
                "views": [
                    "public"
                ],
                "id": 286,
                "created": "2013-08-16T15:18:45",
                "modified": "2013-08-16T15:18:45",
                "fqdn": "rattusdev.nacse.org",
                "ttl": 86400,
                "description": "",
                "server": "relay.oregonstate.edu",
                "priority": 5
            },
            ...
        ]
    }

We know that domain records have a ``name`` field containing their FQDN, so we should construct our query to find only MX records attached to the domain ``orst.edu``. Querying fields of related records is easily accomplished by appending two underscores and the name of the field we want to query in the related record. For example, querying the domain name of MX records is accomplished like so:

.. code:: python

    query = {'i:domain__name__exact': 'orst.edu'}
    print api_connect("http://127.0.0.1:8000/api/v1/dns/mx/", MY_TOKEN, query)

Now our results look like this:

.. code:: json

    {
        "count": 9,
        "next": null,
        "previous": null,
        "results": [
            {
                "label": "exchangemail",
                "domain": "http://127.0.0.1:8000/api/v1/dns/domain/2974/",
                "views": [
                    "public"
                ],
                "id": 410,
                "created": "2013-08-16T15:24:29",
                "modified": "2013-08-16T15:24:29",
                "fqdn": "exchangemail.orst.edu",
                "ttl": 86400,
                "description": "",
                "server": "ex1.oregonstate.edu",
                "priority": 5
            },
            ...
        ]
    }

~~~~~~~~~~~~~~~~~~~~~~
Filtering by Container
~~~~~~~~~~~~~~~~~~~~~~
As with the Cyder user interface, the Cyder API allows you to filter results by their associated container. You can filter by the container's name or its ID. For example, if you wanted to find all domains in the container ``nws``, you could pass the query string parameter ``ctnr=nws`` or ``ctnr_id=292``. (Note that you can only filter by one container at a time. It is not currently possible to find the intersection of two or more containers.)

~~~~~~~~~~~~~~~~~~~~~~~
Filtering by Key-Values
~~~~~~~~~~~~~~~~~~~~~~~
Many records have key-value pairs (also called attributes) associated with them. Specifically, the following records have key-value pairs and key-value pair filtering enabled:

* System
* SOA
* Site
* Network
* Range
* VLAN
* VRF
* Workgroup
* Static Interface
* Dynamic Interface

Key value filtering is very straightforward. However, for technical reasons, it is also somewhat limited compared to ordinary field searching. Only case insensitive exact matching (the same as the ``iexact`` field lookup) is allowed for key-value searching. It is possible to access key-value records directly and perform more complex queries with field lookups, but this doesn't allow you to search for combinations of key-value pairs on the same record without more complex client-side processing.

As an example, let's try finding all systems running Linux.

.. code:: python

    query = {'k:operating+system': 'linux'}
    print api_connect("http://127.0.0.1:8000/api/v1/core/system/", MY_TOKEN, query)

.. code:: json

    {
        "count": 363,
        "next": "http://127.0.0.1:8000/api/v1/core/system/?k:operating+system=linux&page=2",
        "previous": null,
        "results": [
            {
                "id": 9918,
                "name": "voledev",
                "systemkeyvalue_set": [
                    {
                        "id": "http://127.0.0.1:8000/api/v1/core/system/keyvalues/29699/",
                        "key": "Hardware Type",
                        "value": "VM",
                        "is_quoted": false
                    },
                    {
                        "id": "http://127.0.0.1:8000/api/v1/core/system/keyvalues/29700/",
                        "key": "Operating System",
                        "value": "Linux",
                        "is_quoted": false
                    }
                ]
            },
            ...
        ]
    }

This list can be used as is, or it can be further filtered with additional query parameters. For example, we could search for all systems running Linux in the ``nws`` container, or all enabled IPv6 networks on a certain VLAN.

Summary of Field Lookups
------------------------
~~~~~
exact
~~~~~
Find all rows where the queried field matches the exact query value; case sensitive. If you pass the query string parameter ``i:field__exact=Go+Beavs``, it will match fields that contain the value "Go Beavs", but not "go beavs" or "go Beavs".

~~~~~~
iexact
~~~~~~
Find all rows where the queried field matches the exact query value; case insensitive. If you pass the query string parameter ``i:field__iexact=Go+Beavs``, it will match fields that contain the value "Go Beavs", "go beavs", and "go Beavs", as well as any other capitalizations of the string "Go Beavs".

~~~~~~~~
contains
~~~~~~~~
Find all rows where the queried field contains the search value; case sensitive. If you pass the query string parameter ``i:field__contains=Beav``, it will match fields that contain the value "Go Beavs", "I love the Beavs", and "Go Beavers!", but not "go beavs", "I love the beavs", or "Go beavers!"

~~~~~~~~~
icontains
~~~~~~~~~
Find all rows where the queried field contains the search value; case sensitive. If you pass the query string parameter ``i:field__icontains=Beav``, it will match fields that contain the value "Go Beavs", "I love the Beavs", "Go Beavers!", "go beavs", "I love the beavs", and "Go beavers!", as well as any other string containing the search value, regardless of case.

~~
gt
~~
Find all rows where the queried field contains a value that is greater than the search value.

Example query:

.. code::

    ?i:field_gt=10

~~~
gte
~~~
Find all rows where the queried field contains a value that is greater than or equal to the search value.

Example query:

.. code::

    ?i:field_gte=10

~~
lt
~~
Find all rows where the queried field contains a value that is less than the search value.

Example query:

.. code::

    ?i:field_lt=10

~~~
lte
~~~
Find all rows where the queried field contains a value that is less than or equal to the search value.

Example query:

.. code::

    ?i:field_lte=10

~~~~~~~~~~
startswith
~~~~~~~~~~
Find all rows where the queried field starts with the search value; case sensitive. If you pass the query string parameter ``i:field__startswith=Go``, it would match "Go Beavs!" and "Go Beavers!", but not "go beavs", "GO BEAVS!", or "Let's go Beavers!"

~~~~~~~~~~~
istartswith
~~~~~~~~~~~
Find all rows where the queried field starts with the search value; case insensitive. If you pass the query string parameter ``i:field__istartswith=Go``, it would match "Go Beavs!", "Go Beavers!", "go beavs", and "GO BEAVS!", but not "Let's go Beavers!"

~~~~~~~~
endswith
~~~~~~~~
Find all rows where the queried field ends with the search value; case sensitive. If you pass the query string parameter ``i:field__endswith=Beavers``, it would match "Go Beavers" and "I love the Beavers", but not "GO BEAVERS", "Go Beavers!", or "I love the Beavers."

~~~~~~~~~
iendswith
~~~~~~~~~
Find all rows where the queried field ends with the search value; case insensitive. If you pass the query string parameter ``i:field__iendswith=Beavers``, it would match "Go Beavers", "I love the Beavers", and "GO BEAVERS", but not "Go Beavers!" or "I love the Beavers."

~~~~~~
isnull
~~~~~~
Find all rows where the queried field is null or not null. If you pass the query string parameter ``i:field__isnull=False``, it would only match rows where ``field`` has a value.