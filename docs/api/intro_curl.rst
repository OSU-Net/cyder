=======================================
Introduction to the Cyder API with Curl
=======================================

:Version: 0.2
:API Version: 1

.. contents::

-----------------------------
Introduction to the Cyder API
-----------------------------
The Cyder API currently allows read-only access to DNS records, systems, and static interfaces stored in the database. In the future, it will also provide read-write access to these resources.

This document's examples make use of curl, but anything that can make HTTP requests may also be used. A Python version of this tutorial is available if you don't like curl. While this tutorial is fairly elementary, some understanding of curl is expected. You may want to consult ``man curl`` and `"The Art Of Scripting HTTP Requests Using Curl"`_ before continuing.

.. _"The Art Of Scripting HTTP Requests Using Curl": http://curl.haxx.se/docs/httpscripting.html

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

For readability, all API responses in this tutorial will be formatted with linebreaks and indentation, and some may be abbreviated. Actual API responses may differ. If you want your API responses to look as pretty as mine do, pipe the output of your curl request to ``python -mjson.tool``.

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

Through this tutorial, the placeholder ``MY_TOKEN`` will be used instead of an actual API token. Anywhere you see ``MY_TOKEN`` used, you must replace it with your own token.

API Basics
----------
In this section, we'll do a low level overview of the data provided by the API using only Python and the urllib2 library.

~~~~~~~~~~~~~
API Root View
~~~~~~~~~~~~~
First let's construct a basic request to the API.

.. code::

    curl -H "Authorization: Token MY_TOKEN" "https://cyder.nws.oregonstate.edu/api/v1/"

Assuming the requested token and URL are valid, you should now be presented with a listing of all available API endpoints.

.. code:: json

    {
        "core/ctnr": "https://cyder.nws.oregonstate.edu/api/v1/core/ctnr/",
        "core/system": "https://cyder.nws.oregonstate.edu/api/v1/core/system/",
        "core/system/attributes": "https://cyder.nws.oregonstate.edu/api/v1/core/system/attributes/",
        "core/user": "https://cyder.nws.oregonstate.edu/api/v1/core/user/",
        "dhcp/dynamic_interface": "https://cyder.nws.oregonstate.edu/api/v1/dhcp/dynamic_interface/",
        "dhcp/dynamic_interface/attributes": "https://cyder.nws.oregonstate.edu/api/v1/dhcp/dynamic_interface/attributes/",
        "dhcp/network": "https://cyder.nws.oregonstate.edu/api/v1/dhcp/network/",
        "dhcp/network/attributes": "https://cyder.nws.oregonstate.edu/api/v1/dhcp/network/attributes/",
        "dhcp/range": "https://cyder.nws.oregonstate.edu/api/v1/dhcp/range/",
        "dhcp/range/attributes": "https://cyder.nws.oregonstate.edu/api/v1/dhcp/range/attributes/",
        "dhcp/site": "https://cyder.nws.oregonstate.edu/api/v1/dhcp/site/",
        "dhcp/site/attributes": "https://cyder.nws.oregonstate.edu/api/v1/dhcp/site/attributes/",
        "dhcp/static_interface": "https://cyder.nws.oregonstate.edu/api/v1/dhcp/static_interface/",
        "dhcp/static_interface/attributes": "https://cyder.nws.oregonstate.edu/api/v1/dhcp/static_interface/attributes/",
        "dhcp/vlan": "https://cyder.nws.oregonstate.edu/api/v1/dhcp/vlan/",
        "dhcp/vlan/attributes": "https://cyder.nws.oregonstate.edu/api/v1/dhcp/vlan/attributes/",
        "dhcp/vrf": "https://cyder.nws.oregonstate.edu/api/v1/dhcp/vrf/",
        "dhcp/vrf/attributes": "https://cyder.nws.oregonstate.edu/api/v1/dhcp/vrf/attributes/",
        "dhcp/workgroup": "https://cyder.nws.oregonstate.edu/api/v1/dhcp/workgroup/",
        "dhcp/workgroup/attributes": "https://cyder.nws.oregonstate.edu/api/v1/dhcp/workgroup/attributes/",
        "dns/address_record": "https://cyder.nws.oregonstate.edu/api/v1/dns/address_record/",
        "dns/cname": "https://cyder.nws.oregonstate.edu/api/v1/dns/cname/",
        "dns/domain": "https://cyder.nws.oregonstate.edu/api/v1/dns/domain/",
        "dns/mx": "https://cyder.nws.oregonstate.edu/api/v1/dns/mx/",
        "dns/nameserver": "https://cyder.nws.oregonstate.edu/api/v1/dns/nameserver/",
        "dns/ptr": "https://cyder.nws.oregonstate.edu/api/v1/dns/ptr/",
        "dns/soa": "https://cyder.nws.oregonstate.edu/api/v1/dns/soa/",
        "dns/soa/attributes": "https://cyder.nws.oregonstate.edu/api/v1/dns/soa/attributes/",
        "dns/srv": "https://cyder.nws.oregonstate.edu/api/v1/dns/srv/",
        "dns/sshfp": "https://cyder.nws.oregonstate.edu/api/v1/dns/sshfp/",
        "dns/txt": "https://cyder.nws.oregonstate.edu/api/v1/dns/txt/"
    }

