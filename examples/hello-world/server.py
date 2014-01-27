#!/usr/bin/env python
# _*_ coding: utf-8 _*_
#
# Usage: see ./server.py --help
#
import sys
from os import path
import urllib

import tornado.web
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
        processed_data = data.replace('Good buy', '{} world'.format(handler.hello))  # postprocess results
        callback(handler, processed_data)

    IOLoop.instance().add_callback(handle_request)  # emulate async call


class MainHandler(RequestHandler):

    hello = None

    preprocessors = [
        preprocessor
    ]
    postprocessors = [
        postprocessor
    ]

    def get(self):
        self.complete('Good buy!')


class ExceptionHandler(MainHandler):
    def get(self):
        test = 1 / 0  # ZeroDivisionError


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r'/exception', ExceptionHandler),
        ]

        tortik.logger.configure()
        super(Application, self).__init__(handlers)


if __name__ == '__main__':
    # some options & options parsing
    options.define('host', type=str, default='localhost', help='Bind address')
    options.define('port', type=int, default=8888, help='Bind port')
    options.parse_config_file(path.join(path.dirname(__file__), 'options.cfg'), final=False)
    options.parse_command_line()

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
