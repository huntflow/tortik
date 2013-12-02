# _*_ coding: utf-8 _*_
import httplib

# Additional HTTP Status Codes - http://tools.ietf.org/html/rfc6585
PRECONDITION_REQUIRED = 428
TOO_MANY_REQUESTS = 429
REQUEST_HEADER_FIELDS_TOO_LARGE = 431
NETWORK_AUTHENTICATION_REQUIRED = 511

ADDITIONAL_RESPONSE_CODES = {
    PRECONDITION_REQUIRED: 'Precondition Required',
    TOO_MANY_REQUESTS: 'Too Many Requests',
    REQUEST_HEADER_FIELDS_TOO_LARGE: 'Request Header Fields Too Large',
    NETWORK_AUTHENTICATION_REQUIRED: 'Network Authentication Required',
}


def check_status_code(status_code):
    return status_code in httplib.responses or status_code in ADDITIONAL_RESPONSE_CODES


def get_status_code_message(status_code):
    if check_status_code(status_code):
        if status_code in httplib.responses:
            return httplib.responses[status_code]
        return ADDITIONAL_RESPONSE_CODES[status_code]
    else:
        raise ValueError('Unknown status code "{0}"'.format(status_code))
