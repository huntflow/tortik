# _*_ coding: utf-8 _*_
import os
try:
    from cStringIO import StringIO  # python 2
except ImportError:
    from io import StringIO  # python 3

from collections import OrderedDict
import unittest
from tornado.escape import to_unicode

from tortik.util import make_qs, update_url, real_ip
from tortik.util.xml_etree import parse, tostring


class Request(object):
    headers = {}
    remote_ip = None


class BaseTest(unittest.TestCase):
    def assertQueriesEqual(self, qs1, qs2):
        qs1_list = sorted(qs1.split('&'))
        qs2_list = sorted(qs2.split('&'))
        self.assertEqual(qs1_list, qs2_list)

    def assertUrlsEqual(self, url1, url2):
        u1 = url1.split('?')
        u2 = url2.split('?')

        self.assertEqual(len(u1), len(u2))
        self.assertEqual(u1[0], u2[0])
        if len(u1) > 1:
            self.assertQueriesEqual(u1[1], u2[1])


class TestMakeQs(BaseTest):
    """This is copy of Frontik's make_qs test: https://github.com/hhru/frontik/blob/master/tests/test_util.py
    """
    def test_make_qs_simple(self):
        query_args = {'a': '1', 'b': '2'}
        self.assertQueriesEqual(make_qs(query_args), 'a=1&b=2')

    def test_make_qs_not_str(self):
        query_args = {'a': 1, 'b': 2.0, 'c': True}
        self.assertQueriesEqual(make_qs(query_args), 'a=1&b=2.0&c=True')

    def test_make_qs_iterables(self):
        query_args = {'a': [1, 2], 'b': {1, 2}, 'c': (1, 2), 'd': frozenset((1, 2))}
        self.assertQueriesEqual(make_qs(query_args), 'a=1&a=2&b=1&b=2&c=1&c=2&d=1&d=2')

    def test_make_qs_none(self):
        query_args = {'a': None, 'b': None}
        self.assertQueriesEqual(make_qs(query_args), '')

    def test_make_qs_encode(self):
        query_args = {'a': u'тест', 'b': 'тест'}
        qs = make_qs(query_args)
        self.assertIsInstance(qs, str)
        self.assertQueriesEqual(qs, 'a=%D1%82%D0%B5%D1%81%D1%82&b=%D1%82%D0%B5%D1%81%D1%82')

    def test_from_ordered_dict(self):
        qs = make_qs(OrderedDict([('z', 'я'), ('г', 'd'), ('b', ['2', '1'])]))
        self.assertIsInstance(qs, str)
        self.assertEqual(qs, 'z=%D1%8F&%D0%B3=d&b=2&b=1')

    def test_unicode_params(self):
        self.assertQueriesEqual(
            make_qs({'при': 'вет', u'по': u'ка'}),
            '%D0%BF%D1%80%D0%B8=%D0%B2%D0%B5%D1%82&%D0%BF%D0%BE=%D0%BA%D0%B0'
        )

    def test_make_qs_comma(self):
        query_args = {'a': '1,2,3', 'b': 'asd'}
        self.assertQueriesEqual(make_qs(query_args, '/,'), 'a=1,2,3&b=asd')

    def test_make_qs_comma_quoted(self):
        # default value for `safe` parameter of make_qs is '/' so commas
        # should be encoded
        query_args = {'a': '1,2,3', 'b': 'asd'}
        self.assertQueriesEqual(make_qs(query_args), 'a=1%2C2%2C3&b=asd')


