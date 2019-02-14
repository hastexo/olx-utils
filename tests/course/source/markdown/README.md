`markdown`
==========

Add Markdown files here.


Headings
--------

Note that Markdown files should use the following format for headings:

```markdown
Heading 1
=========

Heading 2
---------
```

*Do not* use the following format:

```markdown
# Heading 1

## Heading 2
```

This is due to the quirk that [Mako](http://www.makotemplates.org/)
always treats `##` as a
[comment](http://docs.makotemplates.org/en/latest/syntax.html#comments),
so headings marked up with `##` will simply be suppressed from the
output.


Images
------

Markdown files should start with the following Mako definition:

```
<%namespace file="/olx_partials.xml" import="asset_url"/>
```

Images can then be referenced as follows:

```markdown
![Alt text](/${asset_url("images_<image-filename>")})
```
