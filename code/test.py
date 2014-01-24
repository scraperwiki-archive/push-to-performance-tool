#! /usr/bin/env python

import unittest
import mock
import datetime

# for testing JSONDecodeErrors
# from requests.json()
import simplejson

# The functions we want to test
# are in ./update.py
from update import download_data, push_data


# This gets used in our tests to fake some API calls
class Dispenser(object):
    def __init__(self, items):
        self.items = items

    def __call__(self, *args, **kwargs):
        return self.items.pop(0)


class TestDataDownloader(unittest.TestCase):
    def setUp(self):
        self.box_url = 'http://example.com/foo/bar'
        self.patcher = mock.patch('requests.get')
        self.mock_requests_get = self.patcher.start()
        self.mock_requests_get.return_value = self.mock_response = mock.MagicMock()

    def tearDown(self):
        self.patcher.stop()

    def test_requesting_data(self):
        download_data(self.box_url)
        url = '{0}/sql?q=select * from swdata limit 5000 offset 0'.format(self.box_url)
        self.mock_requests_get.assert_called_with(url)

    def test_decoding_requested_data(self):
        # Tell responseObject.json() what to return
        self.mock_response.json.return_value = [{1: 2}]

        # Try it out, with our mocked responseObject
        d = download_data(self.box_url)

        self.assertEqual(d, [{1: 2}])

    def test_downloads_multiple_chunks(self):
        # Tell responseObject.json() to return
        # `first_response` the first time it's called and
        # `second_response` the second time it's called.
        first_response = [{1: 2}] * 5000
        second_response = [{1: 2}]
        self.mock_response.json.side_effect = Dispenser([first_response, second_response])

        d = download_data(self.box_url)

        url = '{0}/sql?q=select * from swdata limit 5000 offset 5000'.format(self.box_url)
        self.mock_requests_get.assert_called_with(url)

        self.assertEqual(d, [{1: 2}] * 5001)

    def test_missing_database(self):
        self.mock_response.json.return_value = {'error': ''}

        d = download_data(self.box_url)

        self.assertEqual(d, [])

    def test_missing_table(self):
        self.mock_response.json.return_value = 'Could not find table swdata'

        d = download_data(self.box_url)

        self.assertEqual(d, [])

    def test_empty_table(self):
        self.mock_response.json.return_value = []

        d = download_data(self.box_url)

        self.assertEqual(d, [])

    def test_non_json_response(self):
        self.mock_response.json.side_effect = simplejson.decoder.JSONDecodeError('', '', 0)

        d = download_data(self.box_url)

        self.assertEqual(d, [])

    def test_http_error_status(self):
        self.mock_response.ok = False
        self.mock_response.json.return_value = [{1: 2}]

        d = download_data(self.box_url)

        self.assertEqual(d, [])


class TestDataPusher(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('update.Bucket')
    def test_bucket_is_created_with_url_and_token(self, Bucket):
        url = 'http://performance.example.com'
        token = '6c32941c-7ce3-4d87-8f20-7598605c6142'
        data = [{1: 2}]

        push_data(url, token, data)

        Bucket.assert_called_with(url, token)

    @mock.patch('update.Bucket')
    def test_empty_data_is_not_posted(self, Bucket):
        url = 'http://performance.example.com'
        token = '6c32941c-7ce3-4d87-8f20-7598605c6142'
        data = []

        push_data(url, token, data)

        self.assertFalse(Bucket().post.called)

    @mock.patch('update.Bucket')
    def test_data_is_posted(self, Bucket):
        url = 'http://performance.example.com'
        token = '6c32941c-7ce3-4d87-8f20-7598605c6142'
        data = [{1: 2}]

        push_data(url, token, data)

        Bucket().post.assert_called_with(data)

    @mock.patch('update.Bucket')
    def test_data_is_posted_in_chunks(self, Bucket):
        url = 'http://performance.example.com'
        token = '6c32941c-7ce3-4d87-8f20-7598605c6142'
        data = [{1: 2}] * 2001

        push_data(url, token, data)

        p = Bucket().post

        self.assertEquals(p.call_count, 2)
        p.assert_any_call([{1: 2}] * 2000)
        p.assert_any_call([{1: 2}])

    @mock.patch('update.Bucket')
    def test_successful_runs_are_logged(self, Bucket):
        url = 'http://performance.example.com'
        token = '6c32941c-7ce3-4d87-8f20-7598605c6142'
        data = [{1: 2}]

        log = push_data(url, token, data)

        self.assertEquals(log['status'], 'success')
        self.assertEquals(log['rows_pushed'], 1)
        self.assertEquals(log['message'], None)
        self.assertIsInstance(log['date'], datetime.datetime)

    @mock.patch('update.Bucket')
    def test_empty_data_is_logged(self, Bucket):
        url = 'http://performance.example.com'
        token = '6c32941c-7ce3-4d87-8f20-7598605c6142'
        data = []

        log = push_data(url, token, data)

        self.assertEquals(log['status'], 'error')
        self.assertEquals(log['rows_pushed'], 0)
        self.assertEquals(log['message'], 'No rows in source dataset')
        self.assertIsInstance(log['date'], datetime.datetime)


if __name__ == '__main__':
   unittest.main()
