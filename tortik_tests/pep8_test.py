# _*_ coding: utf-8 _*_

from os import path
import unittest

import pep8

_project_root = path.abspath(path.join(path.dirname(__file__), '..'))
_src_dirs = map(lambda x: path.join(_project_root, x), ['tortik', 'tortik_tests', 'examples', 'setup.py'])


class Pep8TestCase(unittest.TestCase):
    def test_pep8(self):
        pep8style = pep8.StyleGuide(
            show_pep8=False,
            show_source=True,
            max_line_length=120,
            statistics=True,
        )
        result = pep8style.check_files(_src_dirs)

        self.assertEqual(result.total_errors, 0, 'Pep8 found code style errors or warnings')
