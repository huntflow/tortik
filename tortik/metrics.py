import time

from prometheus_client import Counter, Histogram
from tornado.httputil import HTTPServerRequest


class _DummyMetric:
    def __init__(self):
        pass

    def labels(self, **kwargs):
        import logging
        logging.warning("Uses dummy metric !!!!")
        return self

    def inc(self, amount=1):
        pass

    def dec(self, amount=1):
        pass

    def set(self, value):
        pass

    def observe(self, value):
        pass

REQUEST_COUNT = _DummyMetric()
PROCESSING_TIME = _DummyMetric()

def init_metrics(registry):
    global REQUEST_COUNT, PROCESSING_TIME

    REQUEST_COUNT = Counter(
        'tortik_request_count',
        'Counter of requests processed by the tortik library',
        ['method', 'endpoint'],
        registry = registry
    )

    PROCESSING_TIME = Histogram(
        'tortik_request_processing_seconds',
        'Histogram of processing time (seconds) for tortik requests',
        ['method', 'endpoint', 'code'],
        buckets=[0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 30.0],
        registry=registry
    )

def count_request(method, endpoint):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()


def observe_processing_time(response, code):
    method = None
    endpoint = None
    request_time = None
    if response is HTTPServerRequest:
        method = response.method
        endpoint = response.uri
        request_time = time.time() - response._start_time
    else:
        method = response.request.method
        endpoint = response.request.uri
        code = response.code
        request_time = response.request_time * 1000.0

    PROCESSING_TIME.labels(method=method, endpoint=endpoint, code=code).observe(float(request_time))