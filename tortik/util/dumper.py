# -*- coding: utf-8 -*-

import json


class Dumper():
    def __init__(self):
        self._refs = set()

    @classmethod
    def dump(cls, obj):
        return cls().make_dump(obj)

    def make_dump(self, obj):
        if isinstance(obj, list):
            if len(obj) == 0:
                return '[ ]'
            if id(obj) in self._refs:
                return self._dec_with_span(self._js_string('<circular reference>'), 'string')
            self._refs.add(id(obj))

            return '<span class="dumper__collapser"></span>[<ul class="dumper-collapsible"><li class="dumper-item">' \
                   + ',</li><li class="dumper-item">'.join(map(lambda x: self.make_dump(x), obj)) + '</li></ul>]'
        elif isinstance(obj, dict):
            if not obj:
                return '{ }'
            if id(obj) in self._refs:
                return self._dec_with_span(self._js_string('<circular reference>'), 'string')
            self._refs.add(id(obj))

            return '<span class="dumper__collapser"></span>{<ul class="dumper-collapsible"><li class="dumper-item">' \
                   + ',</li><li class="dumper-item">'.join(map(lambda (x, y):
                                                               '<span class="dumper-item-prop">'
                                                               + '<span class="dumper-item-prop__q">"</span>'
                                                               + str(x)
                                                               + '<span class="dumper-item-prop__q">"</span></span>: '
                                                               + self.make_dump(y), obj.items())) + \
                   '</li></ul>}'
        elif isinstance(obj, bool):
            return self._dec_with_span('true' if obj else 'false', 'bool')
        elif isinstance(obj, basestring):
            return self._dec_with_span(self._js_string(obj), 'string')
        elif isinstance(obj, (int, float)):
            return self._dec_with_span(str(obj), 'num')
        elif obj is None:
            return self._dec_with_span('null', 'null')
        else:
            return self._dec_with_span(self._js_string(repr(obj)), 'string')

    def _dec_with_span(self, val, cls):
        return '<span class="dumper-item__' + cls + '">' + val + '</span>'

    def _html_encode(self, val):
        return val.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

    def _js_string(self, val):
        return '"' + self._html_encode(json.dumps(val, ensure_ascii=False)[1:-1]) + '"'