This response contains no information from the database, but it is immediately useful because it provides us with information about the API itself in the form of the **root view**. First, it tells us the types of data that we can access, and second, it tells us where this data can be found. This also shows a common trend in the Cyder API: where appropriate, URLs to related records are provided in place of data from the records themselves. This allows you to traverse relations in the Cyder database without constructing URLs or even knowing the structure of the API in advance.

~~~~~~~~~~
List Views
~~~~~~~~~~
Let's see what happens when we request one of the returned URLs.

.. code::

    curl -H "Authorization: Token MY_TOKEN" "https://cyder.nws.oregonstate.edu/api/v1/dns/domain/"

This returns a **list view** of Domain records. List views allow you to navigate through sets of records and are automatically paginated to lessen the load on the server and the client. Later, when you learn about filtering, list views will become the most important part of the Cyder API. Here's an example response to the above query:

.. code:: json

    {
        "count": 2148,
        "next": "https://cyder.nws.oregonstate.edu/api/v1/dns/domain/?page=2",
        "previous": null,
        "results": [
            {
                "created": "2013-11-07T12:35:06",
                "delegated": false,
                "dirty": false,
                "id": 1,
                "is_reverse": true,
                "master_domain": null,
                "modified": "2013-11-07T12:35:06",
                "name": "arpa",
                "purgeable": false,
                "soa": null,
                "url": "https://cyder.nws.oregonstate.edu/dns/domain/1/"
            },
            {
                "created": "2013-11-07T12:35:06",
                "delegated": false,
                "dirty": false,
                "id": 2,
                "is_reverse": true,
                "master_domain": "https://cyder.nws.oregonstate.edu/api/v1/dns/domain/1/",
                "modified": "2013-11-07T12:35:06",
                "name": "in-addr.arpa",
                "purgeable": false,
                "soa": null,
                "url": "https://cyder.nws.oregonstate.edu/dns/domain/2/"
            },
            ...
        ]
    }

1. ``count``, ``next``, and ``previous`` all provide data that can help simplify API interaction.

   - ``count`` gives the number of records of the requested type. This makes it easy to iterate through records without making additional requests to check when you've reached the end.
   - ``next`` and ``previous`` each contain URLs to the next and previous page of results. These are constructed dynamically by the API, so they will always contain any query parameters you have passed. Because these values will be ``null`` if no such page exists, you can also use them to iterate through multi-page lists of results without having to count. This is also safer than counting, because changes made to the database in the middle of a large batch of API requests may cause there to be a different number of pages than there were at the beginning of the operation.

