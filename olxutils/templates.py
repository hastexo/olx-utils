# -*- coding: utf-8 -*-

import os
import sys
import fnmatch

from mako.template import Template
from mako.lookup import TemplateLookup

class OLXTemplates(object):
    """
    Renders OLX templates.

    """
    OLX_DIRS = {
        "about": ["html"],
        "chapter": ["xml"],
        "course": ["xml"],
        "discussion": ["xml"],
        "html": ["html", "xml"],
        "info": ["html"],
        "policies": ["json"],
        "problem": ["xml"],
        "sequential": ["xml"],
        "static": ["html", "js", "md"],
        "tabs": ["xml"],
        "vertical": ["xml"],
        "video": ["xml"],
    }

    LOOKUP_DIRS = ["include"]

    MODULES_DIR = "python_modules"

    context = {}

    lookup = None

    def __init__(self, context):
        self.context = context
        self.lookup = TemplateLookup(directories=self.LOOKUP_DIRS)

        # Add custom module directory to python path
        sys.path.append(os.path.join(os.getcwd(), self.MODULES_DIR))

    def render(self):
        templates = ['course.xml']
        for directory, filetypes in self.OLX_DIRS.iteritems():
            templates.extend(self._find_templates(directory, filetypes))

        self._render_templates(templates)

    def _find_templates(self, directory, filetypes):
        matches = []
        for filetype in filetypes:
            for root, dirnames, filenames in os.walk(directory):
                for filename in fnmatch.filter(filenames, '*.' + filetype):
                    matches.append(os.path.join(root, filename))
        return matches

    def _render_templates(self, templates):
        for filename in templates:
            template = Template(
                filename=filename,
                lookup=self.lookup,
                imports=["from olxutils.helpers import olx_date, olx_suffix"]
            )
            rendered = template.render(**self.context)
            with open(filename, 'w') as f:
                f.write(rendered)
