# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.test import TestCase

from djvision.core.sql import INSERT_DETAIL_RECORD, SELECT_NEW_PEOPLE

from djzbar.utils.informix import do_sql
from djzbar.utils.informix import get_session
from djtools.utils.logging import seperator
from djzbar.settings import INFORMIX_EARL_TEST as EARL


class CoreSqlTestCase(TestCase):

    def setUp(self):
        self.cid = settings.TEST_COLLEGE_ID

    def test_select_new_people(self):
        print("\n")
        print("select new people SQL incantations")
        seperator()

        objects = do_sql(SELECT_NEW_PEOPLE, key='debug', earl=EARL)

        for o in objects:
            print("{}|{}|{}|{}|{}".format(
                o.loginid, o.lastname, o.firstname, o.id, o.dob
            ))

    def test_insert_detail_record(self):
        print("\n")
        print("insert detail record SQL incantation")
        seperator()

        sql = SELECT_NEW_PEOPLE(where = 'AND subID.id = {}'.format(self.cid))
        p = do_sql(sql, key='debug', earl=EARL).first()
        print(p)
        print(p.dob)
        # convert datetime object to string because informix
        #dob = p.dob.strftime("%Y-%m-%d")
        dob = p.dob.strftime("%m-%d-%Y")

        sql = INSERT_DETAIL_RECORD(
            batch_id = 40, username = p.loginid,
            last_name = p.lastname, first_name = p.firstname,
            cid = p.id, faculty = p.facultystatus,
            staff = p.staffstatus, student = p.studentstatus,
            retire = p.retirestatus, dob = dob,
            postal_code = p.zip, account = p.accttypes,
            proxid = p.proxid, phone_ext = p.phoneext,
            departments = p.depts, csv = '', notes = ''
        )

        do_sql(sql, key='debug', earl=EARL)
