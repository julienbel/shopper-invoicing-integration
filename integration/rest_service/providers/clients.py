from __future__ import unicode_literals

from typing import Dict, Union

import requests
from flask import Flask
from flask_caching import Cache
from requests import HTTPError
from six.moves.urllib.parse import urljoin

from integration.rest_service.providers import exceptions

config = {"DEBUG": True, "CACHE_TYPE": "simple", "CACHE_DEFAULT_TIMEOUT": 300}
app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)


class GenericAPIClient(object):
    host = None
    version = None
    client: requests.Session = None

    def __init__(self):
        self.initialize_client()

    def initialize_client(self):
        self.client = requests.Session()
        self._set_headers()

    def refresh_headers(self):
        self._set_headers(force_refresh=True)

    def _set_headers(self, force_refresh=False):
        if force_refresh:
            headers = self.get_headers()
        else:
            headers = cache.get(f"shopper-payments-{self.base_url}")

            if not headers:
                headers = self.get_headers()
                cache.set(f"shopper-payments-{self.base_url}", headers)
        self.client.headers = headers

    def get_headers(self) -> Dict[str, str]:
        return dict()

    @property
    def base_url(self) -> str:
        if self.version:
            return urljoin(self.host, self.version + "/")
        return self.host

    def handle_error(self, response):
        if response.status_code == 400:
            raise exceptions.BadRequestAPIException(
                code=response.status_code, error_message=response.content
            )
        elif response.status_code == 401:
            raise exceptions.UnauthorizedAPIException(
                code=response.status_code, error_message=response.content
            )
        elif response.status_code == 403:
            raise exceptions.ForbiddenAPIException(
                code=response.status_code, error_message=response.content
            )
        elif response.status_code == 404:
            raise exceptions.NotFoundAPIException(
                code=response.status_code, error_message=response.content
            )
        elif response.status_code == 408:
            raise exceptions.TimeoutAPIException(
                code=response.status_code, error_message=response.content
            )
        elif response.status_code == 422:
            raise exceptions.UnprocessableEntityAPIException(
                code=response.status_code, error_message=response.content
            )
        else:
            raise exceptions.UnhandledErrorAPIException(
                code=response.status_code, error_message=response.content
            )

    def request(
            self,
            url: str,
            method: str,
            data: Dict[str, Union[str, int, Dict]] = None,
            json: Dict[str, Union[str, int, Dict]] = None,
            params: Dict[str, Union[str, int, Dict]] = None,
            max_retries: int = 3,
            timeout: int = 5,
    ) -> Dict[str, Union[str, int, Dict]]:

        try:
            response = self.client.request(
                method, url, data=data, json=json, params=params, timeout=timeout
            )
            response.raise_for_status()
        except requests.exceptions.Timeout as e:
            raise exceptions.TimeoutAPIException(
                error_message=str(e)
            )
        except HTTPError:
            if response.status_code in [401, 403] and max_retries and max_retries > 0:
                self.refresh_headers()
                return self.request(
                    url=url,
                    method=method,
                    data=data,
                    json=json,
                    params=params,
                    max_retries=max_retries - 1,
                )
            self.handle_error(response)
            if response.status_code == 200 and not response.content:
                raise exceptions.NotFoundAPIException
        return response.json()
