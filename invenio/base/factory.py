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
    invenio.base.factory
    --------------------

    Implements application factory.
"""

import os

from invenio import config
from invenio.errorlib import register_exception
from invenio.config import \
    CFG_WEBDIR, \
    CFG_FLASK_DISABLED_BLUEPRINTS, \
    CFG_SITE_SECRET_KEY, CFG_BINDIR


from .helpers import with_app_context, unicodifier
from .utils import collect_blueprints, register_extensions, \
    register_configurations
from .wrappers import Flask


__all__ = ['create_app', 'with_app_context']


def create_app(**kwargs_config):
    """
    Prepare WSGI Invenio application based on Flask.

    Invenio consists of a new Flask application with legacy support for
    the old WSGI legacy application and the old Python legacy
    scripts (URLs to *.py files).

    An incoming request is processed in the following manner:

     * The Flask application first routes request via its URL routing
       system (see LegacyAppMiddleware.__call__()).

     * One route in the Flask system, will match Python legacy
       scripts (see static_handler_with_legacy_publisher()).

     * If the Flask application aborts the request with a 404 error, the request
       is passed on to the WSGI legacy application (see page_not_found()). E.g.
       either the Flask application did not find a route, or a view aborted the
       request with a 404 error.
    """

    ## The Flask application instance
    _app = Flask(__name__, #FIXME .split('.')[0],
        ## Static files are usually handled directly by the webserver (e.g. Apache)
        ## However in case WSGI is required to handle static files too (such
        ## as when running simple server), then this flag can be
        ## turned on (it is done automatically by wsgi_handler_test).
        ## We assume anything under '/' which is static to be server directly
        ## by the webserver from CFG_WEBDIR. In order to generate independent
        ## url for static files use func:`url_for('static', filename='test')`.
        static_url_path='',
        static_folder=CFG_WEBDIR)

    # Handle both url with and without trailing slashe by Flask.
    # @blueprint.route('/test')
    # @blueprint.route('/test/') -> not necessary when strict_slashes == False
    _app.url_map.strict_slashes = False

    # Load invenio.conf
    _app.config.from_object(config)

    # Load invenio.cfg
    _app.config.from_pyfile('invenio.cfg')

    ## Update application config from parameters.
    _app.config.update(kwargs_config)

    # Register extendsions listed in invenio.cfg
    register_extensions(_app)

    # Extend application config with packages configuration.
    register_configurations(_app)

    ## Database was here.

    ## First check that you have all rights to logs
    #from invenio.bibtask import check_running_process_user
    #check_running_process_user()

    from invenio.messages import language_list_long

    # Jinja2 hacks were here.
    # See note on Jinja2 string decoding using ASCII codec instead of UTF8 in
    # function documentation

    # SECRET_KEY is needed by Flask Debug Toolbar
    SECRET_KEY = _app.config.get('SECRET_KEY') or CFG_SITE_SECRET_KEY
    if not SECRET_KEY or SECRET_KEY == '':
        fill_secret_key = """
    Set variable CFG_SITE_SECRET_KEY with random string in invenio-local.conf.

    You can use following commands:
    $ %s
    $ %s
        """ % (CFG_BINDIR + os.sep + 'inveniocfg --create-secret-key',
               CFG_BINDIR + os.sep + 'inveniocfg --update-config-py')
        try:
            raise Exception(fill_secret_key)
        except Exception:
            register_exception(alert_admin=True,
                               subject="Missing CFG_SITE_SECRET_KEY")
            raise Exception(fill_secret_key)

    _app.config["SECRET_KEY"] = SECRET_KEY

    # Debug toolbar was here

    # Set email backend for Flask-Email plugin

    # Mailutils were here

    # SSLify was here

    # Legacy was here

    # Jinja2 Memcache Bytecode Cache was here.

    # Jinja2 custom loader was here.

    # SessionInterface was here.

    ## Set custom request class was here.

    ## ... and map certain common parameters
    _app.config['CFG_LANGUAGE_LIST_LONG'] = [(lang, longname.decode('utf-8'))
        for (lang, longname) in language_list_long()]

    ## Invenio is all using str objects. Let's change them to unicode
    _app.config.update(unicodifier(dict(_app.config)))

    from invenio.base import before_request_functions
    before_request_functions.setup_app(_app)

    # Cache was here

    # Logging was here.

    # Login manager was here.

    # Main menu was here.

    # Jinja2 extensions loading was here.

    # Custom template filters were here.

    # Gravatar bridge was here.

    # Set the user language was here.

    # Custom templete filters loading was here.

    def _invenio_blueprint_plugin_builder(plugin):
        """
        Handy function to bridge pluginutils with (Invenio) blueprints.
        """
        from invenio.webinterface_handler_flask_utils import InvenioBlueprint
        if 'blueprint' in dir(plugin):
            candidate = getattr(plugin, 'blueprint')
            if isinstance(candidate, InvenioBlueprint):
                if candidate.name in CFG_FLASK_DISABLED_BLUEPRINTS:
                    _app.logger.info('%s is excluded by CFG_FLASK_DISABLED_BLUEPRINTS' % candidate.name)
                    return
                return candidate
        _app.logger.error('%s is not a valid blueprint plugin' % plugin.__name__)


    ## Let's load all the blueprints that are composing this Invenio instance
    _BLUEPRINTS = [m for m in map(_invenio_blueprint_plugin_builder,
                                  collect_blueprints(app=_app))
                   if m is not None]

    ## Let's attach all the blueprints
    for plugin in _BLUEPRINTS:
        _app.register_blueprint(plugin,
                                url_prefix=_app.config.get(
                                    'BLUEPRINTS_URL_PREFIXES',
                                    {}).get(plugin.name))

    # Flask-Admin was here.

    return _app
