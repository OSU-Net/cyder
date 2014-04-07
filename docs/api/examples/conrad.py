import json
import urllib
import urllib2
from time import sleep


def error(m):
    """
    Print the error in red so the user knows it's important. :)
    """
    print "\x1b[91m" + m + "\x1b[0m"


class Conrad(object):
    """
    Basic class for getting data from the Cyder API. This should work with API
    v1, but compatibility is not guaranteed.
    """
    def __init__(self, token, base_url):
        """
        Params:
          - token       The API token to authenticate with.
          - base_url    The url to prepend to each request. Use a consistent
                        scheme of trailing or leading slashes.
        """
        self.token = token
        self.base_url = base_url
        self.result_str = None  # holds the last result as a string
        self.result = None  # if result_str contains a valid JSON object,
                            # this contains a deserialized representation of
                            # that object
        self.num_results = None
        self.response_code = None  # holds the last request's response code
        self.exception = None  # contains last exception raised
        self.prev_url = None
        self.next_url = None

    def get(self, path, query=None, verbatim=False):
        """
        Params:
        path    The specific path to access under self.base_url. May or
                may not need a leading slash depending on the value of
                base_url.
        query   A dict or string of GET parameters.
        verbatim    Whether or not to treat path as the entire URL.

        Returns the deserialized output of the API if succeessful or False if
        unsuccessful.
        """

        if query:
            if isinstance(query, dict):
                query = urllib.urlencode(query)

            query = "&" + query
        else:
            query = ""

        if verbatim:
            url = path
        else:
            url = self.base_url + path + '?count=100' + query

        req = urllib2.Request(url)
        req.add_header('Authorization', 'Token ' + self.token)

        resp = urllib2.urlopen(req)

        self.result_str = resp.read()
        self.response_code = resp.code

        result = json.loads(self.result_str)

        self.result = result['results']
        self.prev_url = result['previous']
        self.next_url = result['next']
        self.num_results = long(result['count'])

        sleep(0.1)  # sleep to avoid overwhelming the server
        return self.result

    def get_next(self):
        if self.next_url is None:
            return False
        return self.get(self.next_url, verbatim=True)

    def get_prev(self):
        if self.prev_url is None:
            return False
        return self.get(self.prev_url, verbatim=True)