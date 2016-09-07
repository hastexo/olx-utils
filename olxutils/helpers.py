# -*- coding: utf-8 -*-
""" Custom Mako helpers """

def olx_suffix(s):
    return ' ({})'.format(s) if s else ''

def olx_date(d):
    return d.strftime('%Y-%m-%dT%H:%M:%SZ')
