# -*- coding: utf-8 -*-

import os
import re


def __parse_version_from_changelog():
    try:
        deb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'debian', 'changelog')
        with open(deb_path, 'r') as changelog:
            regmatch = re.match(r'python-tortik \((.*)\).*', changelog.readline())
            return regmatch.groups()[0]
    except (IOError, AttributeError):
        return None

version = __parse_version_from_changelog() or '0.2.1'
