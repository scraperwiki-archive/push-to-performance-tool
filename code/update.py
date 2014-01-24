#! /usr/bin/env python

import datetime
import requests
import sys
import itertools

from backdrop.collector.write import Bucket
from backdrop.collector.write import JsonEncoder

from dshelpers import batch_processor

import scraperwiki.runlog; scraperwiki.runlog.setup()


def main():
    # Get the data from the dataset
    if len(sys.argv) < 2:
        # write error message
        return

    box_url = sys.argv[1]
    data = download_data(box_url)

    url = 'http://performance.example.com'
    token = '6c32941c-7ce3-4d87-8f20-7598605c6142'

    # Upload data to performance platform
    log = push_data(url, token, data)

    scraperwiki.sql.save([], log)


def download_data(box_url):
    all_results = []
    for offset in itertools.count(0, 5000):
        url = '{0}/sql?q=select * from swdata limit 5000 offset {1}'.format(box_url, offset)
        response = requests.get(url)

        if not response.ok:
            return all_results

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


def push_data(url, token, data):
    num_rows = len(data)
    if num_rows:
        bucket = Bucket(url, token)
        with batch_processor(bucket.post) as uploader:
            for row in data:
                uploader.push(row)
        return {
            "date": datetime.datetime.now(),
            "status": "success",
            "rows_pushed": num_rows,
            "message": None
        }
    else:
        return {
            "date": datetime.datetime.now(),
            "status": "error",
            "rows_pushed": 0,
            "message": "No rows in source dataset"
        }


if __name__ == '__main__':
   main()