2. As stated before, where appropriate, related records are pointed to with URLs for easy navigation. In this case, if you wanted to check the master domain of the domain name ``in-addr.arpa``, you could simply pass the value of ``master_domain`` to curl and retrieve the appropriate record.


~~~~~~~~~~~~
Detail Views
~~~~~~~~~~~~
Now we know how to retrieve general lists of objects, but what if we want to access a specific record? Since our previous response contained a URL pointing directly to a record, let's see what happens when we follow that URL.

.. code::

    curl -H "Authorization: Token MY_TOKEN" "https://cyder.nws.oregonstate.edu/api/v1/dns/domain/2/"

This returns a **detail view** of the Domain record with an ``id`` of 2.

.. code:: json

    {
        "created": "2013-11-07T12:35:06",
        "delegated": false,
        "dirty": false,
        "id": 2,
        "is_reverse": true,
        "master_domain": "https://cyder.nws.oregonstate.edu/api/v1/dns/domain/1/",
        "modified": "2013-11-07T12:35:06",
        "name": "in-addr.arpa",
        "purgeable": false,
        "soa": null,
        "url": "https://cyder.nws.oregonstate.edu/dns/domain/2/"
    }

You can see that the structure of this record is the same as it was in the list view. Once again, the ``master_domain`` field contains a hyperlink to the related record.

---------
Diving In
---------
This section covers more advanced API topics. You'll learn how to filter results in a variety of ways, including by basic fields, related fields, container, and key-value pairs.

Filtering
---------
Most of the time, you will be using the API to find records matching different search queries. The Cyder API has very powerful search functionality that allows you to query the database by passing your search parameters in the query string.

~~~~~~~~~~~~~~~~~~~
Filtering by Fields
~~~~~~~~~~~~~~~~~~~
Let's say we want to query for every CNAME that aliases a non ``orst.edu`` domain to ``www.orst.edu``. First, we need to determine the structure of CNAME records, so let's look at the CNAME list view.

.. code::

    curl -H "Authorization: Token MY_TOKEN" "https://cyder.nws.oregonstate.edu/api/v1/dns/cname/"

Here's the first record we get back:

