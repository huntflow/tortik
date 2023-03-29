# _*_ coding: utf-8 _*_

import unittest

from tortik.util.dumper import dump


class DumperTestCase(unittest.TestCase):
    def test_circular_reference(self):
        a = {"a": 123}
        a["b"] = a
        expected = {
            "type": "dict",
            "value": {
                "a": {"type": "number", "value": 123},
                "b": {"type": "string", "value": "<circular reference>"},
            },
        }
        self.assertEqual(expected, dump(a))
