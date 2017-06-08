import os

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
        expected = (('**foo**', u'<p><strong>foo</strong></p>\n'),
                    ('*bar*', u'<p><em>bar</em></p>\n'),
                    ('*baz*', u'<p><em>baz</em></p>\n'))

        for t in expected:
            # No extras
            self.assertEqual(self.h.markdown(t[0], extras=[]),
                             t[1])
            # Default set of extras
            self.assertEqual(self.h.markdown(t[0]),
                             t[1])

    def test_strip_whitespace(self):
        expected = (('\n*bar*', u'<p><em>bar</em></p>\n'),
                    ('\nspam', u'<p>spam</p>\n'),
                    ('\n*bar*   ', u'<p><em>bar</em></p>\n'),
                    ('\nspam    ', u'<p>spam</p>\n'))

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
