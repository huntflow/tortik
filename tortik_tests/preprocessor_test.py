# -*- coding: utf-8 -*-
import os
import time

import tornado.web
import tornado.ioloop
import tornado.curl_httpclient
from tornado.escape import json_decode
from tornado.testing import AsyncHTTPTestCase

from tortik.page import RequestHandler


def first_preprocessor(handler, callback):
    def handle_request(response):
        handler.first = True
        callback()

    http_client = tornado.curl_httpclient.CurlAsyncHTTPClient()
    http_client.fetch(handler.request.protocol + "://" + handler.request.host + '/mock/json',
                      handle_request, request_timeout=0.2)


def second_preprocessor(handler, callback):
    def handle_request(response):
        handler.second = True
        callback()

    http_client = tornado.curl_httpclient.CurlAsyncHTTPClient()
    http_client.fetch(handler.request.protocol + "://" + handler.request.host + '/mock/json',
                      handle_request, request_timeout=0.2)


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


class MockJsonHandler(tornado.web.RequestHandler):
    @staticmethod
    def mock_data():
        fd = open(os.path.join(os.path.dirname(__file__), 'data', 'simple.json'), 'r')
        data = json_decode(fd.read())
        fd.close()
        return data

    def get(self):
        self.finish(self.mock_data())


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r"/mock/json", MockJsonHandler),
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
