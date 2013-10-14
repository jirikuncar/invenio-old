# -*- coding: utf-8 -*-
##
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
    invenio.ext.login
    -----------------

    This module provides initialization and configuration for `flask.ext.login`
    module.
"""

from .legacy_user import UserInfo
from flask import request, flash, g
from flask.ext.login import LoginManager, current_user, \
    login_user as flask_login_user, logout_user, login_required, UserMixin


def login_user(user, *args, **kwargs):
    """Allows login user by its id."""
    if type(user) in [int, long]:
        user = UserInfo(user)
    return flask_login_user(user, *args, **kwargs)


def setup_app(app):
    """Setup login extension."""

    @app.errorhandler(401)
    def do_login_first(error=401):
        """Displays login page when user is not authorised."""
        if request.is_xhr:
            return g._("Authorization failure"), 401
        flash(g._("Authorization failure"), 'error')
        from invenio.modules.account.blueprint import login
        return login(referer=request.url), 401

    # Let's create login manager.
    _login_manager = LoginManager(app)
    _login_manager.login_view = app.config.get('CFG_LOGIN_VIEW',
                                               'webaccount.login')
    _login_manager.anonymous_user = UserInfo
    _login_manager.unauthorized_handler(do_login_first)

    @_login_manager.user_loader
    def _load_user(uid):
        """
        Function should not raise an exception if uid is not valid
        or User was not found in database.
        """
        return UserInfo(int(uid))

    return app
