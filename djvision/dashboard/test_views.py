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
        self.created_at_date = settings.TEST_CREATED_AT_DATE

    def test_created_at(self):
        print("\n")
        print("select all records for a specific date")
        seperator()

        session = self.session

        objects = session.query(ProvisioningDetailRec).filter(
            ProvisioningDetailRec.created_at >= self.created_at_date
        ).all()

        print("length of objects")
        print(len(objects))
        for o in objects:
            print("{}|{}|{}|{}|{}|{}|{}|{}".format(
                o.username, o.last_name, o.first_name, o.id, o.birth_date,
                o.batch_rec.created_at, o.batch_rec.total, o.batch_rec.sitrep
            ))
