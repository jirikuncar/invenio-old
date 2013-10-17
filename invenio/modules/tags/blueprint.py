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
    invenio.modules.tags.blueprint
    ------------------------------

    Tagging interface.
"""

# Flask
from flask import render_template, request, flash, redirect, url_for, \
        jsonify, Blueprint
from invenio.base.i18n import _
from invenio.base.decorators import wash_arguments, templated
from flask.ext.login import current_user, login_required

# External imports
from invenio.modules.account.models import User
from invenio.modules.record_editor.models import Bibrec
from invenio.modules.search.models import Collection
from invenio.modules.search.blueprint import response_formated_records
from invenio.ext.menu import register_menu
from invenio.ext.breadcrumb import default_breadcrumb_root, register_breadcrumb
from invenio.ext.sqlalchemy import db

# Internal imports
from .models import \
    WtgTAG, \
    WtgTAGRecord, \
    WtgTAGUsergroup, \
    wash_tag

# Forms
from .forms import \
    CreateTagForm, \
    AttachTagForm, \
    DetachTagForm, \
    DeleteTagForm, \
    validate_tag_exists, \
    validate_user_owns_tag, \
    validators


blueprint = Blueprint('webtag', __name__, url_prefix='/yourtags',
                      template_folder='templates', static_folder='static')

default_breadcrumb_root(blueprint, '.webaccount.tags')


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/display', methods=['GET', 'POST'])
@blueprint.route('/display/cloud', methods=['GET', 'POST'])
@login_required
@templated('tags/display_cloud.html')
@register_menu(blueprint, 'personalize.tags', _('Your Tags'))
@register_breadcrumb(blueprint, '.', _('Your Tags'))
def display_cloud():
    """ List of user's private/group/public tags """
    user = User.query.get(current_user.get_id())
    tags = user.tags_query.order_by(WtgTAG.name).all()

    # Calculate document count for each tag
    min_count = 0
    max_count = 0
    for tag in tags:
        if tag.record_count > max_count:
            max_count = tag.record_count
        if tag.record_count < min_count:
            min_count = tag.record_count

    difference = float(max_count - min_count)
    if not difference:
        difference = 1.0

    # Assign sizes
    min_size = 1.0
    max_size = 2.0

    for tag in tags:
        size = min_size + \
                   float(max_size - min_size) * \
                   float(tag.record_count - min_count) / difference

        tag.css_size = str(size*100)

    return dict(user_tags=tags,
                display_mode='cloud')

@blueprint.route('/display/list', methods=['GET', 'POST'])
@login_required
@templated('tags/display_list.html')
@wash_arguments({'sort_by': (unicode, 'name'),
                                 'order': (unicode, '')})
@register_breadcrumb(blueprint, '.list', _('Display as List'))
def display_list(sort_by, order):
    """ List of user's private/group/public tags """
    tags = User.query.get(current_user.get_id()).tags_query

    sort_by = str(sort_by)
    order = str(order)

    if sort_by == 'record_count':
        tags = tags.order_by(WtgTAG.record_count)
    else:
        tags = tags.order_by(WtgTAG.name)

    tags = tags.all()

    if order == 'desc':
        tags.reverse()

    return dict(user_tags=tags,
                display_mode='list')


@blueprint.route('/tag/<int:id_tag>/records', methods=['GET', 'POST'])
@login_required
@register_breadcrumb(blueprint, '.tags_details', _('Associated Records'))
def tag_details(id_tag):
    """ List of documents attached to this tag """

    if not id_tag:
        flash(_('Invalid tag id'), "error")
        return redirect(url_for('.display_cloud'))

    tag = WtgTAG.query.get(id_tag)

    if not tag:
        flash(_('Invalid tag id'), "error")
        return redirect(url_for('.display_cloud'))

    if tag.id_user != current_user.get_id():
        flash(_('You are not authorized to view this tag'), "error")
        return redirect(url_for('.display_cloud'))

    if not tag.records:
        flash(_('There are no documents tagged with ') + tag.name)
        return redirect(url_for('.display_cloud'))

    return response_formated_records([bibrec.id for bibrec in tag.records],
                              Collection.query.get(1),
                              'hb')

@blueprint.route('/tokenize/<int:id_bibrec>', methods=['GET', 'POST'])
@login_required
@wash_arguments({'q': (unicode, '')})
def tokenize(id_bibrec, q):
    """ Data for tokeninput """
    user = db.session.query(User).get(current_user.get_id())

    # Output only tags unattached to this record
    record = db.session.query(Bibrec).get(id_bibrec)

    tags = db.session.query(WtgTAG)\
        .filter_by(user=user)\
        .filter(WtgTAG.name.like('%'+ q +'%'))\
        .filter(db.not_(WtgTAG.records.contains(record)))\
        .order_by(WtgTAG.name)

    # If a tag with searched name does not exist, lets suggest creating it
    # Clean the name
    new_name = wash_tag(q)
    add_new_name = True

    response_tags = []
    for tag in tags.all():
        tag_json = tag.serializable_fields(['id', 'name'])
        response_tags.append(tag_json)

        # Check if it matches the search name
        if tag_json['name'] == new_name:
            add_new_name = False

    #If the name was not found
    if add_new_name:
        tag_json = {'id': 0, 'name': new_name}
        response_tags.append(tag_json)

    return jsonify(dict(results=response_tags, query=q))


