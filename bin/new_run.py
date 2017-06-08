#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
New course run
"""

import sys
import argparse

from datetime import datetime
from subprocess import check_call, CalledProcessError
from mako import exceptions

from olxutils.templates import OLXTemplates

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=u"Create a new course run")

    def valid_date(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except ValueError:
            msg = u"Not a valid date: '{0}'.".format(s)
            raise argparse.ArgumentTypeError(msg)

    parser.add_argument('-b', "--create-branch",
                        action="store_true",
                        help=(u"Create a new 'run/NAME' "
                              u"git branch, add changed files, "
                              u"and commit them."))
    parser.add_argument('-p', "--public",
                        action="store_true",
                        help=u"Make the course run public"
    )
    parser.add_argument('-s', "--suffix",
                        type=lambda s: unicode(s, 'utf-8'),
                        help=u"The run name suffix"
    )
    parser.add_argument("name",
                        type=lambda s: unicode(s, 'utf-8'),
                        help=u"The run identifier")
    parser.add_argument("start_date",
                        type=valid_date,
                        help=u"When the course run starts (YYYY-MM-DD)"
    )
    parser.add_argument("end_date",
                        type=valid_date,
                        help=u"When the course run ends (YYYY-MM-DD)"
    )

    opts = parser.parse_args()

    if opts.name == "_base":
        message = u"This run name is reserved.  Please choose another one."
        parser.error(message)

    if opts.end_date < opts.start_date:
        message = (u"End date [{:%Y-%m-%d}] "
                   u"must be greater than or equal "
                   u"to start date [{:%Y-%m-%d}].")
        parser.error(message.format(opts.end_date, opts.start_date))

    # Create a git branch
    if opts.create_branch:
        try:
            check_call(u"git rev-parse --verify run/{}".format(opts.name),
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
            sys.stderr.write(message.format(opts.name))
            sys.exit(1)

        try:
            check_call(u"git checkout -b run/{}".format(opts.name), shell=True)
        except CalledProcessError:
            message = u"Error creating branch 'run/{}'\n"
            sys.stderr.write(message.format(opts.name))
            sys.exit(1)

    # Render templates
    templates = OLXTemplates({
        "run_name": opts.name,
        "start_date": opts.start_date,
        "end_date": opts.end_date.replace(hour=23, minute=59, second=59),
        "run_suffix": opts.suffix,
        "is_public": opts.public,
    })

    try:
        templates.render()
    except:
        message = exceptions.text_error_template().render()
        sys.stderr.write(message)
        sys.exit(1)

    # Create symlink for policies
    try:
        check_call(u"ln -sf _base policies/{}".format(opts.name), shell=True)
    except CalledProcessError:
        sys.stderr.write(u"Error creating policies symlink.\n")
        sys.exit(1)

    if opts.create_branch:
        # Git add the changed files and commit them.
        try:
            check_call(u"git add .",
                       shell=True)
            check_call(u"git commit -m 'New run: {}'".format(opts.name),
                       shell=True)
        except CalledProcessError:
            sys.stderr.write(u"Error commiting new run.\n")
            sys.exit(1)

    sys.stderr.write(u"All done!\n")

    if opts.create_branch:
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
        sys.stderr.write(message.format(opts.name))
