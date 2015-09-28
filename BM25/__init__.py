__author__ = 'basilbeirouti'


import psycopg2, datetime
import numpy as np

headers = ['id', 'person_id', 'utc_date', 'mins', 'active_utc_date', 'active_mins']
headers = dict(enumerate(headers))
rawcsvfile = "/Users/basilbeirouti/PycharmProjects/Server/RawData/WFM_Schedule.csv"
filteredcsvfile = "/Users/basilbeirouti/PycharmProjects/Server/ApplicationData/Schedule.csv"

class BorgConnect:

    _shared_state = {}

    _dbparams = {"dbname":"cps_dev01",
                 "user":"beirob",
                 "host":"cpsgpmtst01.isus.emc.com",
                 "password":"JU40QY82#1",
                 "port":"6200"}

    # _dbparams = {"dbname":"cps_dev01",
    #              "user":"bracke",
    #              "host":"bdlgmcprd01.isus.emc.com",
    #              "password":"1",
    #              "port": "6400"}

    def __init__(self):
        self.__dict__ = self._shared_state
        self.get_connection()

    def get_connection(self):
        if "conn" in self._shared_state:
            if self._shared_state["conn"].closed == 0:
                return self._shared_state["conn"]
        self._shared_state["conn"] = self._refresh_connection()
        return self._shared_state["conn"]

#used at the very end when you're finished with the database
    def _close_connection(self):
        if "conn" in self._shared_state:
            print("closed a connection") #only place connections are closed
            self._shared_state["conn"].close()

#used in except block after handling an exception to reestablish connection
    def _refresh_connection(self):
        self._close_connection()
        print("opened a new connection") #only place connections are opened
        # self._shared_state["conn"] = psycopg2.connect(**self._dbparams)
        return psycopg2.connect(**self._dbparams)

#decorator that acts as context manager
    def with_connection(self, f):
        def wrapped(*args, **kwargs):
            conn = self.get_connection()
            with conn.cursor() as cur:
                try:
                    out = f(cur, *args, **kwargs)
                    cur.close()
                    return out

                except psycopg2.ProgrammingError as e:
                    cur.close()
                    print("there's an exception")
                    print(e)
                    self._refresh_connection()
        return wrapped

    def __del__(self):
        print("destructor called")
        self._close_connection()
        # if "conn" in self._shared_state:
        #     self._shared_state["conn"].close()

borg = BorgConnect()
@borg.with_connection
def last_thousand(cur, *args, **kwargs):
    person_id = args[0]
    n = args[1]
    query_last_thousand = """
    SELECT
  DISTINCT sr.srvc_req_num as sr_num,
  wpd.empl_bdge_num as sr_owner_bdge_num,
  rsr.pers_11i_id as person_id,
  rsr.pers_first_nm as first_name,
  rsr.pers_last_nm as last_name,
  sr.srvc_req_prob_text as problem_description,
  sr.srvc_req_crte_dt as srvc_req_crte_dt
FROM
  emcas_engr_s360.w_service_request_d as sr,
  emcas_engr_s360.w_resource_role_ref as rsr,
  emcas_engr_s360.w_person_d as wpd
WHERE
  sr.srvc_req_ownr_rsrc_id = rsr.rsrc_id and
  rsr.empl_bdge_num != 'NA' and
  rsr.pers_11i_id = wpd.pers_11i_id and
      rsr.pers_11i_id = """ + str(person_id) + """ and
  sr.srvc_req_crte_dt > now()::TIMESTAMP - cast(365 || 'days' as INTERVAL)
ORDER BY
  srvc_req_crte_dt DESC
  LIMIT """ + str(n) + ";"
    cur.execute(query_last_thousand)
    results = cur.fetchall()
    return results