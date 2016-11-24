import json

import pytest
import requests


def pytest_addoption(parser):
    parser.addoption('--tested-url',
                     action='store',
                     default='https://python-qa-tech-test.herokuapp.com',
                     help='base url of the tested api')


@pytest.fixture(scope='session')
def base_url(request):
    base = request.config.getoption('--tested-url')
    if base.endswith('/'):
        return base[:-1]
    return base


@pytest.fixture(scope='session')
def session():
    return requests.Session()


@pytest.fixture(scope='session')
def http(base_url, session):
    def request_(request_path, *args, **kwargs):
        method, url = request_path.split(' ')
        url = '{}{}'.format(base_url, url)
        wrap_json_data(kwargs)

        req = requests.Request(method, url, *args, **kwargs)
        prepared_request = req.prepare()
        print(format_as_curl(prepared_request))

        return session.send(prepared_request)
    return request_


# Wrapping of the json data based on what the PATCH endpoint is accepting
def wrap_json_data(request_parameters):
    try:
        json_data = request_parameters['json']
    except KeyError:
        return
    data = 'json_data={}'.format(json.dumps(json_data))
    request_parameters['data'] = data


def format_as_curl(req):
    command = 'curl -X {method}{headers}{data} {uri}'
    tokens = {'method': req.method, 'uri': req.url}

    if req.body:
        tokens['data'] = " -d '{}'".format(req.body)
        # Old style from encoding content-type header needed
        req.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    else:
        tokens['data'] = ""

    if req.headers:
        headers = [' -H {}:{}'.format(*header)
                   for header in req.headers.items()]
        tokens['headers'] = ''.join(headers)
    else:
        tokens['headers'] = ''

    return command.format(**tokens)