@blueprint.route('/record/<int:id_bibrec>/edit', methods=['GET', 'POST'])
@login_required
def editor(id_bibrec):
    """Edits your tags for `id_bibrec`.

    :param id_bibrec: record identifier"""
    user = db.session.query(User).get(current_user.get_id())
    record = db.session.query(Bibrec).get(id_bibrec)

    tags = db.session.query(WtgTAG)\
        .filter_by(user=user)\
        .filter(WtgTAG.records.contains(record))

    tags_json = []
    for tag in tags.all():
        fields = tag.serializable_fields(['id', 'name'])
        fields['can_remove'] = True
        tags_json.append(fields)

    # invenio_templated cannot be used,
    # because this view is requested using AJAX
    return render_template('tags/editor.html', id_bibrec=id_bibrec,
                                                 record_tags=tags_json)

#Temporary solution to call validators, we need a better one
class Field(object):
    def __init__(self, attr, value):
        setattr(self, attr, value)

@blueprint.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    """ Delete a tag """
    response = {}
    response['action'] = 'delete'

    id_tags = request.values.getlist('id_tag', type=int)

    # Validate
    for id_tag in id_tags:
        try:
            field = Field('data', id_tag)
            validate_tag_exists(None, field)
            validate_user_owns_tag(None, field)
        except validators.ValidationError, ex:
            flash(ex.message, 'error')

    db.session.query(WtgTAG)\
        .filter(WtgTAG.id.in_(id_tags))\
        .delete(synchronize_session=False)

    flash(_('Successfully deleted tags.'),'success')

    return redirect(url_for('.display_list'))

# AJAX
# reposnse template:
#   action = name of action 'create' 'attach' 'detach'
#   success = True / False
#
#   if success:
#       id_tag = id of tag participating in process
#       id_bibrec = id of bibrec (if present in action)
#       items = created or deleted model objects
#
#   else:
#       errors = dict of errors from form

@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
@register_breadcrumb(blueprint, '.create', _('New tag'))
@templated('tags/create.html')
def create():
    """ Create a new tag """
    response = {}
    response['action'] = 'create'

    user = db.session.query(User).get(current_user.get_id())

    form = CreateTagForm(request.values, csrf_enabled=False)

    if form.validate_on_submit() or\
       (request.is_xhr and form.validate()) :
        new_tag = WtgTAG()
        form.populate_obj(new_tag)
        new_tag.user = user
        db.session.add(new_tag)
        db.session.flush()
        db.session.refresh(new_tag)

        if 'id_bibrec' in form.data and form.data['id_bibrec']:
            record = db.session.query(Bibrec).get(form.data['id_bibrec'])
            new_tag.records.append(record)
            db.session.add(new_tag)
            response['id_bibrec'] = form.data['id_bibrec']

        db.session.commit()
        db.session.refresh(new_tag)

        response['success'] = True
        response['id_tag'] = new_tag.id
        response['items'] = [new_tag.serializable_fields()]

        if request.is_xhr:
            return jsonify(response)
        else:
            return redirect(url_for('.display_list'))
    else:
        if request.is_xhr:
            response['success'] = False
            response['errors'] = form.errors

            return jsonify(response)
        else:
            return dict(form=form)

@blueprint.route('/attach', methods=['GET', 'POST'])
@login_required
def attach():
    """ Attach a tag to a record """
    response = {}
    response['action'] = 'attach'

    # Ajax - disable csrf
    form = AttachTagForm(request.values, csrf_enabled=False)

    if form.validate():
        association = WtgTAGRecord()
        form.populate_obj(association)

        db.session.add(association)
        db.session.commit()

        response['success'] = True
        response['id_tag'] = association.id_tag
        response['id_bibrec'] = association.id_bibrec
        response['items'] = [association.serializable_fields()]

    else:
        response['success'] = False
        response['errors'] = form.errors

    return jsonify(response)

@blueprint.route('/detach', methods=['GET', 'POST'])
@login_required
def detach():
    """ Detach a tag from a record """
    response = {}
    response['action'] = 'detach'

    # Ajax - disable csrf
    form = DetachTagForm(request.values, csrf_enabled=False)

    if form.validate():
        association = db.session.query(WtgTAGRecord)\
                      .filter_by(id_tag = form.data['id_tag'],
                                 id_bibrec = form.data['id_bibrec']).first()
        if association:
            db.session.delete(association)
            db.session.commit()

        response['success'] = True
        response['id_tag'] = association.id_tag
        response['id_bibrec'] = association.id_bibrec
        response['items'] = [association.serializable_fields()]

    else:
        response['success'] = False
        response['errors'] = form.errors

    return jsonify(response)
