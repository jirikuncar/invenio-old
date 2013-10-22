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

        # Collect tags
        tags = []

        # Private tags
        if user_settings.get(
            'display_tags_private',
            cfg['CFG_WEBTAG_SETTINGS_SHOW']) == cfg['CFG_WEBTAG_SETTINGS_SHOW']:

            tags += WtgTAG.query\
                .join(WtgTAGRecord)\
                .filter(
                    WtgTAG.id_user == id_user,
                    WtgTAGRecord.id_bibrec == id_bibrec)\
                .order_by(WtgTAG.name)\
                .all()


            #.join(UserUsergroup)
            #.filter(or_(_and( UserUsergroup.id_user == id_user, UserUsergroup.id_group == WtgTAG.id_usergroup), WtgTAG.id_user == id_user,



        # Group tags
        #if user_settings.get('display_tags_group', True):

        # Public tags
        #if user_settings.get('display_tags_public', True):

        return render_template_to_string('tags/record.html',
                                         id_bibrec=id_bibrec,
                                         record_tags=tags)
    else:
        return ''
