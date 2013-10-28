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

"""WebTag List of tags in document view"""

# Flask
from flask import url_for
from invenio.ext.template import render_template_to_string
from invenio.base.globals import cfg
from invenio.ext.sqlalchemy import db

# Models
from invenio.modules.tags.models import \
    WtgTAG, \
    WtgTAGRecord

# Related models
from invenio.modules.account.models import User
from invenio.modules.record_editor.models import Bibrec


def template_context_function(id_bibrec, id_user):
    """
    :param id_bibrec: ID of record
    :param id_user: user viewing the record (and owning the displayed tags)
    :return: HTML containing tag list
    """

    if id_user and id_bibrec:
        # Get user settings:
        user = User.query.get(id_user)
        user_settings = user.settings.get(
            'webtag', cfg['CFG_WEBTAG_DEFAULT_USER_SETTINGS'])

        if not user_settings['display_tags']:
            # Do not display if user turned off tags in settings
            return ''

        # Collect tags
        query_results = db.session.query(WtgTAG, WtgTAGRecord.annotation)\
            .filter(WtgTAG.id == WtgTAGRecord.id_tag)\
            .filter(WtgTAGRecord.id_bibrec == id_bibrec).all()

        # Group tags
        #if user_settings.get('display_tags_group', True):
        #.join(UserUsergroup)
        #.filter(or_(_and( UserUsergroup.id_user == id_user, UserUsergroup.id_group == WtgTAG.id_usergroup), WtgTAG.id_user == id_user,

        # Public tags
        #if user_settings.get('display_tags_public', True):

        tag_infos = []

        for (tag, annotation_text) in query_results:
            tag_info = dict(
                id=tag.id,
                name=tag.name,
                owned=(tag.id_user == id_user),
                record_count=tag.record_count,
                annotation=annotation_text,
                label_classes='') #((tag.id_user == id_user) and 'label-tag-owned') or '')

            tag_info['popover_title'] = render_template_to_string(
                'tags/tag_popover_title.html',
                tag=tag_info,
                id_bibrec=id_bibrec)

            tag_info['popover_content'] = render_template_to_string(
                'tags/tag_popover_content.html',
                tag=tag_info,
                id_bibrec=id_bibrec)

            tag_infos.append(tag_info)

        return render_template_to_string(
            'tags/record_tags.html',
            tag_infos=tag_infos,
            id_bibrec=id_bibrec)
    else:
        return ''
