from prometheus_client import Counter, Histogram

REGISTRY = None

def init_metrics(registry):
    global REGISTRY, REQUEST_COUNT, PROCESSING_TIME

    REGISTRY = registry

    REQUEST_COUNT = Counter(
        'tortik_request_count',
        'Counter of requests processed by the tortik library',
        ['method', 'endpoint'],
        registry = REGISTRY
    )

    PROCESSING_TIME = Histogram(
        'tortik_request_processing_seconds',
        'Histogram of processing time (seconds) for tortik requests',
        ['method', 'endpoint', 'code'],
        buckets=[0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 30.0],
        registry=REGISTRY
    )

class _DummyMetric:
    def __init__(self):
        pass

    def labels(self, **kwargs):
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


def count_request(method, endpoint):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()


def observe_processing_time(response):
    PROCESSING_TIME.labels(method=response.request.method, endpoint=response.request.url, code=response.code).observe(int(response.request_time * 1000.0))