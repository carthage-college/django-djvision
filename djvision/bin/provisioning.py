#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
# env
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/')
sys.path.append('/usr/local/lib/python2.7/dist-packages/')
sys.path.append('/data2/django_1.11/')
sys.path.append('/data2/django_projects/')
sys.path.append('/data2/django_third/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djvision.settings.shell')

import django
django.setup()

from django.conf import settings

# informix environment
os.environ['INFORMIXSERVER'] = settings.INFORMIXSERVER
os.environ['DBSERVERNAME'] = settings.DBSERVERNAME
os.environ['INFORMIXDIR'] = settings.INFORMIXDIR
os.environ['ODBCINI'] = settings.ODBCINI
os.environ['ONCONFIG'] = settings.ONCONFIG
os.environ['INFORMIXSQLHOSTS'] = settings.INFORMIXSQLHOSTS
os.environ['LD_LIBRARY_PATH'] = settings.LD_LIBRARY_PATH
os.environ['LD_RUN_PATH'] = settings.LD_RUN_PATH

from djvision.core.sql import (
    INSERT_CVID_RECORD, INSERT_DETAIL_RECORD, INSERT_EMAIL_RECORD
)
from djvision.core.sql import SELECT_NEW_PEOPLE
from djvision.core.data import ProvisioningBatchRec

from djzbar.utils.informix import do_sql
from djzbar.utils.informix import get_session
from djzbar.settings import INFORMIX_EARL_TEST
from djzbar.settings import INFORMIX_EARL_PROD

from openpyxl import Workbook
from openpyxl import load_workbook

import csv
import time
import argparse
import logging


"""
provising framework for new students and employees
"""

# set up command-line options
desc = """
Accepts as input a database name
"""

parser = argparse.ArgumentParser(description=desc)

parser.add_argument(
    '-d', '--database',
    required=True,
    help="Database name (cars or train).",
    dest='database'
)
parser.add_argument(
    '-f', '--filetype',
    required=True,
    help="File type (csv or xlsx).",
    dest='filetype'
)
parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test'
)

TIMESTAMP = time.strftime("%Y%m%d%H%M%S")

# standard logging
info_logger = logging.getLogger('info_logger')
debug_logger = logging.getLogger('debug_logger')
error_logger = logging.getLogger('error_logger')
# create a logger for collecting failed inserts
provisioning_logger = logging.getLogger('provisioning_logger')


def _generate_files(results, filetype, group):
    """
    Active Directory required fields in order:

        loginID, lastName, firstName, nameID,
        [facultyStatus, staffStatus, studentStatus, retireStatus,]
        dob, zip, acct-types, proxID, phoneExt, depts

    at least one of the Status fields must be populated with an 'A'
    or an 'R' for the retireStatus field
    """

    if test:
        sendero = settings.PROVISIONING_DATA_DIRECTORY_TEST
    else:
        sendero = settings.PROVISIONING_DATA_DIRECTORY

    root = '{}{}_{}'.format(sendero, group, TIMESTAMP)

    if filetype == 'csv':
        # create .csv file
        csvphile = ('{}.csv'.format(root))
        phile = open(csvphile,"w")
        output = csv.writer(phile, quoting=csv.QUOTE_ALL)

        for result in results:
            output.writerow(result)

        # close the csv file
        phile.close()

    elif filetype == 'xlsx':
        # load our XLSX template
        phile = load_workbook(
            '{}/static/xml/{}.xlsx'.format(settings.ROOT_DIR, group)
        )
        # obtain the active worksheet
        ws = phile.active

        for result in results:
            row = []
            for r in result:
                row.append(r)
            ws.append(row)

        # Save the xml file
        phile.save('{}.xlsx'.format(root))
        # close the xml file
        phile.close()

    else: # we will never arrive here but just in case
        if test:
            print("filetype must be: 'csv' or 'xlsx'\n")
            parser.print_help()
        else:
            info_logger.info("filetype must be: 'csv' or 'xlsx'")
        phile = None

    return phile


