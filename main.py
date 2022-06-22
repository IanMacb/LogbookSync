#Write header
file = open("Practice_table.csv", 'w')
file.write("ForeFlight Logbook Import"+'\n\n'+"Flights Table"+'\n')
file.write("Date,AircraftID,From,To,Route,TotalTime,PIC,SIC,Night,Solo,CrossCountry,Distance,DayTakeoffs,"
           "DayLandingsFullStop,NightTakeoffs,NightLandingsFullStop,AllLandings,DualGiven,DualReceived,"
           "SimulatedFlight,Person1"+'\n')

file.close()
file = open("Practice_table.csv", 'r')
print(file.read())
file.close()

file = open("Table_2163.csv", 'r')
print(file.readline())