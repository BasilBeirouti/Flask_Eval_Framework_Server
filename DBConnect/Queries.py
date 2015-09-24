__author__ = 'basilbeirouti'

from DBConnect import BorgConnect
import numpy as np
import csv

borg = BorgConnect()

#person lookup table context
@borg.with_connection
def lookupdict(cur, *args, **kwargs):
    query_lookup = """
SELECT
  DISTINCT person.row_wid, person.first_name, person.last_name, person.person_id
FROM
  emcas_engr_s360.profiles_person_it as person
  WHERE type like '%E%'
  ;
        """
    cur.execute(query_lookup)
    rows = cur.fetchall()
    return rows

def build_lookup_dict():
    rows = lookupdict()
    out = dict()
    out.update((tup[0],(tup[1], tup[2])) for tup in rows)
    return out

@borg.with_connection
def whoson(cur, *args, **kwargs):
    #in the query below, remember to remove the - and + CAST('50 hours' as interval) from the last line
    #it is only to get more data. Once all the data is in that table there's no need to artificially expand the query.
    query_whos_on =         """
    SELECT
        shift.person_id, shift.shift_start_date, shift.shift_duration
    FROM
        emcas_engr_s360.profiles_person_shift as shift
    WHERE
        (shift.shift_start_date, shift.shift_start_date + CAST(shift.shift_duration/60-1 || 'HOURS' as INTERVAL))
    OVERLAPS
        (now()::timestamp, now()::timestamp);
                            """
    print("in whoson")
    cur.execute(query_whos_on)
    print("executed with cursor")
    rows = cur.fetchall()
    print("returned results")
    return rows

def writetodisk(personids, filehandle):
    arr = np.asarray(personids, dtype = np.int32)
    np.save(filehandle, arr)

def updatelist(filehandle):
    rows = whoson()
    #get the personids out of the list of tuples
    personids = list(set(int(tup[0]) for tup in rows))
    writetodisk(personids, filehandle)
    return personids

@borg.with_connection
def srdata(cur, *args, **kwargs):
    query_srdata = "SELECT DISTINCT work.sr_num, work.sr_owner_person_id, work.sr_owner, work.problem_description FROM emcas_engr_s360.profiles_work_it as work;"
    cur.execute(query_srdata)
    rows = cur.fetchall()
    return rows

@borg.with_connection
def getwork(cur, *args, **kwargs):
    query_getwork = """
    SELECT
    DISTINCT SR.SRVC_REQ_NUM AS SR_NUM,
    WPD.EMPL_BDGE_NUM AS SR_OWNER_PERSON_ID,
    RSR.PERS_FULL_NM AS SR_OWNER,
    SR.SRVC_REQ_PROB_TEXT AS PROBLEM_DESCRIPTION
    FROM
    EMCAS_ENGR_S360.W_SERVICE_REQUEST_D SR,
    EMCAS_ENGR_S360.W_RESOURCE_ROLE_REF RSR,
    EMCAS_ENGR_S360.W_PERSON_D WPD
    WHERE
    SR.SRVC_REQ_OWNR_RSRC_ID = RSR.RSRC_ID
    AND
    RSR.PERS_11I_ID = WPD.PERS_11I_ID
    AND
    SR.SRVC_REQ_CRTE_DT;
        """
    cur.execute(query_getwork)
    with open("RawData/getwork.csv", 'wt') as csvfile:
        spamwriter = csv.writer(csvfile)
        for row in cur:
            spamwriter.writerow(row)
    cur.close()

@borg.with_connection
def getalltses(cur, *args, **kwargs):
    query_getalltses = """
    SELECT
    DISTINCT PERSON.EMPL_BDGE_NUM AS PERSON_ID,
    PERSON.PERS_FIRST_NM AS FIRST_NAME,
    PERSON.PERS_LAST_NM AS LAST_NAME
    FROM
    EMCAS_ENGR_S360.W_PERSON_D AS PERSON
    WHERE EMC_EMP_TYPE LIKE 'Employee'
    AND PERSON.EMPL_BDGE_NUM is not NULL;
"""
    cur.execute(query_getalltses)
    with open("RawData/getalltses.csv", 'wt') as csvfile:
        spamwriter = csv.writer(csvfile)
        for row in cur:
            spamwriter.writerow(row)
    cur.close()



