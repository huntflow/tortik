# -*- coding: utf-8 -*-
from tornado.escape import json_decode

from tortik.util import HTTPError
from tortik.util.xml_etree import parse, ParseError

try:
    import httplib  # py2
except ImportError:
    import http.client as httplib  # py3


def parse_xml(response):
    if response.code == 599 or response.buffer is None:
        raise HTTPError(httplib.SERVICE_UNAVAILABLE, 'Response timeout or no body buffer')
    try:
        return parse(response.buffer)
    except ParseError:
        raise HTTPError(httplib.SERVICE_UNAVAILABLE, 'Unable to parse xml')


def parse_json(response):
    if response.code == 599 or response.body is None:
        raise HTTPError(httplib.SERVICE_UNAVAILABLE, 'Response timeout or no body')
    try:
        result = json_decode(response.body)
    except ValueError:
        raise HTTPError(httplib.SERVICE_UNAVAILABLE, 'Unable to parse json')
    return result
