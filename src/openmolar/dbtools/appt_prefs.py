# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

import logging

from openmolar import connect
from openmolar.settings import localsettings

#NOTE - the appt_prefs table has unused columns at this point!

QUERY = '''SELECT recall_active, recdent_period, recdent,
rechyg_period, rechyg, recall_method, note
from appt_prefs where serialno = %s'''

UPDATE_QUERY = '''replace into appt_prefs
        (serialno, recall_active, recdent_period, recdent,
        rechyg_period, rechyg, recall_method, note)
        values (%s,%s,%s,%s,%s,%s,%s,%s)
        '''

class ApptPrefs(object):
    '''
    has a tiny percentage of the footprint (and loading time) of the
    main patient class
    '''
    recall_active = False
    note = ""
    def __init__(self, serialno):
        '''
        initiate the class with default variables, then load from database
        '''
        self.serialno = serialno
        self.recdent_period = None
        self.recdent = None
        self.rechyg_period = None
        self.rechyg = None
        self.recall_method = None

        db = connect.connect()
        cursor = db.cursor()
        cursor.execute(QUERY, (self.serialno,))
        row = cursor.fetchone()

        if not row:
            return

        (self.recall_active, self.recdent_period, self.recdent ,
        self.rechyg_period, self.rechyg,
        self.recall_method, self.note) = row

        if self.note is None:
            self.note = ""
        if self.recall_active is None:
            self.recall_active = False

    def commit_changes(self):
        logging.debug("ApptPrefs committing changes")
        values = (
            self.serialno,
            self.recall_active,
             self.recdent_period, self.recdent ,
            self.rechyg_period, self.rechyg,
            self.recall_method,
            self.note
            )

        db = connect.connect()
        cursor = db.cursor()
        cursor.execute(UPDATE_QUERY, values)
        cursor.close()

    def __repr__(self):
        return str(self.__dict__)

if __name__ =="__main__":
    try:
        serialno=int(sys.argv[len(sys.argv)-1])
    except:
        serialno=11956

    prefs = ApptPrefs(serialno)
    for att in prefs.__dict__.keys():
        print att, prefs.__dict__[att]