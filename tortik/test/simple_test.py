#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, with_statement

from tornado.testing import AsyncTestCase
from tornado.httpclient import AsyncHTTPClient

class MyTestCase(AsyncTestCase):
    def test_http_fetch(self):
        client = AsyncHTTPClient(self.io_loop)
        client.fetch("http://www.tornadoweb.org/", self.stop)
        response = self.wait()
        # Test contents of response
        self.assertTrue("FriendFeed" in response.body)