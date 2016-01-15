# -*- coding: utf-8 -*-
from tortik.logger import tortik_log

native_etree = False

try:
    from lxml import etree
except ImportError:
    tortik_log.info('lxml not installed. Using native etree implementation')
    native_etree = True
    import xml.etree.ElementTree as etree


def parse(source, parser=None):
    if parser is None and native_etree is False:
        parser = etree.XMLParser(remove_blank_text=True)

    return etree.parse(source, parser)


def tostring(element, **kwargs):
    native_args = ['encoding', 'method']
    if native_etree is True:
        pass_args = dict()
        for a in native_args:
            if a in kwargs:
                pass_args[a] = kwargs[a]
    else:
        pass_args = kwargs

    return etree.tostring(element, **pass_args)


ParseError = etree.ParseError
