# _*_ coding: utf-8 _*_

from unittest import TestCase

from tortik.page import RequestHandler

fake_real_ip = '127.5.5.5'
fake_request_id = 'abcdef1234567890'


class FakeRequest(object):
    headers = {}


# py2 to py3
_base_make_request = RequestHandler.make_request
_make_request = _base_make_request.im_func if hasattr(_base_make_request, 'im_func') else _base_make_request


class FakeHandler(object):
    def __init__(self):
        self.request = FakeRequest()
        self.request_id = fake_request_id
        self.request.headers = {
            "X-Real-Ip": fake_real_ip
        }

    make_request = _make_request


class MakeRequestTestCase(TestCase):

    def setUp(self):
        self.fake_handler = FakeHandler()
        self.fake_real_ip = fake_real_ip

    def test_full_url(self):
        full_url = 'http://example.com/path_to'
        request = self.fake_handler.make_request(name='abc', method='GET', full_url=full_url)

        self.assertEqual(request.url, full_url)

    def test_full_url_add_query(self):
        full_url = 'http://example.com/path_to'
        request = self.fake_handler.make_request(name='abc', method='GET', full_url=full_url,
                                                 data={'foo': 1})

        self.assertEqual(request.url, full_url+'?foo=1')

    def test_full_url_update_query(self):
        full_url = 'http://example.com/path_to?bar=2'
        request = self.fake_handler.make_request(name='abc', method='GET', full_url=full_url,
                                                 data={'foo': 1})
        self.assertEqual(
            sorted('bar=2&foo=1'.split('&')),
            sorted(request.url.split('?')[1].split('&'))
        )

    def test_full_url_update_same_query(self):
        full_url = 'http://example.com/path_to?bar=2&bar=3'
        request = self.fake_handler.make_request(name='abc', method='GET', full_url=full_url,
                                                 data={'bar': [4, 5]})
        self.assertEqual(
            sorted('bar=4&bar=5'.split('&')),
            sorted(request.url.split('?')[1].split('&'))
        )

    def test_full_url_query(self):
        full_url = 'http://example.com/path_to?foo=1'
        request = self.fake_handler.make_request(name='abc', method='GET', full_url=full_url)
        self.assertEqual(request.url, full_url)

    def test_url_prefix_and_path(self):
        url_prefix = 'example.com/path_to'
        path = 'some/path/to/resource'
        request = self.fake_handler.make_request(
            name='abc',
            method='GET',
            url_prefix=url_prefix,
            path=path)

        self.assertEqual(request.url, 'http://{0}/{1}'.format(url_prefix, path))

    def test_url_prefix_without_path(self):
        url_prefix = 'example.com/path_to'
        request = self.fake_handler.make_request(
            name='abc',
            method='GET',
            url_prefix=url_prefix)

        self.assertEqual(request.url, 'http://{0}'.format(url_prefix))

    def test_url_args_conflict(self):
        with self.assertRaises(TypeError):
            self.fake_handler.make_request(
                name='abc',
                method='GET',
                url_prefix='example.com/path',
                full_url='http://ex.com')

    def test_empty_kwargs(self):
        with self.assertRaises(TypeError):
            self.fake_handler.make_request('abc', 'GET')

    def test_unused_path_argument(self):
        with self.assertRaises(TypeError):
            self.fake_handler.make_request(
                name='abc',
                method='GET',
                path='/path/to/resource',
                full_url='http://ex.com')

    def test_post_full_query(self):
        full_url = 'http://example.com/path_to?foo=1'
        request = self.fake_handler.make_request(name='abc', method='POST', full_url=full_url, data={'bar': 2})
        self.assertEqual(request.url, full_url)
        self.assertEqual(request.body, b'bar=2')

    def test_post_full_query_raw(self):
        full_url = 'http://example.com/path_to?foo=1'
        data = b'{"json":true}'
        request = self.fake_handler.make_request(name='abc', method='POST', full_url=full_url, data=data)
        self.assertEqual(request.url, full_url)
        self.assertEqual(request.body, data)

    def test_post_query(self):
        url_prefix = 'example.com'
        path = '/path/to'
        request = self.fake_handler.make_request(
            name='abc',
            method='POST',
            url_prefix=url_prefix,
            path=path,
            data={'bar': 2}
        )
        self.assertEqual(request.url, 'http://' + url_prefix + path)
        self.assertEqual(request.body, b'bar=2')
