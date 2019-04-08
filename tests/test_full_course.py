from __future__ import unicode_literals

import os
import tempfile

import shutil
import shlex
import tarfile

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

    ARCHIVE_MEMBERS = [
        'course',
        'course/about',
        'course/about/overview.html',
        'course/chapter',
        'course/chapter/conclusion.xml',
        'course/chapter/introduction.xml',
        'course/course.xml',
        'course/html',
        'course/html/README.md',
        'course/html/introduction_unit_01.html',
        'course/html/introduction_unit_02.html',
        'course/html/introduction_unit_03.html',
        'course/info',
        'course/info/handouts.html',
        'course/info/updates.html',
        'course/markdown',
        'course/markdown/README.md',
        'course/markdown/introduction_unit_01.md',
        'course/markdown/introduction_unit_02.md',
        'course/markdown/introduction_unit_03.md',
        'course/policies',
        'course/policies/_base',
        'course/policies/_base/grading_policy.json',
        'course/policies/_base/policy.json',
        'course/policies/assets.json',
        'course/policies/foo',
        'course/sequential',
        'course/sequential/README.md',
        'course/sequential/introduction.xml',
        'course/static',
        'course/static/hot',
        'course/static/hot/README.md',
        'course/static/images',
        'course/static/images/README.md',
        'course/static/markdown',
        'course/static/markdown/README.md',
        'course/static/markdown/introduction_unit_01.md',
        'course/static/markdown/introduction_unit_02.md',
        'course/static/markdown/introduction_unit_03.md',
        'course/static/presentation',
        'course/static/presentation/css',
        'course/static/presentation/css/reveal-override.css',
        'course/static/presentation/css/reveal-override.css.map',
        'course/static/presentation/css/reveal-override.scss',
        'course/static/presentation/css/reveal.css',
        'course/static/presentation/css/white.css',
        'course/static/presentation/css/zenburn.css',
        'course/static/presentation/index.html',
        'course/static/presentation/js',
        'course/static/presentation/js/classList.js',
        'course/static/presentation/js/head.min.js',
        'course/static/presentation/js/highlight.js',
        'course/static/presentation/js/markdown.js',
        'course/static/presentation/js/marked.js',
        'course/static/presentation/js/notes.html',
        'course/static/presentation/js/notes.js',
        'course/static/presentation/js/reveal.js',
        'course/static/presentation/js/zoom.js',
    ]

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

    def verify_archive(self):
        filename = os.path.join(self.sourcedir,
                                'archive.tar.gz')
        with tarfile.open(filename) as tf:
            self.assertEqual(set(tf.getnames()),
                             set(self.ARCHIVE_MEMBERS))

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

    def create_archive(self):
        os.chdir(self.sourcedir)
        cmdline = "olx archive"
        args = shlex.split(cmdline)
        CLI().main(args)

    def test_render_course_matching(self):
        self.render_course("foo",
                           "2019-01-01",
                           "2019-12-31")
        self.diff()
        self.create_archive()
        self.verify_archive()

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

    def test_render_course_matching_git_dirty(self):
        dirtypath = os.path.join(self.sourcedir,
                                 'dirty.txt')
        # Pythonic "touch"
        open(dirtypath, 'a').close()

        with self.assertRaises(CLIException):
            self.render_course("foo",
                               "2019-01-01",
                               "2019-12-31",
                               True)


class InvokeFullCourseTestCase(FullCourseTestCase):

    def test_render_course_matching(self):
        os.chdir(self.sourcedir)
        ctx = MockContext()
        tasks.new_run(ctx)
        self.diff()
        tasks.archive(ctx)
        self.verify_archive()

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
