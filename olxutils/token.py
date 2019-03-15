from __future__ import unicode_literals

import logging

import requests


class TokenHelperException(Exception):
    pass


class TokenHelper(object):

    TOKEN_URL_FORMAT = '%s/oauth2/access_token'

    def __init__(self, url, client_id, client_secret):
        self.token_url = self.TOKEN_URL_FORMAT % url
        self.client_id = client_id
        self.client_secret = client_secret

    def fetch_token(self):
        if not self.client_id:
            raise TokenHelperException('No client ID specified.')
        if not self.client_secret:
            raise TokenHelperException('No client secret specified.')
        request_data = {
            'grant_type': 'client_credentials',
            'token_type': 'jwt',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        r = requests.post(self.token_url,
                          data=request_data)
        # Raise an HTTPError if we didn't get an OK response
        r.raise_for_status()
        logging.debug("Request took %s to complete" % r.elapsed)

        json_result = r.json()
        logging.debug("Request returned JSON result %s" % json_result)

        self.token = json_result['access_token']
        return self.token
