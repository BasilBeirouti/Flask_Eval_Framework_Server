__author__ = 'basilbeirouti'

from DBConnect import BorgConnect
import numpy as np

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