import csv

START_DATE = "6/4/2022"


with open('Table_5293.csv', 'r', newline='') as csvfile:
    data = csv.DictReader(csvfile)
    with open('Updater.csv', 'w', newline='') as updater:
        updater.writelines('ForeFlight Logbook Import\n\nFlights Table\n')
        good = csv.DictWriter(updater, fieldnames=['Date', 'AircraftID', 'From', 'To', 'Route', 'TotalTime', 'PIC', 'Night', 'CrossCountry','DayTakeoffs', 'DayLandingsFullStop', 'NightTakeoffs', 'NightLandingsFullStop', 'AllLandings', 'DualGiven', 'Person1'])
        good.writeheader()
        for i in data:
            date = i['ï»¿"Flight Date"'].split()[0]
            AircraftID = i['Aircraft']
            if AircraftID != "":
                AircraftID = AircraftID.split()[0]
            if i['Activity Type'] == 'Intro Flight': Route = 'VC401'
            else: Route = ''
            Time = i['Total Flight Instruction']
            Person = ' '.join(i['Customer 1 Name'].split()[:2]) + ';Student;'
            good.writerow({'Date': date, 'AircraftID': AircraftID, 'From': 'KSFZ', 'To': 'KSFZ', 'Route': Route, 'TotalTime': Time, 'PIC': Time, 'DayTakeoffs': 1, 'DayLandingsFullStop': 1, 'AllLandings': 1, 'DualGiven': Time, 'Person1': Person})


