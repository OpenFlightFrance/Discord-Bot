import requests, json, sqlite3, os, datetime, dateutil.parser, datetime

class VatsimData():

  def __init__(self):
    self.url = "https://data.vatsim.net/v3/vatsim-data.json"
    self.dbname = "./db/VatsimData.db"

    self.ratings = {
      1: "OBS",
      2: "S1",
      3: "S2",
      4: "S3",
      5: "C1",
      6: "C2",
      7: "C3",
      8: "I1",
      9: "I2",
      10: "I3",
      11: "SUP",
      12: "ADM"
    }
    self.__selfCheck()

  def __selfCheck(self):
    if not "VatsimData.db" in os.listdir('./db'):
      self.__makeDatabase()
      self.__makeActiveTable()
  
  def __connector(self):
    conn = sqlite3.connect(self.dbname)
    c = conn.cursor()
    return conn, c
  
  def __makeDatabase(self):
    conn, c = self.__connector()
    conn.close()
    return
  
  def __makeActiveTable(self):
    conn, c = self.__connector()
    c.execute("""CREATE TABLE active_atc (
      callsign text,
      name text,
      rating text,
      since text
    )""")
    conn.commit()
    conn.close()
    return
  
  def updateActiveData(self):
    response = requests.get(self.url).text
    response = json.loads(response)['controllers']

    conn, c = self.__connector()
    query = "DELETE FROM active_atc"
    c.execute(query)
    conn.commit()

    for d in response:
      if d['callsign'][:2] == "LF" and not d['callsign'][5:] == "ATIS" and not d['rating'] == 1:
        timefrom = dateutil.parser.isoparse(d['logon_time'])
        timenow = datetime.datetime.now().astimezone()
        deltatime = timenow-timefrom

        query = f"INSERT INTO active_atc VALUES(?, ?, ?, ?)"
        values = (
          d['callsign'],
          d['name'],
          self.ratings[int(d['rating'])],
          str(deltatime).split('.')[0],
        )
        c.execute(query, values)
        conn.commit()  
    conn.close()

  def fetchATC(self):
    conn, c = self.__connector()

    data = []
    
    query = "SELECT * FROM active_atc"
    c.execute(query)
    result = c.fetchall()
    if not len(result) == 0:
      for r in result:
        add = {
          'callsign': r[0],
          'name': r[1],
          'rating': r[2],
          'since': r[3]
        }
        data.append(add)
    conn.close()
    return data