from __future__ import unicode_literals

from datetime import datetime

from invoke import task

from olxutils.cli import CLI


@task
def new_run(context,
            name='foo',
            start_date='2019-01-01',
            end_date='2019-12-31',
            create_branch=False):

    def to_date(s):
        return datetime.strptime(s, "%Y-%m-%d")

    CLI().new_run(name,
                  to_date(start_date),
                  to_date(end_date),
                  create_branch)


@task
def archive(context):

    CLI().archive()
