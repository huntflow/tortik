# -*- coding: utf-8 -*-
import tornado.web
import tornado.ioloop
import tornado.curl_httpclient
from tornado.testing import AsyncHTTPTestCase

from tortik.page import RequestHandler


def preprocessor(handler, callback):
    callback(1 / 0)


def check_postprocessor(handler, data, callback):
    handler.set_status(200)
    callback(handler, data)


def postprocessor(handler, data, callback):
    callback(handler, 1 / 0)


class MainHandler(RequestHandler):
    preprocessors = [preprocessor]
    postprocessors = [check_postprocessor]

    def get(self):
        self.complete({"status": "ok"})


class SecondHandler(RequestHandler):
    postprocessors = [postprocessor]

    def get(self):
        self.complete({"status": "ok"})


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/second", SecondHandler),
        ]

        settings = dict(
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class ExceptionsHTTPTestCase(AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def test_main(self):
        self.http_client.fetch(self.get_url("/"), self.stop)
        response = self.wait()
        self.assertEqual(500, response.code)

    def test_second(self):
        self.http_client.fetch(self.get_url("/second"), self.stop)
        response = self.wait()
        self.assertEqual(500, response.code)
