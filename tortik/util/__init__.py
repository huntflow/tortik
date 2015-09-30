# -*- encoding: utf-8 -*-
from types import FunctionType
import tornado.web
from tornado.util import unicode_type

try:
    import urlparse  # py2
except ImportError:
    import urllib.parse as urlparse  # py3

try:
    from urllib import urlencode  # py2
except ImportError:
    from urllib.parse import urlencode  # py3


def decorate_all(decorator_list):
    def is_method_need_to_decorate(func_name, func_obj, check_param):
        """check if an object should be decorated"""
        methods = ["get", "head", "post", "put", "delete"]
        return (func_name in methods and
                isinstance(func_obj, FunctionType) and
                getattr(func_obj, check_param, True))

    """decorate all instance methods (unless excluded) with the same decorator"""
    class DecorateAll(type):
        def __new__(cls, name, bases, dct):
            for func_name, func_obj in dct.items():
                for item in decorator_list:
                    decorator, check_param = item
                    if is_method_need_to_decorate(func_name, func_obj, check_param):
                        dct[func_name] = decorator(dct[func_name])
            return super(DecorateAll, cls).__new__(cls, name, bases, dct)

        def __setattr__(self, func_name, func_obj):
            for item in decorator_list:
                decorator, check_param = item
                if is_method_need_to_decorate(func_name, func_obj, check_param):
                    func_obj = decorator(func_obj)
            super(DecorateAll, self).__setattr__(func_name, func_obj)
    return DecorateAll


def make_list(val):
    if isinstance(val, list):
        return val
    else:
        return [val]


def real_ip(request):
    return (request.headers.get('X-Real-Ip', None) or request.headers.get('X-Forwarded-For', None) or
            request.remote_ip or '127.0.0.1')


HTTPError = tornado.web.HTTPError
ITERABLE = (set, frozenset, list, tuple)


def update_url(url, update_args=None, remove_args=None):
    scheme, sep, url_new = url.partition('://')
    if len(scheme) == len(url):
        scheme = ''
    else:
        url = '//' + url_new

    url_split = urlparse.urlsplit(url)
    query_dict = urlparse.parse_qs(url_split.query, keep_blank_values=True)

    # add args
    if update_args:
        query_dict.update(update_args)

    # remove args
    if remove_args:
        query_dict = dict([(k, query_dict.get(k)) for k in query_dict if k not in remove_args])

    query = make_qs(query_dict)
    return urlparse.urlunsplit((scheme, url_split.netloc, url_split.path, query, url_split.fragment))


def make_qs(query_args):
    def _encode(s):
        if isinstance(s, unicode_type):
            return s.encode('utf-8')
        else:
            return s

    kv_pairs = []
    for key, val in query_args.items():
        if val is not None:
            encoded_key = _encode(key)
            if isinstance(val, ITERABLE):
                for v in val:
                    kv_pairs.append((encoded_key, _encode(v)))
            else:
                kv_pairs.append((encoded_key, _encode(val)))

    qs = urlencode(kv_pairs, doseq=True)

    return qs
