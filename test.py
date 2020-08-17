# import datetime
# import dateutil.parser

# timefrom = "2020-08-17T13:56:38.380548Z"
# timefrom = dateutil.parser.isoparse(timefrom)

# timenow = datetime.datetime.now().astimezone()

# delta = timenow-timefrom
# print()

from utils.VatsimData import VatsimData

VD = VatsimData()

VD.updateActiveData()