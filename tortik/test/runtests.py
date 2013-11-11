#!/usr/bin/env python

try:
    import unittest2 as unittest
except ImportError:
    import unittest

TEST_MODULES = [
    'tortik.test.simple_test',
    'tortik.test.preprocessor_test',
    'tortik.test.postprocessor_test',
    'tortik.test.exceptions_test',
]

def all():
    return unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)

def main():
    import tornado.testing
    tornado.testing.main()

if __name__ == '__main__':
    main()