from olxutils import helpers

from unittest import TestCase


class OLXHelpersTestCase(TestCase):

    def setUp(self):
        self.h = helpers.OLXHelpers()


class SuffixTest(OLXHelpersTestCase):

    def test_expected_suffix(self):
        expected = (('foo', u' (foo)'),
                    ('spam eggs', u' (spam eggs)'),
                    (u'', u''),
                    ('', u''),
                    (None, u''),
                    (False, u''))
        for t in expected:
            self.assertEqual(self.h.suffix(t[0]),
                             t[1])


class MarkdownTest(OLXHelpersTestCase):

    def test_basic_markdown(self):
        extras = []
        expected = (('**foo**', u'<p><strong>foo</strong></p>\n'),
                    ('*bar*', u'<p><em>bar</em></p>\n'),
                    ('*baz*', u'<p><em>baz</em></p>\n'))

        for t in expected:
            self.assertEqual(self.h.markdown(t[0], extras),
                             t[1])

    def test_strip_whitespace(self):
        extras = []
        expected = (('\n*bar*', u'<p><em>bar</em></p>\n'),
                    ('\nspam', u'<p>spam</p>\n'),
                    ('\n*bar*   ', u'<p><em>bar</em></p>\n'),
                    ('\nspam    ', u'<p>spam</p>\n'))

        for t in expected:
            self.assertEqual(self.h.markdown(t[0], extras),
                             t[1])
