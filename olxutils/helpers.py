# -*- coding: utf-8 -*-
""" Custom Mako helpers """


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
