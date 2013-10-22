## This file is part of Invenio.
## Copyright (C) 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
Invenio
-----

Invenio is a digital library framework. And before you ask:
It's GNU/GPLv2 licensed!

Invenio is Fun
``````````````

.. code:: python

    from invenio.base import create_app
    app = create_app()

    if __name__ == "__main__":
        app.run()

And Easy to Setup
`````````````````

.. code:: bash

    $ pip install invenio
    $ python hello.py
     * Running on http://localhost:5000/

Links
`````

* `website <http://invenio-software.org/>`_
* `documentation <TODO>`_
* `development version <http://invenio-software.org/repo/invenio>`_

"""
from __future__ import print_function
from setuptools import Command, setup

def requirements():
    req = []
    dep = []
    for filename in ['requirements.txt', 'requirements-extras.txt',
                     'requirements-flask.txt', 'requirements-flask-ext.txt']:
        with open(filename, 'r') as f:
            for line in f.readlines():
                if '://' in line:
                    dep.append(line)
                else:
                    req.append(str(line))
    return req, dep

install_requires, dependency_links = requirements()

setup(
    name='Invenio',
    version='1.9999-dev',
    url='http://invenio-sofrware.org/repo/invenio',
    license='GPLv2',
    author='CERN',
    author_email='info@invenio-software.org',
    description='Digital library software',
    long_description=__doc__,
    packages=[
        'invenio.base',
        'invenio.ext',
        'invenio.legacy',
        'invenio.modules',
        'invenio.utils',
    ],
    namespace_packages=['invenio'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    entry_points={
        'console_scripts': [
            'inveniomanage = invenio.base.manage:main',
            'textmarc2xmlmarc = invenio.utils.textmarc2xmlmarc:main'
        ],
    },
    install_requires=install_requires,
    dependency_links=dependency_links,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPLv2 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    #test_suite='invenio.testsuite.suite'
)
