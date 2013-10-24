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
    invenio.base.utils
    ------------------

    Implements various utils.
"""

from flask import has_app_context, current_app
from werkzeug.utils import import_string, find_modules
from functools import partial
from itertools import chain


def register_extensions(app):
    for ext_name in app.config.get('EXTENSIONS', []):

        ext = import_string(ext_name)
        ext = getattr(ext, 'setup_app', ext)
        #try:

        #except:
        #    continue

#        try:
        ext(app)
        #except Exception as e:
        #    app.logger.error('%s: %s' % (ext_name, str(e)))

    return app


def import_module_from_packages(name, app=None, packages=None):
    if packages is None:
        if app is None and has_app_context():
            app = current_app
        if app is None:
            raise Exception('Working outside application context or provide app')
        packages = app.config.get('PACKAGES', [])

    for package in packages:
        if package.endswith('.*'):
            for module in find_modules(package[:-2], include_packages=True):
                try:
                    yield import_string(module + '.' + name)
                except ImportError:
                    pass
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    app.logger.error('Could not import: "%s.%s: %s',
                                     module, name, str(e))
                    pass
            continue
        try:
            yield import_string(package + '.' + name)
        except ImportError:
            pass
        except Exception as e:
            app.logger.error('Could not import: "%s.%s: %s',
                             package, name, str(e))
            pass

collect_blueprints = partial(import_module_from_packages, 'views')
autodiscover_models = partial(import_module_from_packages, 'model')
autodiscover_user_settings = partial(import_module_from_packages,
                                     'user_settings')
autodiscover_configs = partial(import_module_from_packages, 'config')
autodiscover_managers = partial(import_module_from_packages, 'manage')


def autodiscover_template_context_functions(app=None):
    tcf = partial(import_module_from_packages, 'template_context_functions')
    return [import_string(m) for p in tcf(app)
            for m in find_modules(p.__name__)]


def register_configurations(app):
    """Includes the configuration parameters of the config file.

    E.g. If the blueprint specify the config string `invenio.messages.config`
    any uppercase variable defined in the module `invenio.messages.config` is
    loaded into the system.
    """
    for config in autodiscover_configs(app):
        app.config.from_object(config)
