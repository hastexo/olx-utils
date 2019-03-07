from __future__ import unicode_literals

from olxutils.git import GitHelper, GitHelperException

import shutil

import os

import tempfile

import git

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from unittest import TestCase


class GitHelperTestCase(TestCase):

    RUN_NAME = 'foo'
    DIR = os.path.dirname(__file__)

    def setUp(self):
        self.helper = GitHelper(self.RUN_NAME)

        self.tmpdir = tempfile.mkdtemp()

        os.chdir(self.tmpdir)
        repo = git.Repo.init()
        with repo.config_writer() as cw:
            cw.set_value("user", "name", "John D. Oe")
            cw.set_value("user", "email", "johndoe@example.com")
            cw.release()

        self.repo = repo

    def create_file(self, content):
        (fd, self.tmpfile) = tempfile.mkstemp(dir=self.tmpdir,
                                              text=True)
        with os.fdopen(fd, 'w') as file:
            file.write(content)

    def add_and_commit(self, message):
        self.repo.git.add(os.path.basename(self.tmpfile))
        self.repo.git.commit('-m', message)

    def test_init(self):
        """
        Check the state of a GitHelper object immediately after
        initialization
        """
        self.assertEqual(self.helper.run, self.RUN_NAME)
        self.assertEqual(self.helper.branch,
                         'run/%s' % self.RUN_NAME)
        self.assertFalse(self.helper.message)

    def test_create_branch(self):
        """
        Create a run branch
        """
        self.create_file('Hello world')
        self.add_and_commit('Test 1')

        self.assertFalse(self.helper.branch_exists())
        self.assertIn('master', self.repo.branches)
        self.helper.create_branch()
        self.assertIn('run/%s' % self.RUN_NAME,
                      self.repo.branches)
        self.assertTrue(self.helper.branch_exists())

    def test_create_branch_error(self):
        """
        Attempt to create a run branch, triggering an
        exception.
        """
        self.create_file('Hello world')
        self.add_and_commit('Test 1')

        self.assertFalse(self.helper.branch_exists())
        self.assertIn('master', self.repo.branches)

        # Simulate an empty PATH, so a git command fails
        with patch.dict(os.environ,
                        {'PATH': ''}):
            with self.assertRaises(GitHelperException) as e:
                self.helper.create_branch()
            expected_msg = 'Error creating branch run/%s' % self.RUN_NAME
            self.assertEqual(str(e.exception), expected_msg)

    def test_create_branch_again(self):
        """
        Ensure that creating two branches with the same name fails
        """
        self.create_file('Hello world')
        self.add_and_commit('Test 1')

        self.assertFalse(self.helper.branch_exists())
        self.helper.create_branch()
        self.assertTrue(self.helper.branch_exists())
        with self.assertRaises(GitHelperException):
            self.helper.create_branch()

    def test_add_to_branch(self):
        """
        Test the automatic addition of new files to a run branch
        """
        self.create_file('Hello world')
        self.add_and_commit('Test 1')
        self.helper.create_branch()
        self.create_file('Bye bye')
        # Should add all files create since the last commit
        self.helper.add_to_branch()
        # Should have been set to a nonempty string when
        # the commit was successful
        self.assertTrue(self.helper.message)

        # We should now have one commit on the master branch,
        # and two on the run/foo branch
        master = self.repo.heads.master
        run = self.repo.heads['run/%s' % self.RUN_NAME]
        self.assertEqual(len(master.commit.tree), 1)
        self.assertEqual(len(run.commit.tree), 2)

        # The commit message on the HEAD of the run/foo branch should
        # be "New run: foo"
        self.assertEqual(run.commit.message,
                         "New run: %s\n" % self.RUN_NAME)

    def test_add_to_branch_error(self):
        self.create_file('Hello world')
        self.add_and_commit('Test 1')
        self.helper.create_branch()
        self.create_file('Bye bye')
        # Simulate an empty PATH, so a git command fails
        with patch.dict(os.environ,
                        {'PATH': ''}):
            with self.assertRaises(GitHelperException) as e:
                self.helper.add_to_branch()
            expected_msg = 'Error committing new run.'
            self.assertEqual(str(e.exception), expected_msg)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
