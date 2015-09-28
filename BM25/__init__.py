__author__ = 'basilbeirouti'


import psycopg2, datetime
import numpy as np

headers = ['id', 'person_id', 'utc_date', 'mins', 'active_utc_date', 'active_mins']
headers = dict(enumerate(headers))

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

def npy_from_csv(schedule):
    wid, person_id, utc_date, mins, active_date, active_mins = zip(*schedule)
    wid, person_id, utc_date, mins, active_date, active_mins = list(wid), list(person_id), list(utc_date), list(mins), list(active_date), list(active_mins)

    schedule_array = np.zeros((len(schedule),),
                          dtype = [('row_id', 'uint32'),
                                   ('person_id', 'uint32'),
                                   ('utc_date', 'a19'),
                                   ('mins', 'uint16'),
                                   ('active_utc_date', 'a19'),
                                   ('active_mins', 'uint16')])
    schedule_array['row_id'] = wid
    schedule_array['person_id'] = person_id
    schedule_array['utc_date'] = utc_date
    schedule_array['mins'] = mins
    schedule_array['active_utc_date'] = active_date
    schedule_array['active_mins'] = active_mins
    return schedule_array
    #u32, u32, str(19), u16, str(19), u16

def schedule_array2list(schedule_array):
    return [list(row) for row in schedule_array]

def make_datetime(schedule):
    for row in schedule:
        row[0], row[1], row[3], row[5] = int(row[0]), int(row[1]), int(row[3]), int(row[5])
        row[2] = datetime.datetime.strptime(bytes.decode(row[2]), "%Y-%m-%d %H:%M:%S")
        row[4] = datetime.datetime.strptime(bytes.decode(row[4]), "%Y-%m-%d %H:%M:%S")
    return schedule

def get_schedule_list():
    schedule_array = np.load(open("/Users/basilbeirouti/PycharmProjects/Server/ApplicationData/Numpy_Schedule.npy", 'rb'))
    out = make_datetime(schedule_array2list(schedule_array))
    return out

schedule_list = get_schedule_list()

def on_now(shift):
    start = shift[2]
    end = shift[2] + datetime.timedelta(minutes = shift[3])
    if start < datetime.datetime.today() < end:
        return True
    return False

def whos_on(schedule_list):
    return [shift for shift in schedule_list if on_now(shift)]

borg = BorgConnect()
@borg.with_connection
def last_thousand(cur, *args, **kwargs):
    badge_num = args[0]
    n = args[1]
    query_last_thousand = """
        SELECT
  DISTINCT sr.srvc_req_num as sr_num,
  wpd.empl_bdge_num as sr_owner_person_id,
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
  wpd.empl_bdge_num =
  """ + str(badge_num) + """
  and
  rsr.pers_11i_id = wpd.pers_11i_id and
  sr.srvc_req_crte_dt > now()::TIMESTAMP - cast(365 || 'days' as INTERVAL)
ORDER BY
  srvc_req_crte_dt DESC
LIMIT
""" + str(n) + ";"
    cur.execute(query_last_thousand)
    results = cur.fetchall()
    return results