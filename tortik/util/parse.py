# -*- coding: utf-8 -*-
from lxml import etree
from tornado.escape import json_decode

from tortik.util import HTTPError

try:
    import httplib  # py2
except ImportError:
    import http.client as httplib  # py3


def parse_xml(response):
    if response.code == 599 or response.buffer is None:
        raise HTTPError(httplib.SERVICE_UNAVAILABLE, 'Response timeout or no body buffer')
    try:
        parser = etree.XMLParser(remove_blank_text=True)
        return etree.parse(response.buffer, parser=parser)
    except etree.ParseError:
        raise HTTPError(httplib.SERVICE_UNAVAILABLE, 'Unable to parse xml')


def parse_json(response):
    if response.code == 599 or response.body is None:
        raise HTTPError(httplib.SERVICE_UNAVAILABLE, 'Response timeout or no body')
    try:
        result = json_decode(response.body)
    except ValueError:
        raise HTTPError(httplib.SERVICE_UNAVAILABLE, 'Unable to parse json')
    return result
