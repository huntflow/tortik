# -*- coding: utf-8 -*-
import tornado.web
import tornado.ioloop
from tornado.testing import AsyncHTTPTestCase
from tortik.page import RequestHandler
import tornado.curl_httpclient
import tortik.logger


def preprocessor(handler, callback):
    def handle_request(response):
        handler.log.info('Log from preprocessor')
        callback()

    http_client = tornado.curl_httpclient.CurlAsyncHTTPClient()
    http_client.fetch("https://api.hh.ru/status", handle_request, request_timeout=0.2)


def postprocessor(handler, data, callback):
    handler.log.info('Log from postprocessor')
    callback(handler, data)


class MainHandler(RequestHandler):
    preprocessors = [
        preprocessor
    ]
    postprocessors = [
        postprocessor
    ]

    def get(self):
        self.complete('Hello, world!')


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
        ]

        settings = dict(
            debug=True,
        )

        tortik.logger.configure()
        tornado.web.Application.__init__(self, handlers, **settings)


class DebugHTTPTestCase(AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def test_main(self):
        self.http_client.fetch(self.get_url('/?debug'), self.stop)
        response = self.wait()
        self.assertEqual(200, response.code)
        self.assertTrue("Log from preprocessor" in response.body)
        self.assertTrue("Log from postprocessor" in response.body)
