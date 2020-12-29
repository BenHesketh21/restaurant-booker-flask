import datetime

print(datetime.datetime.strptime("17:00:00", "%H:%M:%S")+datetime.timedelta(hours=-1))