# -*- coding: utf-8 -*-


def dump(obj):
    refs = set()

    def primitive(value, ptype='string'):
        return dict(type=ptype, value=value)

    def _make_dump(item):
        if isinstance(item, list):
            if len(item) == 0:
                return dict(type='array', value=[])
            if id(item) in refs:
                return primitive('<circular reference>')

            refs.add(id(item))
            return dict(type='array', value=map(lambda x: _make_dump(x), item))
        elif isinstance(item, dict):
            if not item:
                return dict(type='dict', value=dict())
            if id(item) in refs:
                return primitive('<circular reference>')
            refs.add(id(item))

            return dict(type='dict', value=dict((x, _make_dump(y)) for x, y in item.items()))
        elif isinstance(item, bool):
            return primitive('true' if item else 'false', 'bool')
        elif isinstance(item, basestring):
            return primitive(item)
        elif isinstance(item, (int, float)):
            return primitive(item, 'number')
        elif item is None:
            return primitive('null', 'null')
        else:
            return primitive(repr(item), 'string')

    return _make_dump(obj)
