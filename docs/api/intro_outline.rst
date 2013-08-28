=============================
Introduction to The Cyder API
=============================


:Version: 0.1 (draft)
:API Version: 1

.. contents:: 

Introduction to the Cyder API
=============================
The Cyder API currently allows read-only access to DNS records, systems, and static interfaces stored in the database. In the future, it will also provide read-write access to these resources.

This document's examples are written in Python, using version 2.7.4, and make use of the urllib_ and urllib2_ standard Python libraries, but anything that can make HTTP requests may also be used. While this tutorial is fairly elementary, some understanding of urllib2 is expected. You may want to read the Python HOWTO `"Fetch Internet Resources Using urllib2"`_ before starting this tutorial.

.. _urllib: http://docs.python.org/2/library/urllib.html
.. _urllib2: http://docs.python.org/2/library/urllib2.html
.. _"Fetch Internet Resources Using urllib2": http://docs.python.org/2/howto/urllib2.html

For readability, all API responses in this tutorial will be formatted with linebreaks and indentation, and some may be abbreviated. Actual API responses may differ.

Through this tutorial, the placeholder ``MY_TOKEN`` will be used instead of an actual API token. Anywhere you see ``MY_TOKEN`` used, you should replace it with your own token.

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


Getting Started
===============
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

Request Objects
~~~~~~~~~~~~~~~

API Root View
~~~~~~~~~~~~~

List Views
~~~~~~~~~~

Detail Views
~~~~~~~~~~~~

Diving In
=========
This section covers more advanced API topics. You'll learn how to filter results, [AND DO OTHER THINGS TOO, I SWEAR. I JUST HAVE TO FIGURE OUT WHAT THEY ARE.]

Filtering
---------

Filtering by Fields
~~~~~~~~~~~~~~~~~~~

Inclusive Filters
~~~~~~~~~~~~~~~~~

Exclusive Filters
~~~~~~~~~~~~~~~~~

Filtering by Container
~~~~~~~~~~~~~~~~~~~~~~

Filtering by Key~Values
~~~~~~~~~~~~~~~~~~~~~~~