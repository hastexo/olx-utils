from __future__ import unicode_literals

import os
import tempfile

import shutil
import shlex

from subprocess import check_call, CalledProcessError

from olxutils import cli

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

    def render_course(self, cmdline):
        os.chdir(self.sourcedir)
        args = shlex.split(cmdline)
        cli.main(args)

    def test_render_course_matching(self):
        self.render_course("olx-new-run foo 2019-01-01 2019-12-31")

        # There's no Pythonic way that's any more efficient than
        # calling out to "diff -r" here
        print(self.tmpdir)
        check_call('diff -q -r source result',
                   cwd=self.tmpdir,
                   shell=True)

    def test_render_course_nonmatching(self):
        self.render_course("olx-new-run bar 2019-01-01 2019-12-31")

        print(self.tmpdir)
        with self.assertRaises(CalledProcessError):
            check_call('diff -q -r source result',
                       cwd=self.tmpdir,
                       shell=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
