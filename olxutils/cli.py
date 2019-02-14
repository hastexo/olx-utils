#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
New course run
"""

import sys

from argparse import ArgumentParser, ArgumentTypeError

from datetime import datetime
from subprocess import check_call, CalledProcessError
from mako import exceptions

from olxutils.templates import OLXTemplates


class CLI(object):

    def parse_args(self, args=sys.argv[1:]):

        def valid_date(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d")
            except ValueError:
                msg = u"Not a valid date: '{0}'.".format(s)
                raise ArgumentTypeError(msg)

        parser = ArgumentParser(description=u"Create a new course run")

        parser.add_argument('-b', "--create-branch",
                            action="store_true",
                            help=(u"Create a new 'run/NAME' "
                                  u"git branch, add changed files, "
                                  u"and commit them."))
        parser.add_argument('-p', "--public",
                            action="store_true",
                            help=u"Make the course run public")
        parser.add_argument('-s', "--suffix",
                            help=u"The run name suffix")
        parser.add_argument("name",
                            help=u"The run identifier")
        parser.add_argument("start_date",
                            type=valid_date,
                            help=u"When the course run starts (YYYY-MM-DD)")
        parser.add_argument("end_date",
                            type=valid_date,
                            help=u"When the course run ends (YYYY-MM-DD)")

        self.opts = parser.parse_args(args)

        if self.opts.name == "_base":
            message = u"This run name is reserved.  Please choose another one."
            parser.error(message)

        if self.opts.end_date < self.opts.start_date:
            message = (u"End date [{:%Y-%m-%d}] "
                       u"must be greater than or equal "
                       u"to start date [{:%Y-%m-%d}].")
            parser.error(message.format(self.opts.end_date,
                                        self.opts.start_date))

    def check_branch(self):
        try:
            check_call(u"git rev-parse --verify run/{}".format(self.opts.name),
                       shell=True)
        except CalledProcessError:
            pass
        else:
            message = (
                u"The target git branch already exists.  "
                u"Please delete it and try again.\n"
                u"You can do so with: \n"
                u"\n"
                u"git branch -d run/{}\n"
            )
            sys.stderr.write(message.format(self.opts.name))
            sys.exit(1)

        try:
            check_call(u"git checkout -b run/{}".format(self.opts.name),
                       shell=True)
        except CalledProcessError:
            message = u"Error creating branch 'run/{}'\n"
            sys.stderr.write(message.format(self.opts.name))
            sys.exit(1)

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

        try:
            templates.render()
        except:  # noqa: E722
            message = exceptions.text_error_template().render()
            sys.stderr.write(message)
            sys.exit(1)

    def create_symlinks(self):
        # Create symlink for policies
        try:
            check_call(u"ln -sf _base policies/{}".format(self.opts.name),
                       shell=True)
        except CalledProcessError:
            sys.stderr.write(u"Error creating policies symlink.\n")
            sys.exit(1)

    def create_branch(self):
        # Git add the changed files and commit them.
        try:
            check_call(u"git add .",
                       shell=True)
            check_call(u"git commit -m 'New run: {}'".format(self.opts.name),
                       shell=True)
        except CalledProcessError:
            sys.stderr.write(u"Error commiting new run.\n")
            sys.exit(1)

    def show_branch_message(self):
        message = (
            u"\n"
            u"To push this new branch upstream, run:\n"
            u"\n"
            u"$ git push -u origin run/{}\n"
            u"\n"
            u"To switch back to master, run:\n"
            u"\n"
            u"$ git checkout master\n"
        )
        sys.stderr.write(message.format(self.opts.name))

    def main(self, argv=sys.argv):
        self.parse_args(argv[1:])

        if self.opts.create_branch:
            self.check_branch()

        self.render_templates()

        self.create_symlinks()

        if self.opts.create_branch:
            self.create_branch()
            self.show_branch_message()

        sys.stderr.write(u"All done!\n")


def main(argv=sys.argv):
    CLI().main(argv)


if __name__ == "__main__":
    main()
