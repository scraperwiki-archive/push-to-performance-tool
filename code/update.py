#! /usr/bin/env python

import datetime
import requests
import sys
import itertools
import json

from backdrop.collector.write import Bucket
from backdrop.collector.write import JsonEncoder

from dshelpers import batch_processor

import scraperwiki.runlog; scraperwiki.runlog.setup()


def main():
    if len(sys.argv) < 2:
        scraperwiki.sql.save([], {
            "date": datetime.datetime.now(),
            "status": "error",
            "rows_pushed": 0,
            "message": "No source dataset URL was supplied"
        })
        return

    box_url = sys.argv[1]
    url, token = read_settings()

    if url and token:

        # Get data from source dataset
        data = download_data(box_url)

        # Upload data to performance platform
        log = push_data(url, token, data)

        scraperwiki.sql.save([], log)


def read_settings():
    with open('../http/allSettings.json') as file:
        settings = json.loads(file.read())
        return (settings['url'], settings['token'])


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
