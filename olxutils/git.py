from __future__ import unicode_literals

from subprocess import check_call, CalledProcessError


class GitHelperException(Exception):
    pass


class GitHelper(object):

    BRANCH_FORMAT = "run/%s"

    def __init__(self, run):
        self.run = run
        self.branch = self.BRANCH_FORMAT % run
        self.message = ""

    def _git_command(self, args):
        check_call("git %s" % args, shell=True)

    def create_branch(self):
        if self.branch_exists():
            message = (
                "The target git branch already exists.  "
                "Please delete it and try again.\n"
                "You can do so with: \n"
                "\n"
                "git branch -d {}\n"
            )
            raise GitHelperException(message.format(self.branch))

        try:
            self._git_command("checkout -b {}".format(self.branch))
        except CalledProcessError:
            raise GitHelperException('Error creating '
                                     'branch {}'.format(self.branch))

    def branch_exists(self):
        try:
            self._git_command("rev-parse --verify {}".format(self.branch))
        except CalledProcessError:
            return False

        return True

    def add_to_branch(self):
        # Git add the changed files and commit them.
        try:
            self._git_command("add .")
            self._git_command("commit -m 'New run: {}'".format(self.run))
        except CalledProcessError:
            raise GitHelperException('Error committing new run.')
        self.message = (
            "\n"
            "To push this new branch upstream, run:\n"
            "\n"
            "$ git push -u origin {}\n"
            "\n"
            "To switch back to master, run:\n"
            "\n"
            "$ git checkout master\n"
        ).format(self.branch)
