#! /usr/bin/env python

import unittest
import mock

# for testing JSONDecodeErrors
# from requests.json()
import simplejson

# The functions we want to test
# are in ./update.py
from update import download_data


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

if __name__ == '__main__':
   unittest.main()
