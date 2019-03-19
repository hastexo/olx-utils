#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
New course run
"""
from __future__ import unicode_literals

import sys

import os

import warnings

from argparse import ArgumentParser, ArgumentTypeError

from datetime import datetime

from olxutils import __version__
from olxutils.templates import OLXTemplates, OLXTemplateException
from olxutils.git import GitHelper, GitHelperException
from olxutils.archive import ArchiveHelper

# Under which name do we expect the CLI to be generally called?
CANONICAL_COMMAND_NAME = 'olx'


class CLIException(Exception):
    pass


class CLI(object):

    def __init__(self):
        def valid_date(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d")
            except ValueError:
                msg = "Not a valid date: '{0}'.".format(s)
                raise ArgumentTypeError(msg)

        parser = ArgumentParser(prog=CANONICAL_COMMAND_NAME,
                                description="Open Learning XML (OLX) utility")

        subparsers = parser.add_subparsers(dest='subcommand')
        parser.add_argument('-V', '--version',
                            action='version',
                            help="show version",
                            version='%(prog)s ' + __version__)

        nr_help = 'Prepare a local source tree for a new course run'
        nr_parser = subparsers.add_parser('new-run',
                                          help=nr_help)

        nr_parser.add_argument('-b', "--create-branch",
                               action="store_true",
                               help=("Create a new 'run/NAME' "
                                     "git branch, add changed files, "
                                     "and commit them."))
        nr_parser.add_argument('-p', "--public",
                               action="store_true",
                               help="Make the course run public")
        nr_parser.add_argument('-s', "--suffix",
                               help="The run name suffix")
        nr_parser.add_argument("name",
                               help="The run identifier")
        nr_parser.add_argument("start_date",
                               type=valid_date,
                               help="When the course run starts "
                               "(YYYY-MM-DD)")
        nr_parser.add_argument("end_date",
                               type=valid_date,
                               help="When the course run ends "
                               "(YYYY-MM-DD)")

        a_help = 'Create an archive for import into Open edX Studio'
        a_parser = subparsers.add_parser('archive',
                                         help=a_help)
        a_parser.add_argument('-r', '--root-directory',
                              default='.',
                              help="Root directory of course files")

        self.parser = parser

    def parse_args(self, args=sys.argv[1:]):

        opts = self.parser.parse_args(args)

        # Return the passed-in options as a dictionary
        return vars(opts)

    def render_templates(self,
                         name,
                         start_date,
                         end_date,
                         suffix=None,
                         public=False):
        # Render templates
        templates = OLXTemplates({
            "run_name": name,
            "start_date": start_date,
            "end_date": end_date.replace(hour=23,
                                         minute=59,
                                         second=59),
            "run_suffix": suffix,
            "is_public": public,
        })

        templates.render()

    def create_symlinks(self, name):
        # Create symlink for policies
        os.symlink('_base',
                   'policies/{}'.format(name))

    def new_run(self,
                name,
                start_date,
                end_date,
                suffix=None,
                create_branch=False,
                public=False):

        if name == "_base":
            message = ("This run name is reserved. "
                       "Please choose another one.")
            raise CLIException(message)
        if end_date < start_date:
            message = ("End date [{:%Y-%m-%d}] "
                       "must be greater than or equal "
                       "to start date [{:%Y-%m-%d}].")
            raise CLIException(message.format(end_date,
                                              start_date))

        if create_branch:
            helper = GitHelper(run=name)

        try:
            if create_branch:
                helper.create_branch()

            self.render_templates(name,
                                  start_date,
                                  end_date,
                                  suffix,
                                  public)

            self.create_symlinks(name)

            if create_branch:
                helper.add_to_branch()
                sys.stderr.write(helper.message)

        except CLIException:
            raise
        except GitHelperException as g:
            # Once we drop Python 2 support, this should really be
            # "raise CLIException from g"
            raise CLIException(str(g))
        except OLXTemplateException as t:
            # Again, this should be
            # "raise CLIException('Failed to render templates:') from t
            raise CLIException('Failed to render templates:\n' + str(t))

        sys.stderr.write("All done!\n")

    def archive(self, root_directory='.'):
        base_name = "archive"
        helper = ArchiveHelper(root_directory,
                               base_name)

        helper.make_archive()

    def main(self, argv=sys.argv):
        """Main CLI entry point.

        Checks how we were invoked: either we're being called as just
        "olx" or "__main__", in which case we can pass the subcommands
        right through to the argument parser and its subparser(s).

        Or we were called the old way (as olx-new-run), in which case we
        mangle the system arguments to inject the subcommand.

        Or we were called the *really* old way (as new_run.py), in which
        case we pretend we got "new-run" as the subcommand.
        """
        prefix = '%s-' % CANONICAL_COMMAND_NAME
        command = argv[0]

        if os.path.basename(command) == 'new_run.py':
            warnings.warn('"new_run.py" is deprecated, '
                          'use "%s new-run" instead' % CANONICAL_COMMAND_NAME,
                          FutureWarning)
            # Mangle the command into "olx new-run".
            argv[0] = os.path.join(os.path.dirname(command),
                                   CANONICAL_COMMAND_NAME)
            argv.insert(1, 'new-run')
        elif os.path.basename(command).startswith(prefix):
            # Drop the prefix, i.e. turn "olx-foo" into "olx foo".
            argv[0] = os.path.join(os.path.dirname(command),
                                   CANONICAL_COMMAND_NAME)
            argv.insert(1,
                        os.path.basename(command).replace(prefix, ''))

        opts = self.parse_args(argv[1:])

        # Invoke the subcommand, passing the parsed command line
        # options in as kwargs
        getattr(self, opts.pop('subcommand').replace('-', '_'))(**opts)


def main(argv=sys.argv):
    try:
        CLI().main(argv)
    except CLIException as c:
        sys.stderr.write(str(c))
        sys.exit(1)


if __name__ == "__main__":
    main()
