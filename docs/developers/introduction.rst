.. _developers-introduction:

Introducing Invenio for Developers
==================================

This page summarizes adoption of frameworks in used Invenio. It describes
extensions and module anatomy and concept of pluggable components across
modules.

Extensions
----------

Invenio is using many of Flask extensions that extend the functionality of
Flask in various different ways. For instance they add support for
databases, user authentication & authorization, menu & breadcrumbs and
other common tasks.

Many of Flask extensions can be found in the `Flask Extension Registry`_.
All extensions are automatically loaded from ``EXTENSIONS`` configuration
option list. If they should a function ``setup_app(app)`` or function
accepting ``app`` needs to be specified (e.g. ``foo.bar:init``,
``mymodule:setup``).

Continue with :ref:`developers-extensions`.

.. _Flask Extension Registry: http://flask.pocoo.org/extensions/
.. _SQLAlchemy: http://www.sqlalchemy.org/
