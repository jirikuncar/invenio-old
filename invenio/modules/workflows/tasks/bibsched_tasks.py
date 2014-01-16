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
## 59 Temple Place, Suite 330, Boston, MA 021111307, USA.

from invenio.legacy.bibsched.bibtask import write_message


def write_something_bibsched(messagea="This is the default message"):
    """
    This function allows to send a message to bibsched...
    This messages will be store into log.
    """

    def _write_something_bibsched(obj, eng):

        if isinstance(messagea, basestring):
            write_message(messagea)
            return None

        if not isinstance(messagea, list):
            if callable(messagea):
                I = messagea
                while callable(I):
                    I = I(obj, eng)
                write_message(I)
            return None

        if len(messagea) > 0:
            temp = ""
            for I in messagea:
                if callable(I):
                    while callable(I):
                        I = I(obj, eng)
                    temp += str(I)
                elif isinstance(I, basestring):
                    temp += I
            write_message(temp)
            return None

    return _write_something_bibsched


def write_something_generic(messagea, func):
    """
    This function allows to send a message to bibsched...
    This messages will be store into log.
    """

    def _write_something_generic(obj, eng):

        if isinstance(messagea, basestring):
            if isinstance(func,list):
                for function in func:
                    function(messagea)
            else:
                func(messagea)
            return None

        if not isinstance(messagea, list):
            if callable(messagea):
                I = messagea
                while callable(I):
                    I = I(obj, eng)
                if isinstance(func,list):
                    for function in func:
                        function(I)
                else:
                    func(I)
            return None

        if len(messagea) > 0:
            temp = ""
            for I in messagea:
                if callable(I):
                    while callable(I):
                        I = I(obj, eng)
                    temp += str(I)
                elif isinstance(I, basestring):
                    temp += I
            if isinstance(func,list):
                for function in func:
                    function(temp)
            else:
                func(temp)
            return None

    return _write_something_generic


def task_update_progress(msg):
    def _task_update_progress(obj, eng):
        """Updates progress information in the BibSched task table."""
        from invenio.legacy.bibsched.bibtask import task_update_progress as task_update_progress_nested

        task_update_progress_nested(msg)

    return _task_update_progress


def task_update_status(val):
    def _task_update_status(obj, eng):
        """Updates status information in the BibSched task table."""
        from invenio.legacy.bibsched.bibtask import task_update_status as task_update_status_nested

        task_update_status_nested(val)

    return _task_update_status


