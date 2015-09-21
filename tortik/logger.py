# -*- coding: utf-8 -*-
import time
import logging
import logging.handlers
from collections import OrderedDict
from datetime import datetime

from tornado.options import options, define

from tortik.util.dumper import request_to_curl_string

LOGGER_NAME = 'tortik'
_SKIP_EVENT = "skip_event"

tortik_log = logging.getLogger(LOGGER_NAME)


define('tortik_logformat', default='[%(process)s %(asctime)s %(levelname)s %(name)s] %(message)s')


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.name = '.'.join(filter(None, [record.name, getattr(record, 'request_id', None)]))
        event_queue = getattr(record, 'event_queue', None)
        if event_queue is not None and getattr(record, _SKIP_EVENT, None) is None:
            created = record.created or time.time()
            event_queue[record] = {
                'created': str(datetime.fromtimestamp(created).time()),
                'msg': record.getMessage(),
                'exc_info': record.exc_info,
                'type': record.levelname}
        return True


class PageLogger(logging.LoggerAdapter):
    class StageInfo(object):
        def __init__(self, start):
            self.start = start
            self.end = None
            self.counter = 1

        def __str__(self):
            if self.end:
                return "{0:.2f}".format(1000 * (self.end - self.start))
            else:
                return "infinite"

    def __init__(self, request, request_id, use_debug, handler_name):
        self.debug_info = OrderedDict() if use_debug else None
        self.request = request
        logging.LoggerAdapter.__init__(
            self,
            tortik_log,
            {'request_id': str(request_id),
             'event_queue': self.debug_info})
        self.started = time.time()
        self.request_id = request_id
        self.handler_name = handler_name
        self.stages = OrderedDict()
        self.debug('Started {0} {1}'.format(request.method, request.uri), extra={_SKIP_EVENT: True})
        self._completed = False

    def process(self, msg, kwargs):
        if "extra" not in kwargs:
            kwargs["extra"] = self.extra
        else:
            kwargs["extra"].update(self.extra)
        return msg, kwargs

    # def cache_access_started(self, cache_name):
    #     self.debug("Requesting cache {0}".format(cache_name), extra={_SKIP_EVENT: True})
    #     if self.debug_info is not None:
    #         self.debug_info[cache_name] = {
    #             'type': 'cache',
    #             'started': time.time(),
    #             'name': cache_name
    #         }
    #
    # def cache_access_complete(self, name, value):
    #     if self.debug_info is not None:
    #         event = self.debug_info.get(name)
    #         if event is None:
    #             self.error("Cache access response is not found: {0}".format(name))
    #         else:
    #             now = time.time()
    #             event.update({
    #                 'completed': now,
    #                 'took': now - event['started'],
    #                 'value': repr(value),
    #                 })

    def request_started(self, request):
        self.debug("Requesting {0} {1}".format(request.method, request.url), extra={_SKIP_EVENT: True})
        if self.debug_info is not None:
            event = {
                'type': 'NET',
                'started': time.time(),
                'request': {
                    'url': request.url,
                    'method': request.method,
                    'headers': request.headers,
                    'data': request.body,
                    'curl': request_to_curl_string(request)
                }
            }
            self.debug_info[request] = event

    def request_complete(self, resp):
        if self.debug_info is not None:
            event = self.debug_info.get(resp.request, None)
            if event is None:
                self.error("Request for response is not found: {0}".format(resp.request.url))
            else:
                now = time.time()
                event.update({
                    'completed': now,
                    'took': now - event['started'],
                    'time_info': getattr(resp, 'time_info', None),
                    'response': {
                        'code': resp.code,
                        'headers': resp.headers,
                        'body': resp.body,
                        'data': resp.data
                    },
                })

        level = logging.DEBUG
        if 400 <= resp.code < 500:
            level = logging.INFO
        elif resp.code >= 500:
            level = logging.ERROR

        self.log(level, "Complete {0} {1} {2} in {3}ms".format(resp.code, resp.request.method, resp.request.url,
                                                               int(resp.request_time * 1000.0)),
                 extra={_SKIP_EVENT: True})

    def stage_started(self, stage_name):
        if stage_name not in self.stages:
            self.stages[stage_name] = PageLogger.StageInfo(time.time())
        else:
            self.warning("Stage {0} already started".format(stage_name))
            self.stages[stage_name].counter += 1

    def stage_complete(self, stage_name):
        if stage_name in self.stages:
            stage = self.stages[stage_name]
            stage.counter -= 1
            if stage.counter < 0:
                self.error("Freed stage {0} more times then it is needed".format(stage_name))
            elif stage.counter == 0:
                self.stages[stage_name].end = time.time()
        else:
            self.error("Stage {0} wasn't stared".format(stage_name))

    def complete_logging(self, status_code, additional_data=None):
        if self._completed:
            return

        if additional_data is None:
            additional_data = []

        data = [
            ('handler', self.handler_name),
            ('method', self.request.method),
            ('code', status_code),
            ('total', int(1000 * self.request.request_time()))  # <current_time> - <start> if request not finished yet
        ] + list(self.stages.items()) + additional_data

        self.info('MONIK {0}'.format(' '.join('{0}={1}'.format(k, v) for (k, v) in data)))

        self._completed = True

    def get_debug_info(self):
        return self.debug_info.values()


def configure(logfile=None):
    if logfile:
        handler = logging.handlers.WatchedFileHandler(logfile)
        handler.setFormatter(logging.Formatter(options.tortik_logformat))
        tortik_log.addHandler(handler)

    tortik_log.addFilter(RequestIdFilter())
    tortik_log.setLevel(logging.DEBUG)
