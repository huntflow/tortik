#!/usr/bin/env python

import textwrap

try:
    import unittest2 as unittest
except ImportError:
    import unittest

TEST_MODULES = [
    'tortik.test.simple_test',
    'tortik.test.preprocessor_test',
    'tortik.test.postprocessor_test',
]

def all():
    return unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)

if __name__ == '__main__':
    import tornado.testing
    tornado.testing.main()