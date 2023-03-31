try:
    from urllib import quote_plus, _is_unicode
except ImportError:
    from urllib.parse import quote_plus


def urlencode(query, doseq=0, safe="/"):
    """Patched py2 version of urlencode - added `safe` parameter (py3 version
    supports this).

    The original docstring:

    Encode a sequence of two-element tuples or dictionary into a URL query string.

    If any values in the query arg are sequences and doseq is true, each
    sequence element is converted to a separate parameter.

    If the query arg is a sequence of two-element tuples, the order of the
    parameters in the output will match the order of parameters in the
    input.
    """

    if hasattr(query, "items"):
        # mapping objects
        query = query.items()
    else:
        # it's a bother at times that strings and string-like objects are
        # sequences...
        # non-sequence items should not work with len()
        # non-empty strings will fail this
        if len(query) and not isinstance(query[0], tuple):
            raise TypeError
        # zero-length sequences of all types will get here and succeed,
        # but that's a minor nit - since the original implementation
        # allowed empty dicts that type of behavior probably should be
        # preserved for consistency
    parts = []
    if not doseq:
        # preserve old behavior
        for k, v in query:
            k = quote_plus(str(k), safe=safe)
            v = quote_plus(str(v), safe=safe)
            parts.append(k + "=" + v)
    else:
        for k, v in query:
            k = quote_plus(str(k), safe=safe)
            if isinstance(v, str):
                v = quote_plus(v, safe=safe)
                parts.append(k + "=" + v)
            elif _is_unicode(v):
                # is there a reasonable way to convert to ASCII?
                # encode generates a string, but "replace" or "ignore"
                # lose information and "strict" can raise UnicodeError
                v = quote_plus(v.encode("ASCII", "replace"), safe=safe)
                parts.append(k + "=" + v)
            else:
                try:
                    # is this a sufficient test for sequence-ness?
                    len(v)
                except TypeError:
                    # not a sequence
                    v = quote_plus(str(v), safe=safe)
                    parts.append(k + "=" + v)
                else:
                    # loop over the sequence
                    for elt in v:
                        parts.append(k + "=" + quote_plus(str(elt), safe=safe))
    return "&".join(parts)
