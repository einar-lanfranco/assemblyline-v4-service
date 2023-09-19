import logging
from collections import OrderedDict
from multiprocessing import Process

import pytest
import requests_mock
from assemblyline_v4_service.common import helper
from assemblyline_v4_service.common.api import *
from requests import ConnectionError, HTTPError, Session, Timeout, exceptions

SERVICE_CONFIG_NAME = "service_manifest.yml"
TEMP_SERVICE_CONFIG_PATH = os.path.join("/tmp", SERVICE_CONFIG_NAME)


def setup_module():
    if not os.path.exists(TEMP_SERVICE_CONFIG_PATH):
        open_manifest = open(TEMP_SERVICE_CONFIG_PATH, "w")
        open_manifest.write("\n".join([
            "name: Sample",
            "version: sample",
            "docker_config:",
            "    image: sample",
            "heuristics:",
            "  - heur_id: 17",
            "    name: blah",
            "    description: blah",
            "    filetype: '*'",
            "    score: 250",
        ]))
        open_manifest.close()


def teardown_module():
    if os.path.exists(TEMP_SERVICE_CONFIG_PATH):
        os.remove(TEMP_SERVICE_CONFIG_PATH)


def test_development_mode():
    assert DEVELOPMENT_MODE is True


def test_serviceapierror_init():
    # Init with None
    sae = ServiceAPIError(None, None)
    assert sae.api_response is None
    assert sae.api_version is None
    assert sae.status_code is None

    # Init with values
    sae = ServiceAPIError("message", 200, {"blah": "blah"}, "v4")
    assert sae.api_response == {"blah": "blah"}
    assert sae.api_version == "v4"
    assert sae.status_code == 200


def test_serviceapi_init():
    service_attributes = helper.get_service_attributes()
    sa = ServiceAPI(service_attributes, None)
    assert sa.log is None
    assert sa.service_api_host == DEFAULT_SERVICE_SERVER
    assert isinstance(sa.session, Session)
    assert sa.session.headers.__dict__ == {
        '_store': OrderedDict(
            [
                ('user-agent', ('User-Agent', 'python-requests/2.31.0')),
                ('accept-encoding', ('Accept-Encoding', 'gzip, deflate')),
                ('accept', ('Accept', '*/*')),
                ('connection', ('Connection', 'keep-alive')),
                ('x_apikey', ('X_APIKEY', DEFAULT_AUTH_KEY)),
                ('container_id', ('container_id', 'dev-service')),
                ('service_name', ('service_name', 'Sample')),
                ('service_version', ('service_version', 'sample'))
            ]
        )
    }


def test_service_api_with_retries():
    service_attributes = helper.get_service_attributes()
    log = logging.getLogger('assemblyline')
    sa = ServiceAPI(service_attributes, log)
    with requests_mock.Mocker() as m:
        url = f"{sa.service_api_host}/api/v1/blah/"

        # ConnectionError
        m.get(url, exc=ConnectionError)
        p1 = Process(target=sa._with_retries, args=(sa.session.get, url), name="_with_retries with exception ConnectionError")
        p1.start()
        p1.join(timeout=2)
        p1.terminate()
        assert p1.exitcode is None

        # Timeout
        m.get(url, exc=Timeout)
        p1 = Process(target=sa._with_retries, args=(sa.session.get, url), name="_with_retries with exception ConnectionError")
        p1.start()
        p1.join(timeout=2)
        p1.terminate()
        assert p1.exitcode is None

        # Status code of 200
        m.get(url, status_code=200, json={"api_response": "blah"})
        assert sa._with_retries(sa.session.get, url) == "blah"

        # Status code of 400 and no "api_error_message" key
        m.get(url, status_code=400, json={})
        with pytest.raises(ServiceAPIError):
            sa._with_retries(sa.session.get, url)

        # Status code of 400 and the required keys
        m.get(url, status_code=400, json={"api_error_message": "blah", "api_server_version": "blah", "api_response": "blah"})
        with pytest.raises(ServiceAPIError):
            sa._with_retries(sa.session.get, url)


def test_get_safelist():
    service_attributes = helper.get_service_attributes()
    log = logging.getLogger('assemblyline')
    sa = ServiceAPI(service_attributes, log)
    assert sa.get_safelist() == {}

    # TODO
    # Test not in development mode


def test_lookup_safelist():
    service_attributes = helper.get_service_attributes()
    log = logging.getLogger('assemblyline')
    sa = ServiceAPI(service_attributes, log)
    assert sa.lookup_safelist("qhash") is None

    # TODO
    # Test not in development mode
