# -*- coding: utf-8 -*-
import logging

import tornado.web
from tornado.options import options

import tornado_util.server
from tortik.page import RequestHandler
from tortik.logger import configure as configure_logging


def main(app, config_file="tortik_dev.cfg"):
    tornado_util.server.bootstrap(config_file=config_file)

    logging.getLogger("tortik").info('Use config: {0}'.format(config_file))

    configure_logging(options.logfile)
    tornado_util.server.main(app)

class MainHandler(RequestHandler):
    def get(self):
        self.finish("It works!")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
        ]

        settings = dict(
            debug=True
        )

        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == "__main__":
    main(Application)