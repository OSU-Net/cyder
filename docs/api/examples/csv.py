import argparse
import itertools
import sys

from conrad import Conrad


API_TOKEN = "3488d442b17d7e3c8d55f3ed60c660cface5d9ab"
BASE_URL = "http://127.0.0.1:8000/api/v1/"

HOSTS = {"path": "core/system", "attributes": []}


def api_get_csv(path, fields=None, params=None, attributes=None, separator=";",
                limit=None):
    """
    Params:
      - path    The specific path to access.
      - fields  The fields to export as CSV. This field is optional, but not
                passing it may lead to strange results.
      - params  Any query string parameters to pass with the request, stored as
                a dict.
      - attributes  Attributes to retrieve the values of.
      - separator   The character to separate values with. Set to ';' by
                    default.

    Return:
        The results of the API request serialized in a CSV format.
    """

    c = Conrad(API_TOKEN, BASE_URL)

    c.get(path, params)

    if fields is None:
        # Assume that the top-level fields are the same for every record.
        fields = c.result[0].keys()

    # Build the header row.
    csv = separator.join(fields)
    if attributes:
        csv += (separator + separator.join(attributes))
    csv += "\n"

    num_results = 0

    while True:
        for record in c.result:
            for field in fields:
                csv += (str(record[field]) + separator)

            if attributes:
                keyvalues = record[
                    next(itertools.ifilter(lambda x: x.endswith("av_set"),
                                           record),
                         None)]

                for attribute in attributes:
                    for kv in keyvalues:
                        if kv['attribute'] == attribute:
                            csv += (str(kv['value']) + separator)
                            break
                    else:
                        # Not found, but we still want a blank cell where the
                        # value would be.
                        csv += separator

            sys.stdout.write(csv + '\n')
            csv = ""
            num_results += 1
            if limit and num_results >= limit:
                break

        if limit and num_results >= limit:
            break

        if not c.get_next():
            break


def main():
    parser = argparse.ArgumentParser(description="Retrieve data from the Cyder "
                                                 "API and serialize it in CSV "
                                                 "format.")
    parser.add_argument('path', type=str, help="The URL under the API to "
                                               "access.")
    parser.add_argument('--fields', '-f', type=str,
                        help="A comma-separated list of fields to access.")
    parser.add_argument('--attributes', '-a', type=str,
                        help="A comma-separated list of attributes to "
                             "retrieve.")
    parser.add_argument('--params', '-p', type=str,
                        help="Query string parameters to submit with the "
                             "request, in query string format.")
    parser.add_argument('--separator', '-s', type=str, default=';',
                        help="The character to separate values with.")
    parser.add_argument('--limit', '-l', type=int,
                        help="The number of records to retrieve before "
                             "stopping.")

    args = parser.parse_args()

    if args.attributes:
        args.attributes = args.attributes.split(',')

    #sys.stdout.write(api_get_csv(args.path, fields=args.fields,
    #                             params=args.params, attributes=args.attributes,
    #                             separator=args.separator, limit=args.limit))
    api_get_csv(**vars(args))

if __name__ == "__main__":
    main()