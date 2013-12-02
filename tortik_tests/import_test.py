# _*_ coding: utf-8 _*_

import sys
import unittest
import os
from os import path


class ImportAllPythonCodeTestCase(unittest.TestCase):

    def setUp(self):
        self.pkg_dir = path.abspath(path.join(path.dirname(__file__), '..', 'tortik'))
        self.pkg_name = path.basename(self.pkg_dir)

    def test_import_all(self):
        self.assertTrue(path.isdir(self.pkg_dir))
        has_any_module = False
        for module, _, __ in self.i_package_walk():
            has_any_module = True
            self.try_import(module)
        self.assertTrue(has_any_module)

    def try_import(self, module):
        try:
            __import__(module, globals(), locals(), [], -1)  # TODO: use importlib for python 2.7+
        except ImportError, e:
            self.fail('Unable to import "{module}" module ({e!s}). \n\nSys paths:\n{paths}'.format(
                module=module, e=e, paths='\n'.join(sys.path)
            ))

    # ----------------------------------------------------
    def i_package_walk(self):
        base_path = self.pkg_dir + '/'
        base_path_len = len(base_path)
        base_name = self.pkg_name + '.'
        for root, dirs, files in os.walk(self.pkg_dir):
            for basename in files:
                if basename.endswith('.py'):
                    full_path = os.path.join(root, basename)
                    if full_path.startswith(base_path):
                        rel_path = full_path[base_path_len:]
                        module = rel_path.replace('/', '.')[:-3]
                        if module == '__init__':
                            module = self.pkg_name
                        elif module.endswith('.__init__'):
                            module = base_name + module[:-9]
                        else:
                            module = base_name + module
                        yield module, full_path, rel_path
        raise StopIteration()
