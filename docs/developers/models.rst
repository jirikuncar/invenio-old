.. _developers-models:

Models
======

Models define a Python-ic interface to relational databases using
`SQLAlchemy`_ toolkit that *provides a full suite of well
known enterprise-level persistence patterns, designed for efficient and
high-performing database access, adapted into a simple and Pythonic domain
language* [SQLAlchemy2013]_.

In order to add support of SQLAlchemy to our application, the
`Flask-SQLAlchemy`_ extension is used.  It provides useful defaults as
well as extra declarative base helpers.  We recommend reading
`Official Tutorial` for a full introduction and `Other Tutorial` for
better understanding of ORM concepts.


Code structure
--------------

Our custom bridge is contains several custom types and driver hacks for
smoother integration with multiple database engines. The code structure
follows::

    invenio/ext/sqlalchemy
        /engines
            mysql.py
        __init__.py
        expressions.py
        types.py
        utils.py




See :data:`~invenio.ext.sqlalchemy.db` object .



.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _Flask-SQLAlchemy: http://pythonhosted.org/Flask-SQLAlchemy/
.. _Official Tutorial: http://docs.sqlalchemy.org/en/latest/orm/tutorial.html
.. _Other Tutorial: http://www.rmunn.com/sqlalchemy-tutorial/tutorial.html

.. [SQLAlchemy2013] SQLAlchemy website: http://www.sqlalchemy.org/
