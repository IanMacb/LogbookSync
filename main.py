import csv
import datetime
import astral
from astral.sun import sun
import easygui


def main():

    HEADERS = ['Date', 'AircraftID', 'From', 'To', 'Route', 'TotalTime', 'PIC', 'Night', 'CrossCountry', 'DayTakeoffs', 'DayLandingsFullStop', 'NightTakeoffs', 'NightLandingsFullStop', 'AllLandings', 'ActualInstrument', 'Holds', 'DualGiven', 'Person1', 'PilotComments']
    LENGTH = len(HEADERS)

    loc = astral.LocationInfo(name='SFZ', timezone='America/New_York', latitude=41.9208, longitude=-71.4914)
    s: sun()

    entry = input('Last logbook entry day: (MM/DD/YY) ')
    START_DATE = datetime.datetime.strptime(entry, '%m/%d/%y').date()
    # START_DATE = datetime.date(2000, 1, 1)

    file = easygui.fileopenbox(default='c:/Users/%User%/Downloads/*.csv')
    filePath = file[:-len(file.split('\\')[-1])]
    with open(file, 'r', newline='') as csvfile:
        data = csv.DictReader(csvfile)
        with open(f'{filePath}Updater.csv', 'w', newline='') as updater:
            writer = csv.writer(updater)
            writer.writerow(['ForeFlight Logbook Import'] + ['']*(LENGTH-1))
            writer.writerow(['']*LENGTH)
            writer.writerow(['Flights Table'] + ['']*(LENGTH-1))
            writer2 = csv.DictWriter(updater, fieldnames=HEADERS)
            writer2.writeheader()
            for i in data:
                DateTime = datetime.datetime.strptime(i['Start'], "%m/%d/%Y %I:%M:%S %p").astimezone(loc.tzinfo)
                s = sun(loc.observer, date=DateTime.date(), tzinfo=loc.timezone)

                if DateTime.date() > START_DATE:
                    AircraftID = i['Aircraft']
                    if AircraftID != "": AircraftID = AircraftID.split()[0]
                    Route = ''
                    Time = round(float(i['Flight Instruction']), 1)

                    DayLandings = 0
                    if i['Activity Type'] == 'Intro Flight':
                        DayLandings = 1
                    NightLandings = 0

                    Delta = datetime.timedelta(hours=float(Time))
                    End = DateTime + Delta
                    Dusk = s['dusk']
                    Night = (End - max(Dusk, DateTime))
                    Night = round(datetime.timedelta.total_seconds(Night)/3600, 1)
                    if Night <= 0:
                        Night = 0
                    else:
                        DayLandings = 0
                        NightLandings = 1

                    Landings = DayLandings + NightLandings
                    Person = i['Customer 1 Name']
                    Person = f'{Person};Student;'
                    writer2.writerow({'Date': DateTime.date(), 'AircraftID': AircraftID, 'From': 'KSFZ', 'To': 'KSFZ', 'Route': Route, 'TotalTime': Time, 'PIC': Time, 'Night': Night, 'DayTakeoffs': DayLandings, 'DayLandingsFullStop': DayLandings, 'NightTakeoffs': NightLandings, 'NightLandingsFullStop': NightLandings, 'AllLandings': Landings, 'DualGiven': Time, 'Person1': Person})

main()
