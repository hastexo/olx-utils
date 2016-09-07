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
    parser = argparse.ArgumentParser(description="Create a new course run")

    def valid_date(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except ValueError:
            msg = "Not a valid date: '{0}'.".format(s)
            raise argparse.ArgumentTypeError(msg)

    parser.add_argument('-b', "--create-branch",
        action="store_true",
        help="Create a new 'run/NAME' git branch, add changed files, and commit them."
    )
    parser.add_argument('-p', "--public",
        action="store_true",
        help="Make the course run public"
    )
    parser.add_argument('-s', "--suffix",
        help="The run name suffix"
    )
    parser.add_argument("name", help="The run identifier")
    parser.add_argument("start_date",
        type=valid_date,
        help="When the course run starts (YYYY-MM-DD)"
    )
    parser.add_argument("end_date",
        type=valid_date,
        help="When the course run ends (YYYY-MM-DD)"
    )

    opts = parser.parse_args()

    if opts.name == "_base":
        message = "This run name is reserved.  Please choose another one."
        parser.error(message)

    if opts.end_date < opts.start_date:
        message = "End date [{:%Y-%m-%d}] must be greater than or equal to start date [{:%Y-%m-%d}]."
        parser.error(message.format(opts.end_date, opts.start_date))

    # Create a git branch
    if opts.create_branch:
        try:
            check_call("git rev-parse --verify run/{}".format(opts.name), shell=True)
        except CalledProcessError:
            pass
        else:
            message = (
                "The target git branch already exists.  Please delete it and try again.\n"
                "You can do so with: \n"
                "\n"
                "git branch -d run/{}\n"
            )
            sys.stderr.write(message.format(opts.name))
            sys.exit(1)

        try:
            check_call("git checkout -b run/{}".format(opts.name), shell=True)
        except CalledProcessError:
            message = "Error creating branch 'run/{}'\n"
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
        check_call("ln -sf _base policies/{}".format(opts.name), shell=True)
    except CalledProcessError:
        sys.stderr.write("Error creating policies symlink.\n")
        sys.exit(1)

    if opts.create_branch:
        # Git add the changed files and commit them.
        try:
            check_call("git add .", shell=True)
            check_call("git commit -m 'New run: {}'".format(opts.name), shell=True)
        except CalledProcessError:
            sys.stderr.write("Error commiting new run.\n")
            sys.exit(1)

    sys.stderr.write("All done!\n")

    if opts.create_branch:
        message = (
            "\n"
            "To push this new branch upstream, run:\n"
            "\n"
            "$ git push -u origin run/{}\n"
            "\n"
            "To switch back to master, run:\n"
            "\n"
            "$ git checkout master\n"
        )
        sys.stderr.write(message.format(opts.name))
