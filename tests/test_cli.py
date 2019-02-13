from __future__ import unicode_literals

import shlex

import sys

from subprocess import Popen, PIPE

from unittest import TestCase


class OLXUtilsCLITestCase(TestCase):

    # Unqualified name path of the console_script installed by
    # the setup.py entry_points list. This should be dropped in
    # the system PATH, so when we subsequently invoke
    # subprocess.Popen, this should get correctly picked up.
    CLI_PATH = 'olx-new-run'

    # The tests in this class don't use check_call as its use in
    # combination with subprocess.PIPE is strongly discouraged.
    #
    # Reference:
    # https://docs.python.org/3/library/subprocess.html#subprocess.check_call
    def test_invalid_name(self):
        cmdline = '%s _base 2019-01-01 2019-01-31' % self.CLI_PATH
        args = shlex.split(cmdline)
        p = Popen(args,
                  stderr=PIPE)
        ret = p.wait()
        self.assertNotEqual(ret, 0)
        stdout, stderr = p.communicate()
        self.assertIn("This run name is reserved.".encode(),
                      stderr)

    def test_end_before_start_date(self):
        cmdline = '%s foo 2019-02-01 2019-01-31' % self.CLI_PATH
        args = shlex.split(cmdline)
        p = Popen(args,
                  stderr=PIPE)
        ret = p.wait()
        self.assertNotEqual(ret, 0)
        stdout, stderr = p.communicate()
        self.assertIn("must be greater than or equal".encode(),
                      stderr)

    def test_invalid_date(self):
        cmdline = '%s foo 2019-02-01 2019-02-31' % self.CLI_PATH
        args = shlex.split(cmdline)
        p = Popen(args,
                  stderr=PIPE)
        ret = p.wait()
        self.assertNotEqual(ret, 0)
        stdout, stderr = p.communicate()
        self.assertIn("Not a valid date:".encode(),
                      stderr)


class MainModuleTestCase(OLXUtilsCLITestCase):
    """
    Test the __main__.py module, that is, invoking Python with the -m
    package option
    """
    CLI_PATH = '%s -m olxutils' % sys.executable


class NewRunPyTestCase(OLXUtilsCLITestCase):
    """
    # Run the CLI tests with the deprecated compatibility alias
    """
    
    CLI_PATH = 'new_run.py'
