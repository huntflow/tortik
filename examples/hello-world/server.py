#!/usr/bin/env python
# _*_ coding: utf-8 _*_
#
# Usage: see ./server.py --help
#
import sys
from os import path
import urllib

import tornado.web
import tornado.httpclient
from tornado.ioloop import IOLoop
from tornado.options import options

try:
    import tortik
except ImportError:
    sys.path.append(path.abspath(path.join(path.dirname(__file__), '..', '..')))
    import tortik

from tortik.page import RequestHandler
import tortik.logger


def preprocessor(handler, callback):
    def handle_request():
        handler.log.info('Log from preprocessor')
        handler.hello = 'Hello'  # save some data from preprocessor
        callback()

    IOLoop.instance().add_callback(handle_request)  # emulate async call


def postprocessor(handler, data, callback):
    def handle_request():
        handler.log.info('Log from postprocessor')
        added_data = handler.get_data()
        processed_data = map(lambda x: x.get('header_image'), added_data.get('steam', {}).get('large_capsules', []))
        callback(handler, {'images': list(processed_data)})

    IOLoop.instance().add_callback(handle_request)  # emulate async call


class MainHandler(RequestHandler):
    preprocessors = [
        preprocessor
    ]
    postprocessors = [
        postprocessor
    ]

    def get(self):
        self.fetch_requests([
            ('steam', 'http://store.steampowered.com/api/featured/'),
            ('hhapi', 'https://api.hh.ru/dictionaries', {'locale': 'EN'}),
            ('xml', self.request.protocol + "://" + self.request.host + '/mock/xml')
        ], callback=self.complete)


class ExceptionHandler(MainHandler):
    postprocessors = [

    ]

    def get(self):
        test = 1 / 0  # ZeroDivisionError


class MockXmlHandler(tornado.web.RequestHandler):
    @staticmethod
    def mock_data():
        fd = open(path.join(path.dirname(__file__), 'simple.xml'), 'r')
        data = fd.read()
        fd.close()
        return data

    def get(self):
        self.set_header('Content-Type', 'application/xml')
        self.finish(self.mock_data())


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r'/exception', ExceptionHandler),
            (r'/mock/xml', MockXmlHandler),
        ]

        tortik.logger.configure()
        super(Application, self).__init__(handlers)


if __name__ == '__main__':
    # some options & options parsing
    options.define('host', type=str, default='localhost', help='Bind address')
    options.define('port', type=int, default=8888, help='Bind port')
    options.parse_config_file(path.join(path.dirname(__file__), 'options.cfg'), final=False)
    options.parse_command_line()

    # this is how http client could be configured
    tornado.httpclient.AsyncHTTPClient.configure("tornado.simple_httpclient.SimpleAsyncHTTPClient", defaults={
        'user_agent': ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/537.1 (KHTML, like Gecko)"
                       " Chrome/21.0.1180.89 Safari/537.1")
    })

    address = options.host
    port = options.port

    application = Application()
    sys.stderr.write(('Start server at {address}:{port}\n'
                      'See example pages at:\n'
                      '* http://{address}:{port}/\n'
                      '* http://{address}:{port}/?debug{p}\n'
                      '* http://{address}:{port}/exception\n'
                      '* http://{address}:{port}/exception?debug{p}\n'
                      ).format(address=options.host, port=options.port,
                               p=('=' + urllib.quote(options.debug_password)) if options.debug_password else ''))
    application.listen(port, address)

    # start ioloop
    IOLoop.instance().start()
