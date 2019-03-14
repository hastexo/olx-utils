from __future__ import unicode_literals

import os
import tempfile

import shutil
import shlex

from subprocess import check_call, CalledProcessError

from olxutils.cli import CLI, CLIException

import git

from invoke import MockContext
import tasks

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from unittest import TestCase


class FullCourseTestCase(TestCase):
    """
    Render a full course and compare its results to expectations
    """

    SOURCE_DIR = os.path.join(os.path.dirname(__file__),
                              'course',
                              'source')
    RESULT_DIR = os.path.join(os.path.dirname(__file__),
                              'course',
                              'result')

    def setUp(self):
        """
        Copy the source and result files to temporary directories
        """
        self.tmpdir = tempfile.mkdtemp()
        self.sourcedir = os.path.join(self.tmpdir,
                                      'source')
        self.resultdir = os.path.join(self.tmpdir,
                                      'result')
        shutil.copytree(self.SOURCE_DIR,
                        self.sourcedir,
                        symlinks=True)
        shutil.copytree(self.RESULT_DIR,
                        self.resultdir,
                        symlinks=True)

    def diff(self):
        # There's no Pythonic way that's any more efficient than
        # calling out to "diff -r" here
        check_call('diff -q -r source result',
                   cwd=self.tmpdir,
                   shell=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


class CLIFullCourseTestCase(FullCourseTestCase):

    def render_course(self,
                      name,
                      start_date_string,
                      end_date_string,
                      create_branch=False):
        os.chdir(self.sourcedir)
        cmdline = ("olx new-run "
                   "%s %s %s %s") % ('-b' if create_branch else '',
                                     name,
                                     start_date_string,
                                     end_date_string)

        args = shlex.split(cmdline)
        CLI().main(args)

    def test_render_course_matching(self):
        self.render_course("foo",
                           "2019-01-01",
                           "2019-12-31")
        self.diff()

    def test_render_course_nonmatching(self):
        self.render_course("bar",
                           "2019-01-01",
                           "2019-12-31")
        with self.assertRaises(CalledProcessError):
            self.diff()

    def test_render_course_error(self):
        """Force an exception in rendering by removing a required file."""
        os.remove(os.path.join(self.sourcedir,
                               'include',
                               'course.xml'))
        with self.assertRaises(CLIException):
            self.render_course("foo",
                               "2019-01-01",
                               "2019-12-31")

    def test_render_course_force_git_error(self):
        # Simulate an empty PATH, so a git command fails
        with patch.dict(os.environ,
                        {'PATH': ''}):
            with self.assertRaises(CLIException):
                self.render_course("foo",
                                   "2019-01-01",
                                   "2019-12-31",
                                   True)


class CLIGitFullCourseTestCase(CLIFullCourseTestCase):

    def setUp(self):
        super(CLIGitFullCourseTestCase, self).setUp()

        os.chdir(self.sourcedir)
        repo = git.Repo.init()
        with repo.config_writer() as cw:
            cw.set_value("user", "name", "John D. Oe")
            cw.set_value("user", "email", "johndoe@example.com")
            cw.release()
        repo.git.add('.')
        repo.git.commit('-m', 'Initial commit')

        self.repo = repo

    def diff(self):
        check_call('diff -q -r -x .git source result',
                   cwd=self.tmpdir,
                   shell=True)

    def test_render_course_matching_git(self):
        self.render_course("foo",
                           "2019-01-01",
                           "2019-12-31",
                           True)
        self.diff()
        self.assertIn('run/foo', self.repo.branches)


class InvokeFullCourseTestCase(FullCourseTestCase):

    def test_render_course_matching(self):
        os.chdir(self.sourcedir)
        ctx = MockContext()
        tasks.new_run(ctx)
        self.diff()

    def test_render_course_nonmatching(self):
        os.chdir(self.sourcedir)
        ctx = MockContext()
        tasks.new_run(ctx, "bar")
        with self.assertRaises(CalledProcessError):
            self.diff()

    def test_render_course_error(self):
        """Force an exception in rendering by removing a required file."""
        os.remove(os.path.join(self.sourcedir,
                               'include',
                               'course.xml'))
        os.chdir(self.sourcedir)
        ctx = MockContext()
        with self.assertRaises(CLIException):
            tasks.new_run(ctx)
