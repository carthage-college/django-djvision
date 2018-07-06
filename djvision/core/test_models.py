# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.test import TestCase

from djvision.core.data import ProvisioningBatchRec, ProvisioningDetailRec

from djtools.utils.logging import seperator
from djzbar.utils.informix import get_session
from djzbar.settings import INFORMIX_EARL_TEST as EARL


class CoreModelsTestCase(TestCase):

    def setUp(self):
        self.session = get_session(EARL)

    def test_create_batch(self):
        print("\n")
        print("create a batch record")
        seperator()

        session = self.session
        rec = ProvisioningBatchRec(
            total = 4,
            sitrep = 1,
            notes = 'created a test batch record'
        )
        session.add(rec)
        session.flush()
        print("batch ID = {}".format(rec.batch_no))
        session.commit()
        session.close()

    def test_select_detail(self):
        print("\n")
        print("selectd all detail records")
        seperator()

        session = self.session

        objects = session.query(ProvisioningDetailRec).all()
        print("length of objects")
        print(len(objects))
        for o in objects:
            print("{}|{}|{}|{}|{}|{}|{}|{}".format(
                o.username, o.last_name, o.first_name, o.id, o.birth_date,
                o.batch_rec.created_at, o.batch_rec.total, o.batch_rec.sitrep
            ))
