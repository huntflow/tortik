# -*- coding: utf-8 -*-

import time
import tornado.web
import tornado.ioloop
import tornado.curl_httpclient
from tornado.testing import AsyncHTTPTestCase

from tortik.page import RequestHandler


def first_preprocessor(handler, callback):
    def handle_request(response):
        handler.first = True
        callback()

    http_client = tornado.curl_httpclient.CurlAsyncHTTPClient()
    http_client.fetch(b'https://api.hh.ru/status', handle_request, request_timeout=0.2)


def second_preprocessor(handler, callback):
    def handle_request(response):
        handler.second = True
        callback()

    http_client = tornado.curl_httpclient.CurlAsyncHTTPClient()
    http_client.fetch(b'https://api.hh.ru/status', handle_request, request_timeout=0.2)


def third_preprocessor(handler, callback):
    time.sleep(0.5)
    handler.third = True
    callback()


class MainHandler(RequestHandler):
    preprocessors = [
        first_preprocessor,
        second_preprocessor,
        third_preprocessor
    ]

    def get(self):
        if self.first and self.second and self.third:
            self.complete({'status': 'ok'})
        else:
            raise tornado.web.HTTPError(500)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
        ]

        settings = dict(
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class PreprocessorHTTPTestCase(AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def test_main(self):
        self.http_client.fetch(self.get_url('/'), self.stop)
        response = self.wait()
        self.assertEqual(200, response.code)
        self.assertIn(b'ok', response.body)
