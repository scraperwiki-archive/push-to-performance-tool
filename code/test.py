#! /usr/bin/env python

import unittest
import mock

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

    def tearDown(self):
        self.patcher.stop()

    def test_requesting_data(self):
        download_data(self.box_url)
        url = '{0}/sql?q=select * from swdata limit 5000 offset 0'.format(self.box_url)
        self.mock_requests_get.assert_called_with(url)

    def test_decoding_requested_data(self):
        self.mock_requests_get.return_value = response = mock.Mock()

        # Tell responseObject.json() what to return
        response.json.return_value = [{1: 2}]

        # Try it out, with our mocked responseObject
        d = download_data(self.box_url)

        self.assertEqual(d, [{1: 2}])

    def test_downloads_multiple_chunks(self):
        self.mock_requests_get.return_value = response = mock.Mock()

        # Tell responseObject.json() to return
        # `first_response` the first time it's called and
        # `second_response` the second time it's called.
        first_response = [{1: 2}] * 5000
        second_response = [{1: 2}]
        response.json.side_effect = Dispenser([first_response, second_response])

        d = download_data(self.box_url)

        url = '{0}/sql?q=select * from swdata limit 5000 offset 5000'.format(self.box_url)
        self.mock_requests_get.assert_called_with(url)

        self.assertEqual(d, [{1: 2}] * 5001)


if __name__ == '__main__':
   unittest.main()
