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

def import_extension(directories, extension_name):
    """
        Searches EXTENSION_DIRECTORIES for the desired extension;

        returns (setup_app, config)
    """

    for directory in directories:
        ext_path = '{directory}{dot}{name}'.format(
            directory=directory,
            dot=('.' if directory else ''),
            name=extension_name)

        try:
            ext_module = import_string(ext_path)
            ext_setup = getattr(ext_module, 'setup_app', None)
            ext_config = getattr(ext_module, 'config', None)
            if not ext_config:
                try:
                    ext_config = import_string(ext_path + '.config')
                except:
                    pass
            return (ext_setup, ext_config)

        except:
            # Extension not found here, keep looking
            pass

    try:
        # Maybe it is a callable extensions
        ext_module = import_string(extension_name)
        return (ext_module, None)
    except:
        # TODO Write to 'missing-extensions.log'
        return (None, None)


def register_extensions(app):
    for ext_name in app.config.get('EXTENSIONS', []):
        (ext_setup, ext_config) = import_extension(
            app.config.get('EXTENSION_DIRECTORIES', ['']),
            ext_name)
        if ext_config:
            app.config.from_object(ext_config)

        if ext_setup:
            try:
                new_app = ext_setup(app)
                if new_app is not None:
                    app = new_app
            except Exception as e:
                print ext_name, e
                # TODO Write to 'broken-extensions.log'
                pass

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

def collect_blueprints(app=None):
    return chain(
        partial(import_module_from_packages, 'blueprint')(app),
        partial(import_module_from_packages, 'admin_blueprint')(app)
    )

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
