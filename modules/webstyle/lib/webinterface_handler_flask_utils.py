# -*- coding: utf-8 -*-
## This file is part of Invenio.
## Copyright (C) 2012, 2013 CERN.
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
Invenio -> Flask adapter utilities
"""

import types
from functools import wraps
from flask import Blueprint, current_app, request,  \
                  render_template, jsonify, get_flashed_messages, flash, \
                  Response, _request_ctx_stack, stream_with_context, Request

## Placemark for the i18n function
_ = lambda x: x


class InvenioBlueprint(Blueprint):

    def __init__(self, name, import_name, url_prefix=None, config=None,
                 breadcrumbs=None, menubuilder=None, force_https=False,
                 **kwargs):
        """
        Invenio extension of standard Flask blueprint.

        @param name: blueprint unique text identifier
        @param import_name: class name (usually __name__)
        @param url_prefix: URL prefix for all blueprints' view functions
        @param config: importable config class
        @param breadcrumbs: list of breadcrumbs
        @param menubuilder: list of menus
        @param force_https: requires blueprint to be accessible only via https
        """
        Blueprint.__init__(self, name, import_name, url_prefix=url_prefix, **kwargs)
        self.config = config
        self._force_https = force_https

    def invenio_wash_urlargd(self, config):
        def _invenio_wash_urlargd(f):
            @wraps(f)
            def decorator(*args, **kwargs):
                argd = wash_urlargd(request.values, config)
                argd.update(kwargs)
                return f(*args, **argd)
            return decorator
        return _invenio_wash_urlargd


def wash_urlargd(form, content):
    """
    Wash the complete form based on the specification in
    content. Content is a dictionary containing the field names as a
    key, and a tuple (type, default) as value.

    'type' can be list, unicode, invenio.webinterface_handler_wsgi_utils.StringField, int, tuple, or
    invenio.webinterface_handler_wsgi_utils.Field (for
    file uploads).

    The specification automatically includes the 'ln' field, which is
    common to all queries.

    Arguments that are not defined in 'content' are discarded.

    Note that in case {list,tuple} were asked for, we assume that
    {list,tuple} of strings is to be returned.  Therefore beware when
    you want to use wash_urlargd() for multiple file upload forms.

    @Return: argd dictionary that can be used for passing function
    parameters by keywords.
    """

    result = {}

    for k, (dst_type, default) in content.items():
        try:
            value = form[k]
        except KeyError:
            result[k] = default
            continue

        src_type = type(value)

        # First, handle the case where we want all the results. In
        # this case, we need to ensure all the elements are strings,
        # and not Field instances.
        if src_type in (list, tuple):
            if dst_type is list:
                result[k] = [x for x in value]
                continue

            if dst_type is tuple:
                result[k] = tuple([x for x in value])
                continue

            # in all the other cases, we are only interested in the
            # first value.
            value = value[0]

        # Allow passing argument modyfing function.
        if isinstance(dst_type, types.FunctionType):
            result[k] = dst_type(value)
            continue

        # Maybe we already have what is expected? Then don't change
        # anything.
        if isinstance(value, dst_type):
            result[k] = value
            continue

        # Since we got here, 'value' is sure to be a single symbol,
        # not a list kind of structure anymore.
        if dst_type in (int, float, long):
            try:
                result[k] = dst_type(value)
            except:
                result[k] = default

        elif dst_type is tuple:
            result[k] = (value, )

        elif dst_type is list:
            result[k] = [value]

        else:
            raise ValueError('cannot cast form value %s of type %r into type %r' % (value, src_type, dst_type))

    return result
