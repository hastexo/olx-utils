# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import fnmatch
import codecs

from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions


class OLXTemplateException(Exception):
    pass


class OLXTemplates(object):
    """
    Renders OLX templates.

    """
    OLX_DIRS = [
        ("static/markdown", "md"),
        ("static/presentation", "html"),
        ("about", "html"),
        ("chapter", "xml"),
        ("course", "xml"),
        ("discussion", "xml"),
        ("html", "html"),
        ("html", "xml"),
        ("info", "html"),
        ("policies", "json"),
        ("problem", "xml"),
        ("sequential", "xml"),
        ("tabs", "xml"),
        ("vertical", "xml"),
        ("video", "xml"),
    ]

    IMPORTS = [
        "from olxutils.helpers import OLXHelpers as olx_helpers",
    ]

    LOOKUP_DIRS = [
        "include",
        "templates",
        "mako",
        "mako_templates",
        os.path.join("mako", "templates"),
        os.path.join(os.path.abspath(os.path.dirname(__file__)),
                     "templates"),
    ]

    MODULES_DIRS = [
        "include",
        "modules",
        "mako",
        "mako_modules",
        os.path.join("mako", "modules"),
    ]

    DEFAULT_FILTERS = [
        "unicode",
        "trim",
    ]

    context = {}

    lookup = None

    def __init__(self, context):
        self.context = context
        self.lookup = TemplateLookup(
            directories=self.LOOKUP_DIRS,
            imports=self.IMPORTS,
            default_filters=self.DEFAULT_FILTERS,
            input_encoding='utf-8',
        )

        # Add custom module directories to python path
        cwd = os.getcwd()
        for module_dir in self.MODULES_DIRS:
            path = os.path.join(cwd, module_dir)
            sys.path.append(path)

    def render(self):
        templates = ['course.xml']
        for directory, filetype in self.OLX_DIRS:
            templates.extend(self._find_templates(directory, filetype))

        try:
            self._render_templates(templates)
        except:  # noqa: E722
            message = exceptions.text_error_template().render()
            raise OLXTemplateException(message)

    def _find_templates(self, directory, filetype):
        matches = []
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, '*.' + filetype):
                matches.append(os.path.join(root, filename))
        return matches

    def _render_templates(self, templates):
        for filename in templates:
            template = Template(
                filename=filename,
                lookup=self.lookup,
                imports=self.IMPORTS,
                default_filters=self.DEFAULT_FILTERS,
                input_encoding='utf-8',
            )
            context = self.context.copy()
            basename = os.path.basename(filename)
            stripped = os.path.splitext(basename)[0]
            context['filename'] = stripped
            rendered = template.render_unicode(**context)

            # Remove symlink
            if os.path.islink(filename):
                os.unlink(filename)

            with codecs.open(filename, 'w', 'utf-8') as f:
                f.write(rendered)
