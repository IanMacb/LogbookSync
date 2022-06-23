import csv
import datetime
import astral
from astral.sun import sun



START_DATE = datetime.date(2022, 6, 4)

loc = astral.LocationInfo(name='SFZ', timezone='America/New_York', latitude=41.9208, longitude=-71.4914)
s = sun(loc.observer, date=START_DATE, tzinfo=loc.timezone)
#s['sunset']


with open('Table_5293.csv', 'r', newline='') as csvfile:
    data = csv.DictReader(csvfile)
    with open('Updater.xlsx', 'w', newline='') as updater:
        updater.writelines('ForeFlight Logbook Import\n\nFlights Table\n')
        good = csv.DictWriter(updater, fieldnames=['Date', 'AircraftID', 'From', 'To', 'Route', 'TotalTime', 'PIC', 'Night', 'CrossCountry','DayTakeoffs', 'DayLandingsFullStop', 'NightTakeoffs', 'NightLandingsFullStop', 'AllLandings', 'DualGiven', 'Person1'])
        good.writeheader()
        for i in data:
            d = i['ï»¿"Flight Date"'].split()[0].split('/')
            t = i['ï»¿"Flight Date"'].split()[1:3]
            print(t)
            Date = datetime.date(int(d[2]), int(d[0]), int(d[1]))
            Time = datetime.time(int(t[0].split(':')[0]), int(t[0].split(':')[1]))
            print(Date, Time)
            if Date > START_DATE:
                AircraftID = i['Aircraft']
                if AircraftID != "":
                    AircraftID = AircraftID.split()[0]
                if i['Activity Type'] == 'Intro Flight': Route = 'HHIGH VC401'
                else: Route = ''
                Time = i['Total Flight Instruction']
                Person = ' '.join(i['Customer 1 Name'].split()[:2]) + ';Student;'
                good.writerow({'Date': Date, 'AircraftID': AircraftID, 'From': 'KSFZ', 'To': 'KSFZ', 'Route': Route, 'TotalTime': Time, 'PIC': Time, 'DayTakeoffs': 1, 'DayLandingsFullStop': 1, 'AllLandings': 1, 'DualGiven': Time, 'Person1': Person})