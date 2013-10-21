#!/usr/bin/env python

import socket
from tornado import netutil

try:
    import unittest2 as unittest
except ImportError:
    import unittest

def bind_unused_port():
    """Binds a server socket to an available port on localhost.

    Returns a tuple (socket, port).
    """
    [sock] = netutil.bind_sockets(None, 'localhost', family=socket.AF_INET)
    port = sock.getsockname()[1]
    return sock, port


