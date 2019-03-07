|PyPI version| |Build Status| |codecov|

OLX Utilities
=============

A set of tools to facilitate courseware development using the `Open
Learning
XML <http://edx.readthedocs.io/projects/edx-open-learning-xml/en/latest/>`__
(OLX) format.

OLX is sometimes tediously repetitive, and this package enables
courseware authors to apply the
`DRY <https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`__
principle when writing OLX content. It allows you to create templates
(using `Mako <http://www.makotemplates.org/>`__), which in turn enable
you to

-  define OLX fragments only once, to reuse them as often as you want
   (this comes in very handy in using the `hastexo
   XBlock <https://github.com/hastexo/hastexo-xblock>`__),
-  write courseware content in
   `Markdown <https://en.wikipedia.org/wiki/Markdown>`__,
-  do anything else you would like to do using your own plugins.

Install
-------

Install the ``olx-utils`` package from PyPI:

.. code:: bash

    pip install olx-utils

Apply templates to a course
---------------------------

In order to create a new course run named ``newrun``, starting on May 1,
2017 and ending on October 31, 2017, simply change into your courseware
checkout and run:

.. code:: bash

    olx new-run -b newrun 2019-01-01 2019-12-31

The ``-b`` option causes your rendered OLX to be added to a new Git
branch named ``run/newrun``, which you can then import into your Open
edX content store.

    You can also invoke ``olx new-run`` as ``new_run.py``. However, this
    is deprecated and its use is discouraged. ``new_run.py`` will go
    away in a future release.

License
-------

This package is licensed under the `GNU Affero
GPL <https://tldrlegal.com/l/agpl3>`__; see
`LICENSE <https://www.gnu.org/licenses/agpl-3.0.txt>`__
for details.

.. |PyPI version| image:: https://img.shields.io/pypi/v/olx-utils.svg
   :target: https://pypi.python.org/pypi/olx-utils
.. |Build Status| image:: https://travis-ci.org/hastexo/olx-utils.svg?branch=master
   :target: https://travis-ci.org/hastexo/olx-utils
.. |codecov| image:: https://codecov.io/gh/hastexo/olx-utils/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/hastexo/olx-utils
