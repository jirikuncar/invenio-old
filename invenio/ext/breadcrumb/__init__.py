# -*- coding: utf-8 -*-
##
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
    invenio.ext.breadcrumb
"""

from invenio.base.globals import current_function, current_blueprint
from invenio.ext.menu import MenuAlchemy, current_menu


def setup_app(app):
    app.context_processor(breadcrumbs_context_processor)
    return app


def breadcrumbs_context_processor():
    """
        Adds variable 'breadcrumbs' to template context.
        It contains the list of menu entries to render as breadcrumbs.
    """
    # Determine current location in menu hierarchy
    current_path = getattr(current_function, '__breadcrumb__', None) \
        or getattr(current_blueprint, '__breadcrumb__', None)

    if path:
        # List entries on route from 'breadcrumbs' to current path
        breadcrumbs = current_menu.list_path('breadcrumbs', current_path) or []
    else:
        breadcrumbs = []

    return dict(breadcrumbs=breadcrumbs)


def default_breadcrumb(blueprint, text, path=None):
    """
        Registers the default breadcrumb for all endpoints in this blueprint.

        :param text: Text to display in the breadcrumb.
        :param path: Path in the menu hierarchy. If not specified,
            defaults to 'breadcrumbs.blueprint_name'.
    """

    if not path:
        path = 'breadcrumbs.' + blueprint.name

    # Create the menu item
    MenuAlchemy.root.submenu(path).register(blueprint.name, text)

    # Assign path to blueprint
    blueprint.__breadcrumb__ = path


def register_breadcrumb(
        blueprint,
        path,
        text,
        endpoint_arguments_constructor=None):
    """Decorate endpoints that should be displayed as a breadcrumb.

    :param blueprint: Blueprint which owns the function.
    :param path: Path to this item in menu hierarchy
        ("breadcrumbs." is automatically added).
    :param text: Text displayed as link.
    :param order: Index of item among other items in the same menu.
    :param endpoint_arguments_constructor: Function returning dict of
        arguments passed to url_for when creating the link.
    :param active_when: Function returning True when the item
        should be displayed as active.
    :param visible_when: Function returning True when this item
        should be displayed.
    """

    # Resolve relative paths
    if path.startswith('.'):
        # Breadcrumb relative to blueprint
        blueprint_path = getattr(
            blueprint,
            '__breadcrumb__',
            'breadcrumbs.' + blueprint.name)

        # There may be a trailing dot
        path = (blueprint_path + path).strip('.')

    # Get standard menu decorator
    menu_decorator = MenuAlchemy.register_menu(
        blueprint,
        path,
        text,
        0,
        endpoint_arguments_constructor)

    # Apply standard menu decorator and assign breadcrumb
    def breadcrumb_decorator(f):
        f.__breadcrumb__ = path

        return menu_decorator(f)

    return breadcrumb_decorator
