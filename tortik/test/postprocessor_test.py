#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tornado.web
import tornado.ioloop
from tornado.testing import AsyncHTTPTestCase
from tortik.page import RequestHandler
import tornado.curl_httpclient

def first_postprocessor(handler, data, callback):
    callback(handler, data.replace('Hello,', 'Good'))

def second_postprocessor(handler, data, callback):
    callback(handler, data.replace('Good world', 'Good bye'))

class MainHandler(RequestHandler):
    postprocessors = [
        first_postprocessor,
        second_postprocessor,
    ]
    def get(self):
        self.finish('Hello, world!')

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
        ]

        settings = dict(
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class PostprocessorHTTPTestCase(AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def test_main(self):
        self.http_client.fetch(self.get_url('/'), self.stop)
        response = self.wait()
        self.assertEqual(200, response.code)
        self.assertTrue("Good bye!" in response.body)