class TestUpdateUrl(BaseTest):
    def test_simple(self):
        self.assertUrlsEqual(update_url('http://google.com'), 'http://google.com')
        self.assertUrlsEqual(update_url('https://google.com'), 'https://google.com')
        self.assertUrlsEqual(update_url('google.com'), 'google.com')
        self.assertUrlsEqual(update_url('//google.com'), '//google.com')
        self.assertUrlsEqual(update_url('http://google.com?a=1'), 'http://google.com?a=1')
        self.assertUrlsEqual(update_url('http://google.com?a=1&b=2'), 'http://google.com?a=1&b=2')
        self.assertUrlsEqual(update_url('http://google.com?привет=1'),
                             'http://google.com?%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82=1')
        self.assertUrlsEqual(update_url(u'http://google.com?привет=1'),
                             'http://google.com?%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82=1')

    def test_update_args(self):
        self.assertUrlsEqual(update_url('http://google.com', update_args={'a': 1}), 'http://google.com?a=1')
        self.assertUrlsEqual(update_url('http://google.com', update_args={'a': '1'}), 'http://google.com?a=1')
        self.assertUrlsEqual(update_url('http://google.com', update_args={'a': u'1'}), 'http://google.com?a=1')
        self.assertUrlsEqual(update_url('http://google.com', update_args={u'a': u'1'}), 'http://google.com?a=1')

        self.assertUrlsEqual(update_url('http://google.com?a=2', update_args={'a': 1}), 'http://google.com?a=1')
        self.assertUrlsEqual(update_url('http://google.com?a=2&b=1', update_args={'a': 1}), 'http://google.com?a=1&b=1')

    def test_remove_args(self):
        self.assertUrlsEqual(update_url('http://google.com?a=2', remove_args=['a']), 'http://google.com')
        self.assertUrlsEqual(update_url('http://google.com?a=2', remove_args=[u'a']), 'http://google.com')
        self.assertUrlsEqual(update_url('http://google.com?привет=2', remove_args=['привет']), 'http://google.com')
        self.assertUrlsEqual(update_url(u'http://google.com?привет=2', remove_args=[u'привет']), 'http://google.com')
        self.assertUrlsEqual(update_url('http://google.com?a=2&a=1', remove_args=['a']), 'http://google.com')
        self.assertUrlsEqual(update_url('http://google.com?a=2&a=1&b=3', remove_args=['a']), 'http://google.com?b=3')
        self.assertUrlsEqual(update_url('http://google.com?a=2&a=1&b=3', remove_args=['b']),
                             'http://google.com?a=2&a=1')

    def test_both(self):
        self.assertUrlsEqual(update_url('http://google.com?b=3', update_args={'a': 1}, remove_args=['b']),
                             'http://google.com?a=1')
        self.assertUrlsEqual(update_url('http://google.com?a=2&b=3&c=4', update_args={'a': 1}, remove_args=['b']),
                             'http://google.com?a=1&c=4')


class TestParse(BaseTest):
    def test_parse_xml(self):
        fd = open(os.path.join(os.path.dirname(__file__), 'data', 'simple.xml'), 'r')
        tree = parse(fd)
        self.assertEqual(tree.getroot().tag, 'data')
        convert = tostring(tree.getroot(), pretty_print=True, xml_declaration=True, encoding='UTF-8')
        # replace any possible conversion differences that are ok
        # Python 3+ native etree does not include xml declaration so we should remove it everywhere
        converted = to_unicode(convert).replace('\n', '').replace(' ', '').replace('\'', '"').\
            replace('<?xmlversion="1.0"encoding="UTF-8"?>', '').strip()
        fd.seek(0)
        base = to_unicode(fd.read()).replace('\n', '').replace(' ', '').\
            replace('<?xmlversion="1.0"encoding="UTF-8"?>', '').strip()
        self.assertEqual(converted, base)
        fd.close()


class TestRealIp(BaseTest):
    def test_real_ip(self):
        # default
        request = Request()
        self.assertEqual('127.0.0.1', real_ip(request))

        request = Request()
        request.headers = {'X-Real-Ip': '8.8.8.8', 'X-Forwarded-For': '10.0.0.1'}

        self.assertEqual('8.8.8.8', real_ip(request))

        request = Request()
        request.headers = {'X-Forwarded-For': '10.0.0.1, 127.0.0.1'}

        self.assertEqual('10.0.0.1', real_ip(request))
