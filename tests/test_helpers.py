from __future__ import unicode_literals

import os

from olxutils import helpers

from unittest import TestCase

from datetime import datetime

from swiftclient.utils import generate_temp_url

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class OLXHelpersTestCase(TestCase):

    def setUp(self):
        self.h = helpers.OLXHelpers()


class SuffixTest(OLXHelpersTestCase):

    def test_expected_suffix(self):
        expected = (('foo', ' (foo)'),
                    ('spam eggs', ' (spam eggs)'),
                    ('', ''),
                    ('', ''),
                    (None, ''),
                    (False, ''))
        for t in expected:
            self.assertEqual(self.h.suffix(t[0]),
                             t[1])


class MarkdownTest(OLXHelpersTestCase):

    def test_basic_markdown(self):
        expected = (('**foo**', '<p><strong>foo</strong></p>\n'),
                    ('*bar*', '<p><em>bar</em></p>\n'),
                    ('*baz*', '<p><em>baz</em></p>\n'))

        for t in expected:
            # No extras
            self.assertEqual(self.h.markdown(t[0], extras=[]),
                             t[1])
            # Default set of extras
            self.assertEqual(self.h.markdown(t[0]),
                             t[1])

    def test_strip_whitespace(self):
        expected = (('\n*bar*', '<p><em>bar</em></p>\n'),
                    ('\nspam', '<p>spam</p>\n'),
                    ('\n*bar*   ', '<p><em>bar</em></p>\n'),
                    ('\nspam    ', '<p>spam</p>\n'))

        for t in expected:
            # No extras
            self.assertEqual(self.h.markdown(t[0], extras=[]),
                             t[1])
            # Default set of extras
            self.assertEqual(self.h.markdown(t[0]),
                             t[1])

    def test_markdown_file(self):
        extras = ['footnotes', 'fenced-code-blocks']

        for e in extras:
            input_file = os.path.join(os.path.dirname(__file__),
                                      '%s.md' % e)
            output_file = os.path.join(os.path.dirname(__file__),
                                       '%s.html' % e)

            with open(output_file, 'r') as o:
                self.assertEqual(self.h.markdown_file(input_file,
                                                      extras=[e]),
                                 o.read())


class SwiftTempURLTest(OLXHelpersTestCase):

    def test_swift_tempurl(self):
        endpoint = 'https://swift.example.com'
        swift_path = '/v1/AUTH_bd1de33b3eae4287800cfe59f53b6fde'
        path = '/container/object'
        key = 'foobar'
        expiry = datetime(2019, 1, 1)
        timestamp = int(expiry.strftime('%s'))

        expected_tempurl = ''.join([
            endpoint,
            generate_temp_url(swift_path + path,
                              timestamp,
                              key,
                              'GET',
                              absolute=True)
        ])

        with patch.dict(os.environ,
                        {'SWIFT_ENDPOINT': endpoint,
                         'SWIFT_PATH': swift_path,
                         'SWIFT_TEMPURL_KEY': key}):
            tempurl = self.h.swift_tempurl(path, expiry)
            self.assertEqual(tempurl, expected_tempurl)
