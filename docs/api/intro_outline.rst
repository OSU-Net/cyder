=============================
Introduction to The Cyder API
=============================


:Version: 0.1 (draft)
:API Version: 1

.. contents:: 

-----------------------------
Introduction to the Cyder API
-----------------------------
The Cyder API currently allows read-only access to DNS records, systems, and static interfaces stored in the database. In the future, it will also provide read-write access to these resources.

This document's examples are written in Python, using version 2.7.4, and make use of the urllib_ and urllib2_ standard Python libraries, but anything that can make HTTP requests may also be used. While this tutorial is fairly elementary, some understanding of urllib2 is expected. You may want to read the Python HOWTO `"Fetch Internet Resources Using urllib2"`_ before starting this tutorial.

.. _urllib: http://docs.python.org/2/library/urllib.html
.. _urllib2: http://docs.python.org/2/library/urllib2.html
.. _"Fetch Internet Resources Using urllib2": http://docs.python.org/2/howto/urllib2.html

For readability, all API responses in this tutorial will be formatted with linebreaks and indentation, and some may be abbreviated. Actual API responses may differ.

Through this tutorial, the placeholder ``MY_TOKEN`` will be used instead of an actual API token. Anywhere you see ``MY_TOKEN`` used, you should replace it with your own token.

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
        "core/system": "http://127.0.0.1:8000/api/v1/core/system/",
        "core/system/keyvalues": "http://127.0.0.1:8000/api/v1/core/system/keyvalues/",
        "dhcp/dynamic_interface": "http://127.0.0.1:8000/api/v1/dhcp/dynamic_interface/",
        "dhcp/dynamic_interface/keyvalues": "http://127.0.0.1:8000/api/v1/dhcp/dynamic_interface/keyvalues/",
        "dhcp/static_interface": "http://127.0.0.1:8000/api/v1/dhcp/static_interface/",
        "dhcp/static_interface/keyvalues": "http://127.0.0.1:8000/api/v1/dhcp/static_interface/keyvalues/",
        "dns/address_record": "http://127.0.0.1:8000/api/v1/dns/address_record/",
        "dns/cname": "http://127.0.0.1:8000/api/v1/dns/cname/",
        "dns/domain": "http://127.0.0.1:8000/api/v1/dns/domain/",
        "dns/mx": "http://127.0.0.1:8000/api/v1/dns/mx/",
        "dns/nameserver": "http://127.0.0.1:8000/api/v1/dns/nameserver/",
        "dns/ptr": "http://127.0.0.1:8000/api/v1/dns/ptr/",
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
This section covers more advanced API topics. You'll learn how to filter results, [AND DO OTHER THINGS TOO, I SWEAR. I JUST HAVE TO FIGURE OUT WHAT THEY ARE.]

Filtering
---------
Most of the time, you will be using the API to find records matching different search queries. The Cyder API has very powerful search functionality that allows you to query the database by passing your search parameters in the query string. Here's an updated version of our ``api_connect`` function with added support for query parameters:

.. code:: python

    import urllib
    import urllib2
    
    def api_connect(url, token, params=None):
        if params:
            url += urllib.urlencode(params)
        req = urllib2.Request(url)
        req.add_header('Authorization', 'Token ' + token)
        return urllib2.urlopen(req).read()

This function is very simple and doesn't support adding query parameters to a URL which already has them, but it is sufficient for our purposes.

~~~~~~~~~~~~~~~~~~~
Filtering by Fields
~~~~~~~~~~~~~~~~~~~
Let's say we want to query for every CNAME that aliases a non ``orst.edu`` domain to ``www.orst.edu``. First, we need to determine the structure of CNAME records, so let's look at the CNAME list view.

.. code:: python

    print api_connect("http://127.0.0.1:8000/api/v1/cname/", MY_TOKEN)
    
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

    mode         = "i_" | "e_"
    
    field        = ? any valid field name ?
    
    field lookup = "exact" | "iexact" | "contains" | "icontains" | "gt"
                 | "gte" | "lt" | "lte" | "startswith" | "istartswith"
                 | "endswith" | "iendswith" | "isnull" | "search"

    filter       = mode, "_", field, "__", field lookup

Here, ``mode`` sets whether records matching the query should be included (``i_``) or excluded (``e_``). ``field`` must contain the name of a field in the record, including related fields. ``field lookup`` is used to decide how records should be matched. Each of the supported query types is described in Django's `field lookups reference`_. Note that the field lookups ``in``, ``range``, ``year``, ``month``, ``day``, ``week_day``, ``regex``, and ``iregex`` are not supported.

.. _field lookups reference: https://docs.djangoproject.com/en/1.5/ref/models/querysets/#field-lookups

Multiple filters can be combined in a single query to further refine the results.

With this basic format, let's write our query. Remember, we want every CNAME that aliases a non ``orst.edu`` domain to ``www.orst.edu``. This means that we want all records where ``target`` equals ``www.orst.edu``, but where ``fqdn`` doesn't contain ``orst.edu``. First, let's only retrieve results matching the first critera, so we have a baseline to compare our results against.

.. code:: python

    filter = {'i_target__exact': 'www.orst.edu'}
    print api_connect("http://127.0.0.1:8000/api/v1/cname/", MY_TOKEN, filter)
    
.. code:: json

    {
        "count": 233,
        "next": "http://127.0.0.1:8000/api/v1/cname/?i_target__exact=www.orst.edu&page=2",
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

Here we can see the first two results are both domains under ``orst.edu``. Let's try filtering them out.

.. code:: python

    filter = {'i_target__exact': 'www.orst.edu', 'e_fqdn__contains': 'orst.edu'}
    print api_connect("http://127.0.0.1:8000/api/v1/cname/", MY_TOKEN, filter)

.. code:: json

    {
        "count": 182,
        "next": "http://127.0.0.1:8000/api/v1/cname/?i_target__exact=www.orst.edu&e_fqdn__contains=orst.edu&page=2",
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
Basic queries are not only limited to top-level fields. As you may have noticed in the previous example, CNAME records (and others) have a field titled ``views`` which has its contents enclosed with brackets.

~~~~~~~~~~~~~~~~~~~~~~
Filtering by Container
~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~
Filtering by Key-Values
~~~~~~~~~~~~~~~~~~~~~~~