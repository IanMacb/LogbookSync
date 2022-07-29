import csv
import datetime
import astral
from astral.sun import sun


START_DATE = datetime.date(2010, 11, 8)

loc = astral.LocationInfo(name='SFZ', timezone='America/New_York', latitude=41.9208, longitude=-71.4914)
s = sun(loc.observer, date=START_DATE, tzinfo=loc.timezone)


with open('Table.csv', 'r', newline='') as csvfile:
    data = csv.DictReader(csvfile)
    with open('Updater.csv', 'w', newline='') as updater:
        updater.writelines('ForeFlight Logbook Import\n\nFlights Table\n')
        good = csv.DictWriter(updater, fieldnames=['Date', 'AircraftID', 'From', 'To', 'Route', 'TotalTime', 'PIC', 'Night', 'CrossCountry','DayTakeoffs', 'DayLandingsFullStop', 'NightTakeoffs', 'NightLandingsFullStop', 'AllLandings', 'DualGiven', 'Person1'])
        good.writeheader()
        for i in data:
            d = i['Start'].split()[0].split('/')
            t = i['Start'].split()[1].split(':')
            #HH:MM:SS
            c = i['Start'].split()[2]
            #AM/PM
            h = int(t[0])
            if c == 'PM' and h < 12: h += 12
            DateTime = datetime.datetime(int(d[2]), int(d[0]), int(d[1]), h, int(t[1]), int(t[2]), tzinfo=loc.tzinfo)
            s = sun(loc.observer, date=DateTime.date(), tzinfo=loc.timezone)

            if DateTime.date() > START_DATE:
                AircraftID = i['Aircraft']
                if AircraftID != "":
                    AircraftID = AircraftID.split()[0]
                if i['Activity Type'] == 'Intro Flight': Route = 'VC401'
                else: Route = ''
                Time = i['Total Flight Time']
                Night = 0
                #FSP GIVES END TIME FOR SOME REASON
                DayLandings = 1
                NightLandings = 0
                if DateTime > s['dusk']:
                    Night = Time
                    DayLandings = 0
                    NightLandings = 1
                Landings = DayLandings + NightLandings
                Person = ' '.join(i['Customer 1 Name'].split()[:2]) + ';Student;'
                good.writerow({'Date': DateTime.date(), 'AircraftID': AircraftID, 'From': 'KSFZ', 'To': 'KSFZ', 'Route': Route, 'TotalTime': Time, 'PIC': Time, 'Night':Night, 'DayTakeoffs': DayLandings, 'DayLandingsFullStop': DayLandings, 'NightTakeoffs': NightLandings, 'NightLandingsFullStop': NightLandings, 'AllLandings': Landings, 'DualGiven': Time, 'Person1': Person})
