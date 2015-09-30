# -*- coding: utf-8 -*-
from tornado.httputil import HTTPHeaders
from tornado.util import basestring_type

from . import ITERABLE


def dump(obj):
    refs = set()

    def primitive(value, ptype='string'):
        return dict(type=ptype, value=value)

    def _make_dump(item):
        if isinstance(item, ITERABLE):
            if len(item) == 0:
                return dict(type='array', value=[])
            if id(item) in refs:
                return primitive('<circular reference>')

            refs.add(id(item))
            return dict(type='array', value=list(map(lambda x: _make_dump(x), item)))
        elif isinstance(item, dict):
            if not item:
                return dict(type='dict', value=dict())
            if id(item) in refs:
                return primitive('<circular reference>')
            refs.add(id(item))

            return dict(type='dict', value=dict((x, _make_dump(y)) for x, y in item.items()))
        elif isinstance(item, bool):
            return primitive('true' if item else 'false', 'bool')
        elif isinstance(item, basestring_type):
            return primitive(item)
        elif isinstance(item, (int, float)):
            return primitive(item, 'number')
        elif item is None:
            return primitive('null', 'null')
        else:
            return primitive(repr(item), 'string')

    return _make_dump(obj)


def request_to_curl_string(request):
    def _escape_apos(s):
        return s.replace("'", "'\"'\"'")

    try:
        if request.body:
            request.body.decode('ascii')
        is_binary_data = False
    except UnicodeError:
        is_binary_data = True

    curl_headers = HTTPHeaders(request.headers)
    if request.body and 'Content-Length' not in curl_headers:
        curl_headers['Content-Length'] = len(request.body)

    if is_binary_data:
        curl_echo_data = "echo -e {} |".format(repr(request.body))
        curl_data_string = '--data-binary @-'
    else:
        curl_echo_data = ''
        curl_data_string = "--data '{}'".format(_escape_apos(str(request.body))) if request.body else ''

    return "{echo} curl -X {method} '{url}' {headers} {data}".format(
        echo=curl_echo_data,
        method=request.method,
        url=request.url,
        headers=' '.join("-H '{}: {}'".format(k, _escape_apos(str(v))) for k, v in curl_headers.items()),
        data=curl_data_string
    ).strip()
