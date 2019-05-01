from __future__ import unicode_literals

from olxutils.token import TokenHelper, TokenHelperException

import requests_mock

from unittest import TestCase


class TokenHelperTestCase(TestCase):

    FAKE_CMS_URL = 'https://cms.pohgha9thaom4ii7.6t8'

    def test_get_token(self):
        client_id = 'foo'
        client_secret = 'bar'
        expected_token = 'blatch'
        post_uri = '%s/oauth2/access_token' % self.FAKE_CMS_URL

        helper = TokenHelper(self.FAKE_CMS_URL,
                             client_id,
                             client_secret)

        with requests_mock.Mocker() as m:
            m.register_uri('POST',
                           post_uri,
                           json={'access_token': expected_token})
            token = helper.fetch_token()
            self.assertTrue(m.called)
            self.assertEqual(token, expected_token)

    def test_get_token_missing_id(self):
        client_id = None
        client_secret = 'bar'

        helper = TokenHelper(self.FAKE_CMS_URL,
                             client_id,
                             client_secret)

        with self.assertRaises(TokenHelperException):
            helper.fetch_token()

    def test_get_token_missing_secret(self):
        client_id = 'foo'
        client_secret = None

        helper = TokenHelper(self.FAKE_CMS_URL,
                             client_id,
                             client_secret)

        with self.assertRaises(TokenHelperException):
            helper.fetch_token()
