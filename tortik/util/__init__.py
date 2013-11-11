# -*- encoding: utf-8 -*-

from urllib import urlencode
import urllib
import urlparse
from types import FunctionType
from lxml import etree
import httplib


from tortik.util.http import get_status_code_message

import tornado.web

try:
    from collections import OrderedDict
except ImportError:
    from ordered_dict import OrderedDict

def do_decorate(func_name, func_obj, check_param):
    """check if an object should be decorated"""
    methods = ["get", "head", "post", "put", "delete"]
    return (func_name in methods and
            isinstance(func_obj, FunctionType) and
            getattr(func_obj, check_param, True))


def decorate_all(decorator_list):
    """decorate all instance methods (unless excluded) with the same decorator"""
    class DecorateAll(type):
        def __new__(cls, name, bases, dct):
            for func_name, func_obj in dct.iteritems():
                for item in decorator_list:
                    decorator, check_param = item
                    if do_decorate(func_name, func_obj, check_param):
                        dct[func_name] = decorator(dct[func_name])
            return super(DecorateAll, cls).__new__(cls, name, bases, dct)

        def __setattr__(self, func_name, func_obj):
            for item in decorator_list:
                decorator, check_param = item
                if do_decorate(func_name, func_obj, check_param):
                    func_obj = decorator(func_obj)
            super(DecorateAll, self).__setattr__(func_name, func_obj)
    return DecorateAll

def make_list(val):
    if isinstance(val, list):
        return val
    else:
        return [val]

def real_ip(request):
    return (request.headers.get("X-Real-Ip", None) or request.headers.get("X-Forwarded-For", None)
            or request.remote_ip or '127.0.0.1')


HTTPError = tornado.web.HTTPError
# class HTTPError(tornado.web.HTTPError):
#     """An exception that will turn into an HTTP error response."""
#     def __init__(self, status_code, backend_response=None, to_user=None, to_log=None, bad_argument=None, headers=None):
#         self.status_code = status_code
#         self.backend_response = backend_response
#         self.to_user = to_user
#         self.to_log = to_log
#         self.log_message = to_log  # if propogated to tornado
#         self.bad_argument = bad_argument
#         self.headers = headers if headers is not None else {}
#
#     def __str__(self):
#         message = "HTTP %d: %s" % (
#             self.status_code, get_status_code_message(self.status_code))
#         if self.log_message:
#             return message + " (" + (self.log_message % self.args) + ")"
#         else:
#             return message

def update_url(url, update_args=None, remove_args=None):
    scheme, sep, url_new = url.partition('://')
    if len(scheme) == len(url):
        scheme = ''
    else:
        url = '//' + url_new

    url_split = urlparse.urlsplit(url.encode('utf-8') if isinstance(url, unicode) else url)
    query_dict = urlparse.parse_qs(url_split.query, keep_blank_values=True)

    # add args
    if update_args:
        query_dict.update(update_args)
        # remove args
    if remove_args:
        query_dict = dict([(k, query_dict.get(k)) for k in query_dict if k not in remove_args])

    query = urlencode(query_dict, doseq=True)
    # specific case without net location. Thx to maizy for this fuckin' case
    if url_split.netloc:
        return urlparse.urlunsplit((scheme, url_split.netloc, url_split.path, query, url_split.fragment))
    else:
        return ''.join([
            scheme,
            '://' if scheme else '',
            url_split.path,
            '?' if query else '',
            query,
            '#' if url_split.fragment else '',
            url_split.fragment
        ])


def make_qs(query_args):
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
