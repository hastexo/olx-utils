from __future__ import unicode_literals

import os

import shlex

from subprocess import Popen, PIPE

from unittest import TestCase


class OLXUtilsCLITestCase(TestCase):

    CLI_PATH = os.path.join(os.path.dirname(__file__),
                            '../bin/olx-new-run')

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
