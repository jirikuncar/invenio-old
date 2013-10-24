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
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.from invenio.ext.cache import cache

#FIXME: add signal management and relation between them

from invenio.ext.cache import cache

field_definitions = cache.get('RECORD_FIELD_DEFINITIONS')
legacy_field_matchings = cache.get('LEGACY_FIELD_MATCHINGS')

if field_definitions is None or legacy_field_matchings is None:
    print ">>> Recreating the cache for fields!"
    from invenio.core.record.config_engine import FieldParser
    field_definitions, legacy_field_matchings = FieldParser().create()
    cache.set('RECORD_FIELD_DEFINITIONS', field_definitions)
    cache.set('LEGACY_FIELD_MATCHINGS', legacy_field_matchings)

model_definitions = cache.get('RECORD_MODEL_DEFINITIONS')
if model_definitions is None:
    print ">>> Recreating the cache for models"
    from invenio.core.record.config_engine import ModelParser
    model_definitions = ModelParser().create()
    cache.set('RECORD_MODEL_DEFINITIONS', model_definitions)
