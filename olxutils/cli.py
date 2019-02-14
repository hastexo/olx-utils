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
from subprocess import check_call

from olxutils.templates import OLXTemplates, OLXTemplateException
from olxutils.git import GitHelper, GitHelperException

# Under which name do we expect the CLI to be generally called?
CANONICAL_COMMAND_NAME = 'olx'


class CLIException(Exception):
    pass


class CLI(object):

    def parse_args(self, args=sys.argv[1:]):

        def valid_date(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d")
            except ValueError:
                msg = "Not a valid date: '{0}'.".format(s)
                raise ArgumentTypeError(msg)

        parser = ArgumentParser(prog=CANONICAL_COMMAND_NAME,
                                description="Open Learning XML (OLX) utility")

        subparsers = parser.add_subparsers(dest='subcommand')
        new_run_help = 'Prepare a local source tree for a new course run'
        new_run_parser = subparsers.add_parser('new-run',
                                               help=new_run_help)

        new_run_parser.add_argument('-b', "--create-branch",
                                    action="store_true",
                                    help=("Create a new 'run/NAME' "
                                          "git branch, add changed files, "
                                          "and commit them."))
        new_run_parser.add_argument('-p', "--public",
                                    action="store_true",
                                    help="Make the course run public")
        new_run_parser.add_argument('-s', "--suffix",
                                    help="The run name suffix")
        new_run_parser.add_argument("name",
                                    help="The run identifier")
        new_run_parser.add_argument("start_date",
                                    type=valid_date,
                                    help="When the course run starts "
                                         "(YYYY-MM-DD)")
        new_run_parser.add_argument("end_date",
                                    type=valid_date,
                                    help="When the course run ends "
                                         "(YYYY-MM-DD)")

        self.opts = parser.parse_args(args)

        if self.opts.name == "_base":
            message = "This run name is reserved.  Please choose another one."
            new_run_parser.error(message)

        if self.opts.end_date < self.opts.start_date:
            message = ("End date [{:%Y-%m-%d}] "
                       "must be greater than or equal "
                       "to start date [{:%Y-%m-%d}].")
            new_run_parser.error(message.format(self.opts.end_date,
                                                self.opts.start_date))

    def render_templates(self):
        # Render templates
        templates = OLXTemplates({
            "run_name": self.opts.name,
            "start_date": self.opts.start_date,
            "end_date": self.opts.end_date.replace(hour=23,
                                                   minute=59,
                                                   second=59),
            "run_suffix": self.opts.suffix,
            "is_public": self.opts.public,
        })

        templates.render()

    def create_symlinks(self):
        # Create symlink for policies
        check_call("ln -sf _base policies/{}".format(self.opts.name),
                   shell=True)

    def new_run(self):
        if self.opts.create_branch:
            helper = GitHelper(run=self.opts.name)

        try:
            if self.opts.create_branch:
                helper.create_branch()

            self.render_templates()

            self.create_symlinks()

            if self.opts.create_branch:
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

        self.parse_args(argv[1:])

        # We could use getattr() here, but even with all our
        # safeguards in place subcommand is still user input. So just
        # enumerate and repeat the method names here.
        if self.opts.subcommand == 'new-run':
            self.new_run()


def main(argv=sys.argv):
    try:
        CLI().main(argv)
    except CLIException as c:
        sys.stderr.write(str(c))
        sys.exit(1)


if __name__ == "__main__":
    main()