def main():
    """
    main function
    """

    key = settings.INFORMIX_DEBUG

    if filetype not in ['csv','xlsx']:
        if test:
            print("filetype must be: 'csv' or 'xlsx'\n")
            parser.print_help()
        else:
            info_logger.info("filetype must be: 'csv' or 'xlsx'")
        exit(-1)

    if database == 'train':
        EARL = INFORMIX_EARL_TEST
    elif database == 'cars':
        EARL = INFORMIX_EARL_PROD
    else:
        if test:
            print("database must be: 'cars' or 'train'\n")
            parser.print_help()
        else:
            info_logger.info("database must be: 'cars' or 'train'")
        exit(-1)

    sql = SELECT_NEW_PEOPLE(where = '')

    if test:
        debug_logger.debug("new people sql")
        debug_logger.debug("sql = {}".format(sql))

    people = []
    objects = do_sql(sql, key=key, earl=EARL)

    # the people list allows us to iterate over the result set more
    # than once, whereas just using objects result would throw an
    # error after the first iteration.
    for o in objects:
        if test:
            debug_logger.debug(o)
        people.append(o)

    if people:
        length = len(people)
        sitrep = 1
        notes = ''

        session = get_session(EARL)

        response = _generate_files(people, filetype, 'new_people')

        if not response:
            sitrep = 0
            info_logger.info("{} file was not generated".format(filetype))
            info_logger.info("people = {}".format(people))

            # create batch record
            rec = ProvisioningBatchRec(
                total = length, sitrep = sitrep, notes = notes
            )
            session.add(rec)
            session.commit()
        else:
            # create batch record
            rec = ProvisioningBatchRec(
                total = length, sitrep = sitrep, notes = notes
            )
            session.add(rec)
            session.commit()

            # batch record ID
            rid = rec.batch_no

            for p in people:
                notes = ''
                csv = '|'.join(
                    ['{}'.format(value) for (key, value) in p.items()]
                )
                if test:
                    debug_logger.debug("csv = {}".format(csv))

                try:
                    sql = INSERT_EMAIL_RECORD(cid=p.id, ldap=p.loginid)
                    if test:
                        debug_logger.debug(
                            "INSERT_EMAIL_RECORD = {}".format(sql)
                        )
                    else:
                        do_sql(sql, key=key, earl=EARL)
                except:
                    notes += "failed insert = {}|{}|".format(p,sql)
                    provisioning_logger.info(
                        "INSERT_EMAIL_RECORD fail = {}|{}".format(p,sql)
                    )

                try:
                    sql = INSERT_CVID_RECORD(cid=p.id, ldap=p.loginid)
                    if test:
                        debug_logger.debug(
                            "INSERT_CVID_RECORD = {}".format(sql)
                        )
                    else:
                        do_sql(sql, key=key, earl=EARL)
                except:
                    notes += "failed insert = {}|{}".format(p,sql)
                    provisioning_logger.info(
                        "INSERT_CVID_RECORD fail = {}|{}".format(p,sql)
                    )

                # convert datetime object to string because informix
                try:
                    dob = p.dob.strftime("%m-%d-%Y")
                except:
                    dob = None

                # insert detail record
                sql = INSERT_DETAIL_RECORD(
                    batch_id = rid, username = p.loginid,
                    last_name = p.lastname, first_name = p.firstname,
                    cid = p.id, faculty = p.facultystatus,
                    staff = p.staffstatus, student = p.studentstatus,
                    retire = p.retirestatus, dob = dob,
                    postal_code = p.zip, account = p.accttypes,
                    proxid = p.proxid, phone_ext = p.phoneext,
                    departments = p.depts, csv = csv, notes = notes
                )

                try:
                    if test:
                        debug_logger.debug("sql = {}".format(sql))
                    do_sql(sql, key=key, earl=EARL)
                except Exception as e:
                    provisioning_logger.info("insert fail: p = {}".format(p))
                    if test:
                        error_logger.error("sql fail = {}".format(e))
                        print("die: sql fail")
                        exit(-1)

        session.close()
    else:
        if test:
            print("No objects found for provisioning.")
        else:
            info_logger.info("No objects found for provisioning.")


######################
# shell command line
######################

if __name__ == '__main__':
    args = parser.parse_args()
    test = args.test
    database = args.database.lower()
    filetype = args.filetype.lower()
    sys.exit(main())
