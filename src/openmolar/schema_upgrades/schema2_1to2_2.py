# -*- coding: utf-8 -*-
# Copyright (c) 2012 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
This module provides a function 'run' which will move data
to schema 2_2
'''
from __future__ import division

import logging
import sys
from openmolar.settings import localsettings
from openmolar.dbtools import schema_version
from openmolar import connect

from PyQt4 import QtGui, QtCore

logging.basicConfig()

SQLSTRINGS = [
'drop table if exists currtrtmt',
'drop table if exists est_link',
'update patients set addr2="" where addr2 is NULL',
'update patients set addr3="" where addr3 is NULL',
'update patients set town="" where town is NULL',
'update patients set county="" where town is NULL',

'''
alter table patients 
    alter column addr2 set default "", 
    alter column addr3 set default "",
    alter column town set default "",
    alter column county set default ""
''',

'''
create table est_link (
  ix         int(11) unsigned not null auto_increment ,
  est_id     int(11),
  tx_hash    varchar(20) NOT NULL,
PRIMARY KEY (ix),
INDEX (est_id)
)'''
]

            
SOURCE_QUERY = '''
select courseno, ix, category, type from newestimates 
order by serialno, courseno, category, completed desc, type'''

DEST_QUERY = '''insert into est_link (est_id, tx_hash) 
    values (%s, %s)'''


class UpdateException(Exception):
    '''
    A custom exception. If this is thrown the db will be rolled back
    '''
    pass

class dbUpdater(QtCore.QThread):
    def __init__(self, parent=None):
        super(dbUpdater, self).__init__(parent)
        self.stopped = False
        self.path = None
        self.completed = False
        self.MESSAGE = "upating database"

    def progressSig(self, val, message=""):
        '''
        emits a signal showing how we are proceeding.
        val is a number between 0 and 100
        '''
        if message != "":
            self.MESSAGE = message
        self.emit(QtCore.SIGNAL("progress"), val, self.MESSAGE)

    def execute_statements(self, sql_strings):
        '''
        execute the above commands
        NOTE - this function may fail depending on the mysql permissions
        in place
        '''
        db = connect.connect()
        db.autocommit(False)
        cursor = db.cursor()
        sucess = False
        try:
            i, commandNo = 0, len(sql_strings)
            for sql_string in sql_strings:
                try:
                    cursor.execute(sql_string)
                except connect.GeneralError, e:
                    print "FAILURE in executing sql statement",  e
                    print "erroneous statement was ",sql_string
                    if 1060 in e.args:
                        print "continuing, as column already exists issue"
                self.progressSig(2+70*i/commandNo,sql_string[:40]+"...")
            sucess = True
        except Exception, e:
            print "FAILURE in executing sql statements",  e
            db.rollback()
        if sucess:
            db.commit()
            db.autocommit(True)
        else:
            raise UpdateException("couldn't execute all statements!")

    def completeSig(self, arg):
        self.emit(QtCore.SIGNAL("completed"), self.completed, arg)

    def run(self):
        print "running script to convert from schema 2.0 to 2.2"
        try:
            #- execute the SQL commands
            self.progressSig(5, _("creating est_link table"))
            self.execute_statements(SQLSTRINGS)
            
            self.progressSig(90, _("populating est_link table"))            
            self.transfer_data()

            self.progressSig(97, _('updating settings'))
            print "update database settings..."

            schema_version.update(("2.2",), "2_1 to 2_2 script")

            self.progressSig(100, _("updating stored schema version"))
            self.completed = True
            self.completeSig(_("ALL DONE - sucessfully moved db to")
            + " 2.2")

        except UpdateException, e:
            localsettings.CLIENT_SCHEMA_VERSION = "2.0"
            self.completeSig(_("rolled back to") + " 2.0")

        except Exception, e:
            print "Exception caught",e
            self.completeSig(str(e))

        return self.completed

    def transfer_data(self):
        '''
        function specific to this update.
        '''
        db = connect.connect()
        db.autocommit(False)
        try:
            cursor = db.cursor()
            cursor.execute(SOURCE_QUERY)
            rows = cursor.fetchall()
            cursor.close()
            cursor = db.cursor()
            step = 1 / len(rows)     
            count, prev_courseno, prev_cat_type = 1, 0, "" 
            for i, row in enumerate(rows):
                courseno, ix, category, type_ = row
                cat_type = "%s%s"% (category, type_) 
                if courseno != prev_courseno:
                    count = 1
                    prev_courseno = courseno
                elif cat_type != prev_cat_type:
                    count = 1
                    prev_cat_type = cat_type
                else:
                    count += 1
                    
                tx_hash = hash("%s %s %s"% (category, count, type_))
                values = (ix, tx_hash)
                cursor.execute(DEST_QUERY, values)
                if i % 1000 == 0:
                    self.progressSig(80 * i/len(rows) + 10, 
                    _("transfering data"))
            cursor.close()
            db.commit()
            db.close()
        except Exception as exc:
            logging.exception("error transfering data")
            db.rollback()
            raise UpdateException(exc)

if __name__ == "__main__":
    dbu = dbUpdater()
    if dbu.run():
        print "ALL DONE, conversion sucessful"
    else:
        print "conversion failed"