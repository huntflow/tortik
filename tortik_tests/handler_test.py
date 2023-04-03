# -*- coding: utf-8 -*-
import os

import tornado.web
import tornado.ioloop
import tornado.curl_httpclient
from tornado.escape import json_decode
from tornado.testing import AsyncHTTPTestCase, gen_test

from tortik.page import RequestHandler


class MainHandler(RequestHandler):
    @staticmethod
    def mock_data():
        fd = open(os.path.join(os.path.dirname(__file__), "data", "simple.json"), "r")
        data = json_decode(fd.read())
        fd.close()
        return data

    def get(self):
        self.complete(self.mock_data())


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
        ]
        tornado.web.Application.__init__(self, handlers)


class PreprocessorHTTPTestCase(AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    @gen_test
    def test_main(self):
        response = yield self.http_client.fetch(self.get_url("/"))
        self.assertEqual(200, response.code)
        self.assertIn(b"42de59705652efc5306463cafb5db34c", response.body)
