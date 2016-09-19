# -*- coding: utf-8 -*-
""" Custom Mako helpers """

import textwrap
import markdown2


class OLXHelpers(object):
    """
    OLX helper methods.

    """
    @staticmethod
    def suffix(s):
        return ' ({})'.format(s) if s else ''

    @staticmethod
    def date(d):
        return d.strftime('%Y-%m-%dT%H:%M:%SZ')

    @staticmethod
    def markdown(content):
        # Fix up whitespace.
        if content[0] == "\n":
            content = content[1:]
        content.rstrip()
        content = textwrap.dedent(content)

        return markdown2.markdown(content, extras=[
            "code-friendly",
            "fenced-code-blocks",
            "footnotes",
            "tables",
            "use-file-vars",
        ])

    @classmethod
    def markdown_file(cls, filename):
        content = ''
        with open(filename, 'r') as f:
            content = f.read()
        return cls.markdown(content)
