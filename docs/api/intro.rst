=============================
Introduction to The Cyder API
=============================

:Author: Zane Salvatore
:Version: 0.1 (draft)
:API Version: 1

The Cyder API allows read-only access to DNS records and static interfaces stored in the database. In the future, it will also provide read-write access to these resources.

This document's examples are written in Python and make use of the urllib2 library, but any language and library that can make HTTP requests may also be used.

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

Accessing the API
-----------------

To begin with, let's do a simple example.

.. code:: python

    import urllib2
    
    def api_connect(token):
        req = urllib2.Request("http://127.0.0.1:8000/api/v1/")
        req.add_header('HTTP-Accept', 'application/json')
        req.add_header('Authorization', 'Token ' + token)
        return urllib2.urlopen(req).read()

This function illustrates a very basic request to the Cyder API. It creates a request object, adds the necessary headers, and then returns the response from the server. If a valid token is passed to the function, it returns the following:

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

