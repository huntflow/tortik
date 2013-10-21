# -*- coding: utf-8 -*-

import urlparse, urllib
from itertools import count
from functools import wraps, partial
from copy import copy
import tornado.web
import tornado.curl_httpclient

from tortik.util import decorate_all, make_list, real_ip, Item
from tortik.logger import PageLogger
from tortik.util.async import AsyncGroup
from tortik.util.parse import parse_xml, parse_json

stats = count()

_DEBUG_ALL = "all"
_DEBUG_ONLY_ERRORS = "only_errors"
_DEBUG_NONE = "none"

def preprocessors(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        def finished_cb():
            method(self, *args, **kwargs)

        ag = AsyncGroup(finished_cb, log=self.log.debug, name='preprocessors')
        for preprocessor in self.preprocessors:
            preprocessor(self, ag.add_notification())

        ag.try_finish()

    return wrapper

class RequestHandler(tornado.web.RequestHandler):
    decorators = [
        (preprocessors, 'preprocessors'),
        (tornado.web.asynchronous, 'asynchronous'),  # should be the last
    ]
    __metaclass__ = decorate_all(decorators)

    def initialize(self, *args, **kwargs):
        debug_agrs = self.get_arguments('debug')
        # debug_arg_set = (len(debug_agrs) > 0 and debug_pass is not None and
        #                  (debug_pass == '' or debug_pass == debug_agrs[-1]))

        if debug_agrs:
            self.debug_type = _DEBUG_ALL
        # elif options.debug:
        #     self.debug_type = _DEBUG_ONLY_ERRORS
        else:
            self.debug_type = _DEBUG_NONE

        self.request_id = self.request.headers.get('X-Request-Id', str(stats.next()))

        self.log = PageLogger(self.request, self.request_id, (self.debug_type != _DEBUG_NONE),
                              handler_name=(type(self).__module__ + '.' + type(self).__name__))

        self.responses = {}
        self.http_client = tornado.curl_httpclient.CurlAsyncHTTPClient()

        self.preprocessors = copy(self.preprocessors) if hasattr(self, 'preprocessors') else []
        self.postprocessors = copy(self.postprocessors) if hasattr(self, 'postprocessors') else []

        self.data = Item()

    def add(self, name, data):
        self.data[name] = Item(data) if isinstance(data, dict) else data

    def finish(self, chunk=None):
        if chunk is not None:
            self.write(chunk)

        chunk = "".join(self._write_buffer)
        def finished_cb(handler, data):
            self._write_buffer = [data]
            tornado.web.RequestHandler.finish(handler)

        if self.postprocessors:
            last = len(self.postprocessors) - 1
            def add_cb(index):
                if index == last:
                    return finished_cb
                else:
                    def _cb(handler, data):
                        self.postprocessors[index + 1](handler, data, add_cb(index + 1))
                    return _cb

            self.postprocessors[0](self, chunk, add_cb(0))
        else:
            finished_cb(self, chunk)

    def fetch_requests(self, requests, callback=None, stage='page'):
        self.log.stage_started(stage)
        requests = make_list(requests)

        def _finish_cb():
            self.log.stage_complete(stage)
            callback()

        ag = AsyncGroup(_finish_cb, self.log.debug, name=stage)

        def _on_fetch(response, name):
            content_type = response.headers.get('Content-Type').split(';')[0]
            response.data = None
            try:
                if content_type == 'text/xml':
                    response.data = parse_xml(response)
                elif content_type == 'application/json':
                    response.data = parse_json(response)
            except:
                self.log.warning('Could not parse response with Content-Type header')

            self.responses[name] = response
            self.log.request_complete(response)

        for req in requests:
            self.log.request_started(req)
            self.http_client.fetch(req, ag.add(partial(_on_fetch, name=req.name)))

    def make_request(self, name, method, full_url=None, url_prefix=None, path='', data='', headers=None,
                     connect_timeout=0.5, request_timeout=2, follow_redirects=True):

        if not ((full_url is None) ^ (url_prefix is None)):
            raise TypeError('make_request required path/url_prefix arguments pair or full_url argument')
        if full_url is not None and path != '':
            raise TypeError("Can't combine full_url and path arguments")

        scheme = 'http'
        query = ''
        body = ''

        if not isinstance(data, dict) and full_url is not None:
            data = urlparse.parse_qs(data)

        if full_url is not None:
            parsed_full_url = urlparse.urlsplit(full_url)
            scheme = parsed_full_url.scheme
            url_prefix = parsed_full_url.netloc
            path = parsed_full_url.path
            if len(data):
                updated_query = urlparse.parse_qs(parsed_full_url.query)
                updated_query.update(data)
                data = updated_query

        def _make_qs(query_args):
            def _encode(s):
                if isinstance(s, unicode):
                    return s.encode('utf-8')
                else:
                    return s

            kv_pairs = []
            for (key, val) in query_args.iteritems():
                if val is not None:
                    if isinstance(val, list):
                        for v in val:
                            kv_pairs.append((key, _encode(v)))
                    else:
                        kv_pairs.append((key, _encode(val)))

            qs = urllib.urlencode(kv_pairs)

            return qs

        data = _make_qs(data) if isinstance(data, dict) else data

        if method in ['GET', 'HEAD']:
            query = data
        else:
            body = data

        headers = {} if headers is None else headers

        headers.update({
            'X-Forwarded-For': real_ip(self.request),
            'X-Request-Id': self.request_id,
            'Content-Type': headers.get('Content-Type', 'application/x-www-form-urlencoded')
        })

        req = tornado.curl_httpclient.HTTPRequest(
            url=urlparse.urlunsplit((scheme, url_prefix, path, query, '')),
            method=method,
            headers=headers,
            body=body,
            connect_timeout=connect_timeout,
            request_timeout=request_timeout,
            follow_redirects=follow_redirects
        )
        req.name = name
        return req

    def add_preprocessor(self, preprocessor):
        self.preprocessors.append(preprocessor)

    def add_postprocessor(self, postprocessor):
        self.postprocessors.append(postprocessor)


