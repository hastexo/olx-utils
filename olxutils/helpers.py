# -*- coding: utf-8 -*-
""" Custom Mako helpers """

import textwrap
import markdown2
import codecs

from os import environ
from swiftclient.utils import generate_temp_url


class OLXHelpers(object):
    """
    OLX helper methods.

    """
    @staticmethod
    def suffix(s):
        return u' ({})'.format(s) if s else u''

    @staticmethod
    def date(d):
        return d.strftime('%Y-%m-%dT%H:%M:%SZ')

    @staticmethod
    def markdown(content, extras=None):
        # Fix up whitespace.
        if content[0] == u"\n":
            content = content[1:]
        content.rstrip()
        content = textwrap.dedent(content)

        # Default extras
        if extras is None:
            extras = [
                "fenced-code-blocks",
                "footnotes",
                "tables",
                "use-file-vars"
            ]

        return markdown2.markdown(content,
                                  extras=extras)

    @classmethod
    def markdown_file(cls, filename, extras=None):
        content = ''
        with codecs.open(filename, 'r', encoding="utf-8") as f:
            content = f.read()
        return cls.markdown(content,
                            extras=extras)

    @staticmethod
    def swift_tempurl(path, date):
        swift_endpoint=environ.get('SWIFT_ENDPOINT')
        swift_path=environ.get('SWIFT_PATH')
        swift_tempurl_key=environ.get('SWIFT_TEMPURL_KEY')

        assert(swift_endpoint)
        assert(swift_path)
        assert(swift_tempurl_key)

        path = u"{}{}".format(swift_path, path)
        timestamp = int(date.strftime("%s"))
        temp_url = generate_temp_url(path, timestamp, swift_tempurl_key, 'GET', absolute=True)

        return u"{}{}".format(swift_endpoint, temp_url)
