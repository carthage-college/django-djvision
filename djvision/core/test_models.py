# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.test import TestCase

from djvision.core.data import ProvisioningBatchRec

from djtools.utils.logging import seperator
from djzbar.utils.informix import get_session
from djzbar.settings import INFORMIX_EARL_TEST as EARL


class AppsSmsModelsTestCase(TestCase):

    def test_create(self):
        print("\n")
        print("create a batch record")
        seperator()

        session = get_session(EARL)
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