.. code:: json

    {
        "created": "2013-11-08T18:37:24",
        "description": "",
        "domain": "https://cyder.nws.oregonstate.edu/api/v1/dns/domain/1416/",
        "fqdn": "www.emt.orst.edu",
        "id": 1,
        "label": "www",
        "modified": "2013-11-08T18:37:24",
        "target": "www.orst.edu",
        "ttl": 3600,
        "views": [
            "private",
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

    mode         = "i" | "e"

    field        = ? any valid field name ?

    field lookup = "exact" | "contains" | "in" | "gt" | "gte" | "lt" | "lte"
                 | "startswith" | "endswith" | "range" | "year" | "month"
                 | "day" | "week_day" | "isnull" | "search"

    filter       = mode, ":", field, "__", field lookup

Here, ``mode`` sets whether records matching the query should be included (``i:``) or excluded (``e:``). ``field`` must contain the name of a field in the record, including related fields. ``field lookup`` is used to decide how records should be matched. Each of the supported query types is described in Django's `field lookups reference`_. Note that the field lookups ``regex`` and ``iregex`` are not supported. Additionally, some of the supported field lookups are idiosyncratic and must be used in unique ways which will be discussed later.

.. COMMENT: TODO Change last sentence to reference specific section.

.. _field lookups reference: https://docs.djangoproject.com/en/1.4/ref/models/querysets/#field-lookups

Multiple filters can be combined in a single query to further refine the results.

With this basic format, let's write our query. Remember, we want every CNAME that aliases a non ``orst.edu`` domain to ``www.orst.edu``. This means that we want all records where ``target`` equals ``www.orst.edu``, but where ``fqdn`` doesn't contain ``orst.edu``. First, let's only retrieve results matching the first critera, so we have a baseline to compare our results against.

.. code::

    curl -H "Authorization: Token MY_TOKEN" "https://cyder.nws.oregonstate.edu/api/v1/dns/cname/?i:target__exact=www.orst.edu"

.. code:: json

    {
        "count": 235,
        "next": "https://cyder.nws.oregonstate.edu/api/v1/dns/cname/?i%3Atarget__exact=www.orst.edu&page=2",
        "previous": null,
        "results": [
            {
                "created": "2013-11-08T18:37:24",
                "description": "",
                "domain": "https://cyder.nws.oregonstate.edu/api/v1/dns/domain/1416/",
                "fqdn": "www.emt.orst.edu",
                "id": 1,
                "label": "www",
                "modified": "2013-11-08T18:37:24",
                "target": "www.orst.edu",
                "ttl": 3600,
                "views": [
                    "private",
                    "public"
                ]
            },
            {
                "created": "2013-11-08T18:37:26",
                "description": "",
                "domain": "https://cyder.nws.oregonstate.edu/api/v1/dns/domain/1416/",
                "fqdn": "emt.orst.edu",
                "id": 7,
                "label": "",
                "modified": "2013-11-08T18:37:26",
                "target": "www.orst.edu",
                "ttl": 3600,
                "views": [
                    "private",
                    "public"
                ]
            },
            {
                "created": "2013-11-08T18:37:41",
                "description": "",
                "domain": "https://cyder.nws.oregonstate.edu/api/v1/dns/domain/1611/",
                "fqdn": "cla-dev.cws.oregonstate.edu",
                "id": 40,
                "label": "cla-dev",
                "modified": "2013-11-08T18:37:41",
                "target": "www.orst.edu",
                "ttl": 3600,
                "views": [
                    "private",
                    "public"
                ]
            },
            ...
        ]
    }

Here we can see the first two results are both domains under ``orst.edu``. Let's try filtering them out. We know we don't want any domain including ``orst.edu``, so let's use an exclusion filter to remove any result where the field ``fqdn`` has ``orst.edu`` in it.

.. code::

    curl -H "Authorization: Token MY_TOKEN" "https://cyder.nws.oregonstate.edu/api/v1/dns/cname/?i:target__exact=www.orst.edu&e:fqdn__contains=orst.edu"

.. code:: json

    {
        "count": 184,
        "next": "https://cyder.nws.oregonstate.edu/api/v1/dns/cname/?e%3Afqdn__contains=orst.edu&i%3Atarget__exact=www.orst.edu&page=2",
        "previous": null,
        "results": [
            {
                "created": "2013-11-08T18:37:41",
                "description": "",
                "domain": "https://cyder.nws.oregonstate.edu/api/v1/dns/domain/1611/",
                "fqdn": "cla-dev.cws.oregonstate.edu",
                "id": 40,
                "label": "cla-dev",
                "modified": "2013-11-08T18:37:41",
                "target": "www.orst.edu",
                "ttl": 3600,
                "views": [
                    "private",
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

.. code::

    curl -H "Authorization: Token MY_TOKEN" "https://cyder.nws.oregonstate.edu/api/v1/dns/mx/"

.. code:: json

    {
        "count": 523,
        "next": "https://cyder.nws.oregonstate.edu/api/v1/dns/mx/?page=2",
        "previous": null,
        "results": [
            {
                "created": "2013-11-07T12:48:40",
                "description": "",
                "domain": "https://cyder.nws.oregonstate.edu/api/v1/dns/domain/1167/",
                "fqdn": "rattusdev.nacse.org",
                "id": 2,
                "label": "rattusdev",
                "modified": "2013-11-07T12:48:40",
                "priority": 5,
                "server": "relay.oregonstate.edu",
                "ttl": 86400,
                "views": [
                    "private",
                    "public"
                ]
            },
            ...
        ]
    }

We know that domain records have a ``name`` field containing their FQDN, so we should construct our query to find only MX records attached to the domain ``orst.edu``. Querying fields of related records is easily accomplished by appending two underscores and the name of the field we want to query in the related record. For example, querying the domain name of MX records is accomplished like so:

.. code::

    curl -H "Authorization: Token MY_TOKEN" "https://cyder.nws.oregonstate.edu/api/v1/dns/mx/?i:domain__name__exact=orst.edu"

Now our results look like this:

.. code:: json

    {
        "count": 9,
        "next": "https://cyder.nws.oregonstate.edu/api/v1/dns/mx/?i%3Adomain__name__exact=orst.edu&count=1&page=2",
        "previous": null,
        "results": [
            {
                "created": "2013-11-07T12:56:21",
                "description": "",
                "domain": "https://cyder.nws.oregonstate.edu/api/v1/dns/domain/1411/",
                "fqdn": "exchangemail.orst.edu",
                "id": 126,
                "label": "exchangemail",
                "modified": "2013-11-07T12:56:21",
                "priority": 5,
                "server": "ex1.oregonstate.edu",
                "ttl": 86400,
                "views": [
                    "private",
                    "public"
                ]
            }
        ]
    }

~~~~~~~~~~~~~~~~~~~~~~
Filtering by Container
~~~~~~~~~~~~~~~~~~~~~~
As with the Cyder user interface, the Cyder API allows you to filter results by their associated container. You can filter by the container's name or its ID. For example, if you wanted to find all domains in the container ``nws``, you could pass the query string parameter ``ctnr=nws`` or ``ctnr_id=292`` (assuming 292 is the ID of ``nws`` in your Cyder installation). Note that you can only filter by one container at a time. It is not currently possible to find the intersection of two or more containers.

The endpoint ``/api/v1/core/ctnr/`` is a useful illustration of this feature, because it is used to filter the domains, ranges, users, and workgroups related to each container.

~~~~~~~~~~~~~~~~~~~~~~~
Filtering by Attributes
~~~~~~~~~~~~~~~~~~~~~~~
Many records have attributes associated with them. Specifically, the following records have attributes and attribute filtering enabled:

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

Attribute filtering is very straightforward. **Note: For technical reasons, attribute searching is limited compared to ordinary field searching. Only case insensitive exact matching is allowed for attribute searching.** It is possible to access key-value records directly and perform more complex queries with field lookups, but this doesn't allow you to search for combinations of key-value pairs on the same record without more complex client-side processing.

The basic format of a keyvalue query parameter is as follows:

.. code::

    https://cyder.nws.oregonstate.edu/api/v1/[endpoint]/?a:[attribute+name]=[attribute+value]

As usual, the name and value must be properly URL encoded.

As an example, let's try finding all systems running Linux.

.. code::

    curl -H "Authorization: Token MY_TOKEN" "https://cyder.nws.oregonstate.edu/api/v1/core/system/?a:operating+system=linux"

.. code:: json

    {
        "count": 368,
        "next": "https://cyder.nws.oregonstate.edu/api/v1/core/system/?page=2&a%3AOperating+System=linux",
        "previous": null,
        "results": [
            {
                "created": "2013-11-07T12:48:45",
                "id": 13,
                "modified": "2013-11-07T12:48:45",
                "name": "voledev",
                "systemav_set": [
                    {
                        "attribute": "Hardware type",
                        "id": "https://cyder.nws.oregonstate.edu/api/v1/core/system/attributes/16/",
                        "value": "VM"
                    },
                    {
                        "attribute": "Operating system",
                        "id": "https://cyder.nws.oregonstate.edu/api/v1/core/system/attributes/17/",
                        "value": "Linux"
                    }
                ]
            },
            ...
        ]
    }

This list can be used as is, or it can be further filtered with additional query parameters. For example, we could search for all systems running Linux in the ``nws`` container, or all enabled IPv6 networks on a certain VLAN.

Sorting
-------
By passing a comma separated list of fields in a query parameter named ``sort``, you can sort query results. Sort is descending by default, but ascending sort may be achieved by prepending a dash (`-`) to the field name.

Setting Results Per Page
------------------------
You may set the number of results to display per page by passing a query parameter named ``count`` with the number of records to display (up to a limit of 100).