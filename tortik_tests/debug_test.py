# -*- coding: utf-8 -*-

import tornado.web
import tornado.ioloop
from tornado.testing import AsyncHTTPTestCase
from tornado.options import options

from tortik.page import RequestHandler
import tortik.logger


def preprocessor(handler, callback):
    def handle_request():
        handler.log.info('Log from preprocessor')
        callback()

    handler.fetch_requests(
        handler.make_request(
            name='status',
            method='GET',
            full_url='https://api.hh.ru/status',
            request_timeout=0.2
        ),
        callback=handle_request
    )


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


class ExceptionHandler(MainHandler):
    def get(self):
        test = 1 / 0
        self.complete('Hello, world!')


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/exception", ExceptionHandler),
        ]

        settings = dict(
            debug=options.debug,
        )
        tortik.logger.configure()
        tornado.web.Application.__init__(self, handlers, **settings)


class DebugHTTPTestCase(AsyncHTTPTestCase):
    def setUp(self):
        self._old_debug = options.debug
        self._old_debug_password = options.debug_password
        options.debug = True
        options.debug_password = ''

        super(DebugHTTPTestCase, self).setUp()

    def tearDown(self):
        options.debug = self._old_debug
        options.debug_password = self._old_debug_password
        super(DebugHTTPTestCase, self).tearDown()

    def get_app(self):
        return Application()

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def test_main(self):
        self.http_client.fetch(self.get_url('/?debug'), self.stop)
        response = self.wait()
        self.assertEqual(200, response.code)
        self.assertIn(b'Log from preprocessor', response.body)
        self.assertIn(b'Log from postprocessor', response.body)
        self.assertIn(b'https://api.hh.ru/status', response.body)

    def test_exception(self):
        self.http_client.fetch(self.get_url('/exception'), self.stop)
        response = self.wait()
        self.assertEqual(500, response.code)
        self.assertIn(b'Log from preprocessor', response.body)
        self.assertNotIn(b'Log from postprocessor', response.body)
        self.assertIn(b'https://api.hh.ru/status', response.body)
        self.assertIn(b'ZeroDivisionError', response.body)

    def test_debug_exception(self):
        self.http_client.fetch(self.get_url('/exception?debug'), self.stop)
        response = self.wait()
        self.assertEqual(200, response.code)
        self.assertIn(b'code=500', response.body)
        self.assertIn(b'ZeroDivisionError', response.body)


class DebugPasswordHTTPTestCase(AsyncHTTPTestCase):
    def setUp(self):
        self._old_debug = options.debug
        self._old_debug_password = options.debug_password
        options.debug = False
        options.debug_password = '123'

        super(DebugPasswordHTTPTestCase, self).setUp()

    def tearDown(self):
        options.debug = self._old_debug
        options.debug_password = self._old_debug_password
        super(DebugPasswordHTTPTestCase, self).tearDown()

    def get_app(self):
        return Application()

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def test_debug_false(self):
        self.http_client.fetch(self.get_url('/?debug'), self.stop)
        response = self.wait()
        self.assertEqual(200, response.code)
        self.assertNotIn(b'Log from preprocessor', response.body)
        self.assertNotIn(b'Log from postprocessor', response.body)
        self.assertNotIn(b'https://api.hh.ru/status', response.body)
        self.assertIn(b'Hello, world!', response.body)

    def test_debug_true(self):
        self.http_client.fetch(self.get_url('/?debug=123'), self.stop)
        response = self.wait()
        self.assertEqual(200, response.code)
        self.assertIn(b'Log from preprocessor', response.body)
        self.assertIn(b'Log from postprocessor', response.body)
        self.assertIn(b'https://api.hh.ru/status', response.body)

    def test_exception(self):
        self.http_client.fetch(self.get_url('/exception'), self.stop)
        response = self.wait()
        self.assertEqual(500, response.code)
        self.assertNotIn(b'Log from preprocessor', response.body)
        self.assertNotIn(b'Log from postprocessor', response.body)
        self.assertNotIn(b'https://api.hh.ru/status', response.body)
        self.assertNotIn(b'Hello, world!', response.body)

    def test_debug_exception(self):
        self.http_client.fetch(self.get_url('/exception?debug=123'), self.stop)
        response = self.wait()
        self.assertEqual(200, response.code)
        self.assertIn(b'code=500', response.body)
        self.assertIn(b'ZeroDivisionError', response.body)


class DebugTurnedOffHTTPTestCase(AsyncHTTPTestCase):
    def setUp(self):
        self._old_debug = options.debug
        options.debug = False
        super(DebugTurnedOffHTTPTestCase, self).setUp()

    def tearDown(self):
        options.debug = self._old_debug
        super(DebugTurnedOffHTTPTestCase, self).tearDown()

    def get_app(self):
        return Application()

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def test_debug(self):
        self.http_client.fetch(self.get_url('/?debug'), self.stop)
        response = self.wait()
        self.assertEqual(200, response.code)
        self.assertNotIn(b'Log from preprocessor', response.body)
        self.assertNotIn(b'Log from postprocessor', response.body)
        self.assertNotIn(b'https://api.hh.ru/status', response.body)
        self.assertIn(b'Hello, world!', response.body)

    def test_debug_exception(self):
        self.http_client.fetch(self.get_url('/exception'), self.stop)
        response = self.wait()
        self.assertEqual(500, response.code)
        self.assertNotIn(b'Log from preprocessor', response.body)
        self.assertNotIn(b'Log from postprocessor', response.body)
        self.assertNotIn(b'https://api.hh.ru/status', response.body)
        self.assertNotIn(b'Hello, world!', response.body)
