[![PyPI version](https://img.shields.io/pypi/v/olx-utils.svg)](https://pypi.python.org/pypi/olx-utils)

# OLX Utilities

A set of tools to facilitate courseware development using the
[Open Learning XML](http://edx.readthedocs.io/projects/edx-open-learning-xml/en/latest/)
(OLX) format.

OLX is sometimes tediously repetitive, and this package enables
courseware authors to apply the
[DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) principle
when writing OLX content. It allows you to create templates (using
[Mako](http://www.makotemplates.org/)), which in turn enable you to

- define OLX fragments only once, to reuse them as often as you want
  (this comes in very handy in using the
  [hastexo XBlock](https://github.com/hastexo/hastexo-xblock)),
- write courseware content in
  [Markdown](https://en.wikipedia.org/wiki/Markdown),
- do anything else you would like to do using your own plugins.

## Install

Install the `olx-utils` package from PyPI:

```bash
pip install olx-utils
```

## Apply templates to a course

In order to create a new course run named `newrun`, starting on May 1,
2017 and ending on October 31, 2017, simply change into your
courseware checkout and run:

```bash
new_run.py -b newrun 2017-05-01 2017-10-31
```

The `-b` option causes your rendered OLX to be added to a new Git
branch named `run/newrun`, which you can then import into your Open
edX content store.

## License

This package is licensed under the Affero GPL; see [`LICENSE`](LICENSE) for
details.
