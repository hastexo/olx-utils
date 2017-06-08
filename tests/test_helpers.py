from olxutils import helpers

from unittest import TestCase


class SuffixTest(TestCase):

    def test_expected_suffix(self):
        expected = (('foo', u' (foo)'),
                    ('spam eggs', u' (spam eggs)'),
                    (u'', u''),
                    ('', u''),
                    (None, u''))
        for t in expected:
            self.assertEqual(helpers.suffix(t[0]),
                             t[1])
                                            


