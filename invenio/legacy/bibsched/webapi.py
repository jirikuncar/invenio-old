## This file is part of Invenio.
## Copyright (C) 2011, 2012 CERN.
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

# pylint: disable=C0103
"""Invenio BibSched live view engine implementation"""

from flask import url_for

from invenio.config import CFG_SITE_URL, CFG_BINDIR, CFG_PREFIX
from invenio.legacy.dbquery import run_sql

import os
import subprocess
import time


def get_css():
    """
    Get css styles
    """
    return """
           <style type="text/css">
           .task_waiting {
               color: #ccbb22;
           }
           .task_running {
               color: #33bb22;
           }
           .task_error {
               color: #dd1100;
           }
           .admin_row_color{
               background-color:#EBF7FF;
           }
          .last_updated {
               color:#787878;
               font-size:13px;
               font-style:italic;
          }
          .mode {
               font-size:14px;
          }
          .bibsched_status {
               font-size:14px;
          }

          .clean_error{
            border:solid 1px #CC0000;
            background:#F7CBCA;
            color:#CC0000;
            font-size:14px;
            font-weight:bold;
            padding:4px;
            max-width: 650px;
        }

           </style>
           """

def get_javascript():
    """
    Get all required scripts
    """
    js_scripts = """<script type="text/javascript" src="%(site_url)s/js/jquery.min.js">
                    </script>
                    <script type="text/javascript" src="%(custom)s">
                    </script>
                 """ % {'site_url':CFG_SITE_URL,
                        'custom': url_for('scheduler.static',
                                          filename='js/scheduler/base.js') }
    return js_scripts

def get_bibsched_tasks():
    """
    Run SQL query to get all tasks present in bibsched queue
    """
    waiting_tasks = run_sql("SELECT id,proc,priority,user,runtime,status,progress FROM schTASK WHERE (status='WAITING' OR status='SLEEPING') ORDER BY priority DESC, runtime ASC, id ASC")
    other_tasks = run_sql("SELECT id,proc,priority,user,runtime,status,progress\
                           FROM schTASK WHERE status IN ('RUNNING',\
                           'CONTINUING','SCHEDULED','ABOUT TO STOP',\
                           'ABOUT TO SLEEP', 'DONE WITH ERRORS')")
    return waiting_tasks + other_tasks

def get_bibsched_mode():
    """
    Gets bibsched running mode: AUTOMATIC or MANUAL
    """
    process = subprocess.Popen([os.path.join(CFG_BINDIR, 'bibsched'), 'status'], stdout=subprocess.PIPE)
    output = process.communicate()[0]
    try:
        status = output.split('\n')[1].split()[-1]
        if status in ['MANUAL', 'AUTOMATIC']:
            return status
        else:
            return 'Unknown'
    except IndexError:
        return 'Unknown'

def get_motd_msg():
    """
    Gets content from motd file
    """
    motd_path = os.path.join(CFG_PREFIX, "var", "run", "bibsched.motd")
    try:
        motd_msg = open(motd_path).read().strip()
    except IOError:
        return ""
    if len(motd_msg) > 0:
        return "MOTD [%s] " % time.strftime("%Y-%m-%d %H:%M",time.localtime(os.path.getmtime(motd_path))) + motd_msg
    else:
        return ""
