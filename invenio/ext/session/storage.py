# -*- coding: utf-8 -*-

## This file is part of Invenio.
## Copyright (C) 2011, 2012, 2013 CERN.
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
    invenio.ext.session.storage
    ---------------------------

    Session storage interface.
"""


class SessionStorage(object):
    """
    Session storage slub.
    """

    def set(self, name, value, timeout=None):
        """
        Stores data in a key-value storage system for defined time.
        """
        raise NotImplementedError()

    def get(self, name):
        """
        Returns data from the key-value storage system.
        """
        raise NotImplementedError()

    def delete(self, name):
        """
        Deletes data from the key-value storage system.
        """
        raise NotImplementedError()
