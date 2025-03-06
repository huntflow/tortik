from prometheus_client import Counter, Gauge, Histogram, Summary

REQUEST_COUNT = Counter(
    'tortik_request_count',
    'Counter of requests processed by the tortik library',
    ['method', 'endpoint']
)

PROCESSING_TIME = Histogram(
    'tortik_request_processing_seconds',
    'Histogram of processing time (seconds) for tortik requests',
    ['operation'],
    buckets=[0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 30.0]
)


def count_request(method, endpoint):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()


def observe_processing_time(response):
    PROCESSING_TIME.labels(method=response.request.method, endpoint=response.request.url, code=response.code).observe(int(response.request_time * 1000.0))