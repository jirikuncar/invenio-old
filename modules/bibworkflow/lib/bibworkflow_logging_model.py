# -*- coding: utf-8 -*-
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

import logging
import traceback
from datetime import datetime

from invenio.sqlalchemyutils import db
from sqlalchemy import desc
from sqlalchemy.orm.exc import NoResultFound


def get_logger(logger_name, db_handler_class,
               loglevel=logging.DEBUG, **kwargs):
    """
    Will initialize and return a Python logger object with
    handlers to output logs in sys.stderr as well as the
    datebase.
    """
    logging.basicConfig(level=loglevel)

    # Get a basic logger object
    logger = logging.getLogger(logger_name)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(levelname)s %(asctime)s %(name)s    %(message)s')

    db_handler = db_handler_class()
    db_handler.setFormatter(formatter)
    db_handler.setLevel(loglevel)
    logger.addHandler(db_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(loglevel)
    logger.addHandler(stream_handler)

    # Let's not propagate to root logger..
    logger.propagate = 0

    # FIXME: loglevels are simply overwritten somewhere in Celery
    #        even if Celery is not being "used".
    #
    #        This means loglevel.DEBUG is NOT working at the moment!
    logger.setLevel(loglevel)

    # Add any kwargs to extra parameter and return logger
    wrapped_logger = BibWorkflowLogAdapter(logger, kwargs)
    return wrapped_logger


class BibWorkflowEngineHandler(logging.Handler):
    """
    """
    def emit(self, record):
        log_obj = BibWorkflowEngineLog(id_workflow=record.obj.uuid,
                                       log_type=record.levelno,
                                       message=record.msg,
                                       error_msg=traceback.format_exc())
        db.session.add(log_obj)
        db.session.commit()


class BibWorkflowObjectHandler(logging.Handler):
    """
    """
    def emit(self, record):
        log_obj = BibWorkflowObjectLog(id_bibworkflowobject=record.obj.id,
                                       log_type=record.levelno,
                                       message=record.msg,
                                       error_msg=traceback.format_exc())
        db.session.add(log_obj)
        db.session.commit()


class BibWorkflowLogAdapter(logging.LoggerAdapter):
    """
    This example adapter expects the passed in dict-like object to have a
    'obj' key, whose value in brackets is used during logging.
    """

    def process(self, msg, kwargs):
        kwargs['extra'] = self.extra
        return msg, kwargs


class BibWorkflowObjectLog(db.Model):
    """
    This class represent a record of a log emit by an object
    into the database the object must be saved before using
    this class. Indeed it needs the id of the object into
    the database.
    """
    __tablename__ = 'bwlOBJECTLOGGING'
    id = db.Column(db.Integer, primary_key=True)
    id_bibworkflowobject = db.Column(db.Integer(255),
                                     db.ForeignKey('bwlOBJECT.id'),
                                     nullable=False)
    log_type = db.Column(db.Integer, default=0, nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    message = db.Column(db.TEXT, default="", nullable=False)
    error_msg = db.Column(db.TEXT, default="", nullable=False)

    def __repr__(self):
        return "<BibWorkflowObjectLog(%i, %s, %s, %s)>" % \
               (self.id, self.id_bibworkflowobject, self.message, self.created)

    @classmethod
    def get(cls, *criteria, **filters):
        """ A wrapper for the filter and filter_by functions of sqlalchemy.
        Define a dict with which columns should be filtered by which values.

        look up also sqalchemy BaseQuery's filter and filter_by documentation
        """
        return cls.query.filter(*criteria).filter_by(**filters)

    @classmethod
    def get_most_recent(cls, *criteria, **filters):
        """ Returns the most recently created log. """

        most_recent = cls.get(*criteria, **filters).\
            order_by(desc(BibWorkflowObjectLog.created)).first()
        if most_recent is None:
            raise NoResultFound
        else:
            return most_recent

    @classmethod
    def delete(cls, id=None):
        cls.get(BibWorkflowObjectLog.id == id).delete()
        db.session.commit()


class BibWorkflowEngineLog(db.Model):
    __tablename__ = "bwlWORKFLOWLOGGING"
    id = db.Column(db.Integer, primary_key=True)
    id_workflow = db.Column(db.String(255), nullable=False)
    log_type = db.Column(db.Integer, default=0, nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    message = db.Column(db.TEXT, default="", nullable=False)
    error_msg = db.Column(db.TEXT, default="", nullable=False)

    def __repr__(self):
        return "<BibWorkflowEngineLog(%i, %s, %s, %s)>" % \
               (self.id, self.id_workflow, self.message, self.created)

    @classmethod
    def get(cls, *criteria, **filters):
        """ A wrapper for the filter and filter_by functions of sqlalchemy.
        Define a dict with which columns should be filtered by which values.

        look up also sqalchemy BaseQuery's filter and filter_by documentation
        """
        return cls.query.filter(*criteria).filter_by(**filters)

    @classmethod
    def get_most_recent(cls, *criteria, **filters):
        """ Returns the most recently created log. """

        most_recent = cls.get(*criteria, **filters).\
            order_by(desc(BibWorkflowEngineLog.created)).first()
        if most_recent is None:
            raise NoResultFound
        else:
            return most_recent

    @classmethod
    def delete(cls, uuid=None):
        cls.get(BibWorkflowEngineLog.id == uuid).delete()
        db.session.commit()


__all__ = ['BibWorkflowObjectLog', 'BibWorkflowEngineLog']
