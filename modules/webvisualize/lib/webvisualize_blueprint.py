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

"""WebVisualize Flask Blueprint"""

from datetime import datetime
import socket

from flask import g, render_template, request, flash, redirect, url_for, \
    current_app, abort, jsonify

from invenio.webinterface_handler_flask_utils import _, InvenioBlueprint
from invenio.webuser_flask import current_user

from invenio.sqlalchemyutils import db
from invenio.webvisualize_model import VslConfig

blueprint = InvenioBlueprint('webvisualize', __name__,
                             url_prefix="/visualize",
                             #config='invenio.webcomment_config',
                             breadcrumbs=[(_('Comments'),
                                           'webcomment.subscribtions')],
                             menubuilder=[('personalize.comment_subscriptions',
                                           _('Your comment subscriptions'),
                                           'webvisualize.index', 20)])

from invenio.record_blueprint import request_record


from invenio.importutils import autodiscover_modules
_VISUALIZERS = dict(map(lambda v: (v.Visualizer.graph_type, v.Visualizer),
                        autodiscover_modules(['invenio'], related_name_re=".+_webvisualizer\.py")))


@blueprint.route('/view/<cid>', methods=['GET'])
def view(cid):
    vc = VslConfig.query.get(cid)
    if vc.graph_type in _VISUALIZERS:
        visualizer = _VISUALIZERS[vc.graph_type]()
    else:
        abort(501) # log error unknown type
    return render_template(visualizer.template, visualize_config=vc, 
                           visualizer=visualizer)
    #return render_template('webvisualize_view.html', visualize_config=cid)

@blueprint.route('/index', methods=['GET'])
def index():
    return render_template('webvisualize_index.html')

@blueprint.route('/dataset/<name>.json', methods=['GET'])
def dataset(name):
    vc = VslConfig.query.filter_by(name=name).one()
    return jsonify(vc.json_config)