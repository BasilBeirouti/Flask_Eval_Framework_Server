__author__ = 'basilbeirouti'


import psycopg2

class BorgConnect:

    _shared_state = {}

    _dbparams = {"dbname":"<dbname>",
                 "user":"<user>",
                 "host":"<host>",
                 "password":"<password>",
                 "port":"<port>"}

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






