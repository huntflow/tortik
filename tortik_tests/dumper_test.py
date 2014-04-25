# _*_ coding: utf-8 _*_

import unittest

from tortik.util.dumper import Dumper


class DumperTestCase(unittest.TestCase):
    def test_circular_reference(self):
        a = {'a': 123}
        a['b'] = a
        expected = ('<span class="dumper__collapser"></span>{<ul class="dumper-collapsible"><li class="dumper-item">'
                    '<span class="dumper-item__prop">a</span>: <span class="dumper-item__num">123</span>,</li>'
                    '<li class="dumper-item"><span class="dumper-item__prop">b</span>: '
                    '<span class="dumper-item__string">"&lt;circular reference&gt;"</span></li></ul>}')
        self.assertEqual(expected, Dumper.dump(a))
