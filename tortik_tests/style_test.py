# _*_ coding: utf-8 _*_
from __future__ import absolute_import

import sys
from os import path
import unittest
from StringIO import StringIO

from tortik_tests import pep8

_project_root = path.abspath(path.join(path.dirname(__file__), '..'))
_src_dirs = [path.join(_project_root, 'tortik'),
             path.join(_project_root, 'tortik_tests'),
             path.join(_project_root, 'setup.py')]


class StyleTestCase(unittest.TestCase):

    def test_pep8(self):
        # TODO: remove sys.stdout/sys.stderr workaround
        nose_capture_enabled = isinstance(sys.stdout, StringIO)
        nose_stdout = None
        nose_stderr = None
        if nose_capture_enabled:
            sys.stdout, nose_stdout = StringIO(), sys.stdout
            sys.stderr, nose_stderr = StringIO(), sys.stderr

        pep8style = pep8.StyleGuide(
            show_pep8=False,
            show_source=True,
            repeat=True,
            max_line_length=120,
            statistics=True,
        )
        result = pep8style.check_files(_src_dirs)

        fail = False
        if result.total_errors > 0:
            format_vals = {'out': '', 'err': '', 'stat': ''}
            if nose_capture_enabled:
                format_vals['out'] = sys.stdout.getvalue() + '\n'
                format_vals['err'] = sys.stderr.getvalue() + '\n'
            format_vals['stat'] = '\n'.join(result.get_statistics(''))
            statistics = '{out}{err}Statistics:{stat}'.format(**format_vals)
            fail = True
        if nose_capture_enabled:
            sys.stdout = nose_stdout
            sys.stderr = nose_stderr
        if fail:
            print(statistics.decode('ascii', 'replace').replace(u'\uFFFD', '?'))
            self.fail('PEP8 styles errors')
