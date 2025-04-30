import json
import databaseTools # for future logging to SQL database
from datetime import datetime
from dataclasses import asdict, dataclass

dbt = None
mode = 1 # 1 = file, 2 = database
filename = None
events = []
counter = 0
database = ""
filelocation = "e:\\temp\\logs\\"

@dataclass
class log:
    id : int
    importance : int
    type : str
    time : str
    message : str
# importance:
# 0 - None
# 1 - Low
# 2 - High
# 3 - Error

class Logger:

    def __init__(self):
        global dbt
        dbt = databaseTools.databaseTools()

    def start(self, name, startmode):
        global mode
        global filename
        mode = startmode
        starttime = datetime.now()
        filename = name + '-' + str(starttime.strftime("%Y-%m-%d-%H%M%S")) + ".log"
    
    def log(self, importance, type, message):
        global counter
        global events
        counter += 1
        recordedlog = log(counter, importance, type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
        events.append(recordedlog)

    def stop(self):
        log_dicts = [asdict(recordedlog) for recordedlog in events]
        logfile = filelocation + filename
        if mode == 1:
            with open(logfile, 'w') as outfile:
                json.dump(log_dicts, outfile, indent = 4)
        else:
            dbt.insert(database, ["id", "importance", "type", "time", "message"], log_dicts, ["int", "int", "str", "str", "str"])
