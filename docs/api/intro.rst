=============================
Introduction to The Cyder API
=============================

:Author: Zane Salvatore
:Version: 0.1 (draft)
:API Version: 1

The Cyder API allows read-only access to DNS records, systems, and static interfaces stored in the database. In the future, it will also provide read-write access to these resources.

This document's examples are written in Python and make use of the urllib2 standard Python library, but anything that can make HTTP requests may also be used, including command line tools.

For readability, API responses in this tutorial will be formatted with linebreaks and indentation. Actual API responses will differ.

Getting Started
===============

This section will lead you through the first steps of using the Cyder API.

Requesting Your API Token
-------------------------

API access is restricted to those with a token. A token is a randomly-generated 40 character hex string that is associated with your username. All API requests must be accompanied by a valid token or the request will be ignored.

Generating your token is simple:

1. Log into Cyder.

2. Go to your user profile (click your username at the top of the screen).

3. Click **Request API Token**.

4. Enter the token's intended purpose.

You will now see a page with your token's key, purpose, and date of creation. From this page you can also revoke your token, should it be compromised or no longer needed.

**Note:** It is strongly recommended that you generate a new key for each application that will be accessing the API.

API Basics
----------

In this section, we'll do a low level overview of the data provided by the API using only Python and the urllib2 library.

First, let's look at a basic function to submit requests to the API:

.. code:: python

    import urllib2
    
    def api_connect(url, token):
        req = urllib2.Request(url)
        req.add_header('HTTP-Accept', 'application/json')
        req.add_header('Authorization', 'Token ' + token)
        return urllib2.urlopen(req).read()

This function illustrates the structure of a very basic request to the Cyder API. It creates a request object, adds the necessary headers, and then returns the response from the server. At a minimum, you must pass headers containing the desired response format (``application/json`` is the only currently supported format, but if you don't send it the server will return an HTML response instead) and your API token. If the API root URL, response format, and a valid token are passed to the function, it returns the following as a string:

.. code:: json

    {
        "staticinterface": "http://127.0.0.1:8000/api/v1/staticinterface/",
        "domain": "http://127.0.0.1:8000/api/v1/domain/",
        "addressrecord": "http://127.0.0.1:8000/api/v1/addressrecord/",
        "system": "http://127.0.0.1:8000/api/v1/system/",
        "mx": "http://127.0.0.1:8000/api/v1/mx/",
        "cname": "http://127.0.0.1:8000/api/v1/cname/",
        "srv": "http://127.0.0.1:8000/api/v1/srv/",
        "nameserver": "http://127.0.0.1:8000/api/v1/nameserver/",
        "txt": "http://127.0.0.1:8000/api/v1/txt/",
        "ptr": "http://127.0.0.1:8000/api/v1/ptr/"
    }

This response contains no information from the database, but it is immediately useful because it provides us with information about the API itself. First, it tells us the types of data that we can access, and second, it tells us where this data can be found. This also shows a common trend in the Cyder API: where appropriate, URLs to related records are provided for ease of navigation. This allows you to traverse relations in the Cyder database without constructing URLs or even knowing the structure of the API in advance.

Let's see what happens when we pass one of these URLs to ``api_connect``.

.. code:: python

    print api_connect("http://127.0.0.1:8000/api/v1/domain/",  "fa4a19797dc9f920c7ae096f4474531c86aaaa0a")

This returns a **list view** of Domain records. List views allow you to navigate through sets of records and are automatically paginated to lessen the load on the server and client. Here is a truncated version of a possible response to the above query:

.. code:: json

    {
        "count": 2068,
        "next": "http://127.0.0.1:8000/api/v1/domain/?page=2",
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
                "master_domain": "http://127.0.0.1:8000/dns/domain/1/",
                "name": "in-addr.arpa",
                "purgeable": false,
                "soa": null
            },
            ...
        ]
    }

There are a few important things to note here:

1. *count*, *next*, and *previous* all provide data that can help simplify API interaction.

   - *count* gives the number of records of the requested type. This makes it easy to iterate through records without making additional requests to check when you've reached the end.
   - *next* and *previous* each contain URLs to the next and previous page of results. These are constructed dynamically by the API, so they will always contain any query parameters you have passed. Because these values will be ``null`` if no such page exists, you can also use them to iterate through multi-page lists of results without having to count. This is also safer than counting, because changes made to the database in the middle of a large batch of API requests may cause there to be fewer pages than there were at the beginning.
   
2. As stated before, where appropriate, related records are pointed to with URLs for easy navigation. In this case, if you wanted to check the master domain of the domain name ``in-addr.arpa``, you could simply pass the value of ``master_domain`` to api_connect and retrieve the appropriate record.

Now we know how to retrieve general lists of objects, but what if we want to access a specific record? Since our previous response contained a URL pointing directly to a record, let's see what happens when we follow that URL.

.. code:: python

    print api_connect("http://127.0.0.1:8000/api/v1/domain/2/",  "fa4a19797dc9f920c7ae096f4474531c86aaaa0a")
    
This returns a **detail view** of the Domain record with an ``id`` of 2. 

    {
        "delegated": false,
        "dirty": false,
        "id": 2,
        "is_reverse": true,
        "master_domain": "http://127.0.0.1:8000/dns/domain/1/",
        "name": "in-addr.arpa",
        "purgeable": false,
        "soa": null
    }

[Put some stuff about the response and detail views here.]

Domain records are simple, but some objects, such as Static Interfaces, are more complex. In addition to a variety of predefined fields, Static Interface records can have user defined key-value pairs 