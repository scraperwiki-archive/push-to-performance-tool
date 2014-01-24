#! /usr/bin/env python

import datetime
import requests
import sys
import itertools

import scraperwiki.runlog; scraperwiki.runlog.setup()


def main():
    # Get the data from the dataset
    if len(sys.argv) < 2:
        # write error message
        return

    raise RuntimeError("Something went wrong")

    box_url = sys.argv[1]
    data = download_data(box_url)

    from pprint import pprint
    pprint(data)

    # Upload data to performance platform
    result = magic_upload_to_gds(where, data)

    # Write upload date to index
    if result != "all good":
        scraperwiki.status("error", "data failed to upload")


def download_data(box_url):
    all_results = []
    for offset in itertools.count(0, 5000):
        url = '{0}/sql?q=select * from swdata limit 5000 offset {1}'.format(box_url, offset)
        response = requests.get(url)

        try:
            chunk = response.json()
        except:
            return all_results

        if not isinstance(chunk, list):
            chunk = []
        all_results.extend(chunk)
        if len(chunk) < 5000:
            break

    return all_results


if __name__ == '__main__':
   main()
