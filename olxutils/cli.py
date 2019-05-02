#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
New course run
"""
from __future__ import print_function, unicode_literals

import sys

import os

import warnings

import logging

from argparse import ArgumentParser, ArgumentTypeError

from datetime import datetime

from olxutils import __version__
from olxutils.templates import OLXTemplates, OLXTemplateException
from olxutils.git import GitHelper, GitHelperException
from olxutils.archive import ArchiveHelper
from olxutils.token import TokenHelper
from olxutils.upload import UploadHelper

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
        parser.add_argument('-v', '--verbose',
                            action='count',
                            dest='verbosity',
                            default=0,
                            help=("verbose output "
                                  "(repeat for increased verbosity)"))
        parser.add_argument('-q', '--quiet',
                            action='store_const',
                            const=-1,
                            default=0,
                            dest='verbosity',
                            help=("quiet output "
                                  "(show errors only)"))

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

        t_help = 'Retrieve an Open edX CMS REST API token'
        t_epilog = ('You can also set the OLX_LMS_URL, '
                    'OLX_LMS_CLIENT_ID, '
                    'and OLX_LMS_CLIENT_SECRET environment variables '
                    'instead of the --url, '
                    '--client-id, and '
                    '--client-secret options.')
        t_parser = subparsers.add_parser('token',
                                         help=t_help,
                                         epilog=t_epilog)
        # Using os.getenv(var) here rather than os.environ, because
        # os.getenv() returns None if the envar is unset, as opposed
        # to os.environ[var] which would return KeyError.
        t_parser.add_argument('--url',
                              default=os.getenv('OLX_LMS_URL'),
                              help='Open edX CMS URL')
        t_parser.add_argument('--client-id',
                              default=os.getenv('OLX_LMS_CLIENT_ID'),
                              metavar='ID',
                              help=('Open edX CMS Django OAuth '
                                    'Toolkit client ID'))
        t_parser.add_argument('--client-secret',
                              default=os.getenv('OLX_LMS_CLIENT_SECRET'),
                              metavar='SECRET',
                              help=('Open edX CMS Django OAuth '
                                    'Toolkit client secret'))

        u_help = 'Upload a course archive into the Open edX content store'
        u_epilog = ('You can also set the OLX_CMS_URL '
                    'and OLX_CMS_TOKEN environment variables '
                    'instead of the --url and '
                    '--token options.')
        u_parser = subparsers.add_parser('upload',
                                         help=u_help,
                                         epilog=u_epilog)
        u_parser.add_argument('--url',
                              help='Open edX CMS URL')
        u_parser.add_argument('--token',
                              help='Open edX REST API token')
        u_parser.add_argument('-f',
                              '--file',
                              required=True,
                              help=('File to be uploaded. '
                                    'This must be a valid Open edX '
                                    'course archive.'))
        u_parser.add_argument('-c',
                              '--course-id',
                              help=('Full Open edX course ID, in '
                                    '"course-v1:org+course+run" form. '
                                    'If unspecified, the course ID is '
                                    'detected from the course.xml file '
                                    'found the course archive.'))
        u_parser.add_argument('--wait',
                              default=False,
                              action='store_true',
                              help=('Wait for the course import '
                                    'to fully complete. If unset, '
                                    'the command returns as soon '
                                    'as the CMS has accepted the upload, '
                                    'and returns a task ID that '
                                    'can subsequently be checked with '
                                    '"%s status".' % CANONICAL_COMMAND_NAME))

        s_help = 'Check the status of a course upload task'
        s_epilog = ('You can also set the OLX_CMS_URL '
                    'and OLX_CMS_TOKEN environment variables '
                    'instead of the --url and '
                    '--token options.')
        s_parser = subparsers.add_parser('status',
                                         help=s_help,
                                         epilog=s_epilog)
        s_parser.add_argument('--url',
                              help='Open edX CMS URL')
        s_parser.add_argument('--token',
                              help='Open edX REST API token')
        s_parser.add_argument('-f',
                              '--file',
                              required=True,
                              help=('File to be uploaded. '
                                    'This must be a valid Open edX '
                                    'course archive.'))
        s_parser.add_argument('-c',
                              '--course-id',
                              help=('Full Open edX course ID, in '
                                    '"course-v1:org+course+run" form. '
                                    'If unspecified, the course ID is '
                                    'detected from the course.xml file '
                                    'found the course archive.'))
        s_parser.add_argument('-t',
                              '--task-id',
                              required=True,
                              help=('Task ID, as returned from '
                                    '%s upload' % CANONICAL_COMMAND_NAME))

        self.parser = parser

        self.setup_logging()

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

        try:
            if create_branch:
                helper = GitHelper(run=name)

                if helper.is_checkout_dirty():
                    raise CLIException(('The local checkout is dirty, '
                                        'please add uncommitted changes.'))

                helper.create_branch()

            self.render_templates(name,
                                  start_date,
                                  end_date,
                                  suffix,
                                  public)

            self.create_symlinks(name)

            if create_branch:
                helper.add_to_branch()
                logging.warn(helper.message)

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

        logging.info("All done!")

    def setup_logging(self):
        env_loglevel = os.getenv('OLX_LOG_LEVEL', 'WARNING').upper()
        loglevel = getattr(logging, env_loglevel)
        logging.basicConfig(level=loglevel,
                            format='%(message)s')

    def apply_verbosity(self, verbosity):
        # Python log levels go from 10 (DEBUG) to 50 (CRITICAL),
        # our verbosity argument goes from -1 (-q) to 2 (-vv).
        # We never want to suppress error and critical messages,
        # and default to the OLX_LOG_LEVEL environment variable,
        # and if *that's* unset, use 30 (WARNING). Hence:
        root = logging.getLogger()
        verbosity = min(verbosity, 2)
        loglevel = root.getEffectiveLevel() - (verbosity * 10)
        root.setLevel(loglevel)

    def archive(self, root_directory='.'):
        base_name = "archive"
        helper = ArchiveHelper(root_directory,
                               base_name)

        helper.make_archive()

    def token(self,
              url=None,
              client_id=None,
              client_secret=None):

        helper = TokenHelper(
            url or os.getenv('OLX_LMS_URL'),
            client_id or os.getenv('OLX_LMS_CLIENT_ID'),
            client_secret or os.getenv('OLX_LMS_CLIENT_SECRET')
        )
        return helper.fetch_token()

    def upload(self,
               url=None,
               file='archive.tar.gz',
               token=None,
               course_id=None,
               wait=False):

        helper = UploadHelper(
            url or os.getenv('OLX_CMS_URL'),
            archive=file,
            token=token or os.getenv('OLX_CMS_TOKEN'),
            course_id=course_id
        )
        return helper.upload(wait)

    def status(self,
               task_id,
               url=None,
               file='archive.tar.gz',
               token=None,
               course_id=None):

        helper = UploadHelper(
            url or os.getenv('OLX_CMS_URL'),
            archive=file,
            token=token or os.getenv('OLX_CMS_TOKEN'),
            course_id=course_id
        )
        return helper.fetch_upload_task_state(task_id)

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

        self.apply_verbosity(opts.pop('verbosity') or 0)

        # Invoke the subcommand, passing the parsed command line
        # options in as kwargs
        ret = getattr(self,
                      opts.pop('subcommand').replace('-', '_'))(**opts)

        # Subcommands may issue a return code or text output, which
        # might be meant to be parsed or piped to other programs. This
        # output is not emitted via a logging call (where it goes to
        # stderr), but via the print function and thus to stdout.
        if ret:
            print(ret)


def main(argv=sys.argv):
    try:
        CLI().main(argv)
    except Exception as e:
        sys.stderr.write('%s\n' % str(e))
        logging.debug('', exc_info=True)
        try:
            sys.exit(e.errno)
        except AttributeError:
            sys.exit(1)


if __name__ == "__main__":
    main()
