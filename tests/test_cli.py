from __future__ import unicode_literals

import shlex
import sys

from datetime import datetime

from olxutils import cli
from olxutils.cli import CLI, CLIException

# This is extraordinarily ugly, but it's evidently the only option to
# replace sys.stderr with a StringIO instance in a way that it works
# in Python 2 (where sys.stderr is bytes-only) and Python 3 (where
# sys.stderr is unicode-only).
try:
    # Python 2
    from cStringIO import StringIO
except ImportError:
    # Python 3
    from io import StringIO

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from subprocess import Popen, PIPE

from unittest import TestCase


class OLXUtilsCLITestCase(TestCase):
    """
    Run the CLI by importing the cli module and invoking its main()
    method
    """

    CLI_PATH = cli.__file__
    SUBCOMMAND = 'new-run'

    def create_command(self,
                       argstring):
        command = [self.CLI_PATH, argstring]
        if self.SUBCOMMAND:
            command.insert(1, self.SUBCOMMAND)
        return ' '.join(command)

    @patch('sys.stderr', new_callable=StringIO)
    def execute_and_check_error(self,
                                cmdline,
                                expected_output,
                                mock_stderr):
        args = shlex.split(cmdline)

        with patch.multiple(sys,
                            argv=args):
            with self.assertRaises(SystemExit) as se:
                cli.main(sys.argv)
            self.assertNotEqual(se.exception.code, 0)
            self.assertIn(expected_output,
                          mock_stderr.getvalue())

    def test_invalid_name(self):
        cmdline = self.create_command('_base 2019-01-01 2019-01-31')
        expected_output = "This run name is reserved."
        self.execute_and_check_error(cmdline,
                                     expected_output)

    def test_end_before_start_date(self):
        cmdline = self.create_command('foo 2019-02-01 2019-01-31')
        expected_output = "must be greater than or equal"
        self.execute_and_check_error(cmdline,
                                     expected_output)

    def test_invalid_date(self):
        cmdline = self.create_command('foo 2019-02-01 2019-02-31')
        expected_output = "Not a valid date:"
        self.execute_and_check_error(cmdline,
                                     expected_output)


class NewRunTestCase(TestCase):
    """
    Run the CLI's new_run method directly
    """

    def execute_and_check_error(self,
                                expected_output,
                                *args):
        with self.assertRaises(CLIException) as e:
            CLI().new_run(*args)
        self.assertIn(expected_output, str(e.exception))

    def test_invalid_name(self):
        args = ('_base',
                datetime.strptime('2019-01-01', "%Y-%m-%d"),
                datetime.strptime('2019-01-31', "%Y-%m-%d"))

        expected_output = "This run name is reserved."
        self.execute_and_check_error(expected_output,
                                     *args)

    def test_end_before_start_date(self):
        args = ('foo',
                datetime.strptime('2019-02-01', "%Y-%m-%d"),
                datetime.strptime('2019-01-31', "%Y-%m-%d"))
        expected_output = "must be greater than or equal"
        self.execute_and_check_error(expected_output,
                                     *args)


class OLXUtilsCustomArgsTestCase(OLXUtilsCLITestCase):
    """
    Run the CLI by importing the cli module and invoking its main()
    method, overriding its "args" argument
    """

    @patch('sys.stderr', new_callable=StringIO)
    def execute_and_check_error(self,
                                cmdline,
                                expected_output,
                                mock_stderr):
        args = shlex.split(cmdline)

        with self.assertRaises(SystemExit) as se:
            cli.main(args)
        self.assertNotEqual(se.exception.code, 0)
        self.assertIn(expected_output,
                      mock_stderr.getvalue())


class NewRunPyCustomArgsTestCase(OLXUtilsCustomArgsTestCase):
    """
    Run the CLI by importing the cli module and invoking its main()
    method, overriding its "args" argument and setting argv[0]
    to "new_run.py"
    """
    CLI_PATH = 'new_run.py'
    SUBCOMMAND = None


class OLXNewRunCustomArgsTestCase(OLXUtilsCustomArgsTestCase):
    """
    Run the CLI by importing the cli module and invoking its main()
    method, overriding its "args" argument and setting argv[0]
    to "olx-new-run"
    """
    CLI_PATH = 'olx-new-run'
    SUBCOMMAND = None


class MainModuleSubcommandTestCase(OLXUtilsCustomArgsTestCase):
    """
    Test the __main__.py module, that is, invoking Python with the -m
    package option (with a subcommand)
    """
    CLI_PATH = '__main__'
    SUBCOMMAND = 'new-run'


class OLXUtilsShellTestCase(OLXUtilsCLITestCase):
    """
    Runs the CLI by invoking "olx-new-run" in a subprocess, which
    should be picked up in $PATH.
    """

    # Unqualified name path of the console_script installed by
    # the setup.py entry_points list. This should be dropped in
    # the system PATH, so when we subsequently invoke
    # subprocess.Popen, this should get correctly picked up.
    CLI_PATH = 'olx-new-run'
    SUBCOMMAND = None

    # The tests in this class don't use check_call as its use in
    # combination with subprocess.PIPE is strongly discouraged.
    #
    # Reference:
    # https://docs.python.org/3/library/subprocess.html#subprocess.check_call
    def execute_and_check_error(self,
                                cmdline,
                                expected_output):
        args = shlex.split(cmdline)
        p = Popen(args,
                  stderr=PIPE)
        ret = p.wait()
        self.assertNotEqual(ret, 0)
        stdout, stderr = p.communicate()
        self.assertIn(expected_output.encode(),
                      stderr)


class OLXUtilsShellSubcommandTestCase(OLXUtilsShellTestCase):
    """
    Runs the CLI by invoking "olx new-run" in a subprocess, which
    should be picked up in $PATH.
    """
    CLI_PATH = 'olx'
    SUBCOMMAND = 'new-run'


class NewRunPyTestCase(OLXUtilsShellTestCase):
    """
    # Run the CLI tests with the deprecated compatibility alias
    """
    CLI_PATH = 'new_run.py'
    SUBCOMMAND = None
