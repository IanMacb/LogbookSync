import pymupdf
import csv
import easygui
import sys
import configparser

# TODO open and parse multiple files together

HEADERS = ['Date',
           'AircraftID',
           'From',
           'To',
           'Route',
           'TotalTime',
           'PIC',
           'SIC',
           'Night',
           'CrossCountry',
           'Takeoff Day',
           'Landing Full-Stop Day',
           'Takeoff Night',
           'Landing Full-Stop Night',
           'AllLandings',
           'ActualInstrument',
           'Holds',
           'DualGiven',
           'Person1',
           'PilotComments']

MONTHS = {'January': 1,
          'February': 2,
          'March': 3,
          'April': 4,
          'May': 5,
          'June': 6,
          'July': 7,
          'August': 8,
          'September': 9,
          'October': 10,
          'November': 11,
          'December': 12,}


def file_open(file_name="", ask=False):
    """
    Opens a PDF file and processes it using mymupdf
    :param file_name: STR file name to open, default empty
    :param ask: BOOL decision to prompt user via GUI
    :return: STR file content, STR file path
    """
    #determines OS and configures the path to the users downloads folder
    os = sys.platform
    default_path = ""
    splitter = ""
    if 'linux' in os:
        default_path = "/home/ian/Downloads/"
        splitter = "/"
    elif 'Windows' in os:
        default_path = "C:\\Users\\%User%\\Downloads"
        splitter = "\\"
    elif 'Mac' in os:
        #TODO
        print("go fuk yourself")

    #TODO error handling
    #opens the file select GUI window and grabs all the text off the file
    if ask:
        file_name = easygui.fileopenbox(default=default_path)
    file_path = file_name[:-len(file_name.split(f"{splitter}")[-1])]
    doc = pymupdf.open(f"{file_name}")
    text = doc.get_page_text(0)

    return text, file_path


def parse(text):
    """
    strips useless stuff and organizes text from PDF
    :param text: STR all the text converted from the PDF file
    :return: STR year_month month and year in yyyy/mm
        DICT data_dict organized data ready to be formatted to foreflight
    """

    #removes the header and column titles
    header, _, text = text.partition("T\nL\nT\nL\n")
    header = header.split("\n")
    text = text.split("\n")

    #reads the month and year from the report
    year_month = header[0]
    year_month = year_month.split(" ")
    year_month[0] = MONTHS[year_month[0]]
    year_month = f"{year_month[1]}/{year_month[0]}"

    #filters through lines to only keep days with flight time (looks for part 91/135 label)
    data = []
    for i, line_text in enumerate(text):
        if "135" in line_text or "91" in line_text:
            data.append(text[i - 17:i])

    #loops through filtered flight days to cleen up tabs
    for i, line_text in enumerate(data):
        date = line_text[0].split("\xa0")
        date = date[-1]
        data[i][0] = date

        tail = line_text[1].split("\xa0")
        tail = tail[-1]
        data[i][1] = tail

        #processes remarks column to start, end, and route. prefixes with 'K' if necessary
        remarks = line_text[16].split(" - ")
        for j, entry in enumerate(remarks):
            if len(entry) < 4:
                remarks[j] = f"K{entry}"
        start = remarks[0].upper()
        end = remarks[-1].upper()
        route = ""
        if len(remarks) > 2:
            route = remarks[1:-1]
        data[i].append(start)
        data[i].append(end)
        data[i].append(route)

    #organizes data into usable dict
    data_dict = []
    for i, line_text in enumerate(data):
        data_dict.append({"Date": line_text[0],
                          "AircraftID": line_text[1],
                          "start": line_text[17],
                          "end": line_text[18],
                          "route": line_text[19],
                          "total_time": float(line_text[7]),
                          "night_time": float(line_text[8]),
                          "IFR_time": float(line_text[9]),
                          "day_takeoffs": int(line_text[12]),
                          "day_landings": int(line_text[13]),
                          "night_takeoffs": int(line_text[14]),
                          "night_landings": int(line_text[15])
                          })

    return year_month, data_dict


def file_save(data, year_month, file_name='FF_logbook_updater.csv'):
    """
    formats data into a CSV table and saves to file name in same directory as the PDF
    :param data: DICT preprocessed data from PDF
    :param year_month: STR month and year in yyyy/mm
    :param file_name: STR file name, default 'FF_logbook_updater.csv'
    :return:
    """

    #loads config file to 'options' object
    options = configparser.ConfigParser(allow_unnamed_section=True)
    options.read_file(open("options.cfg"))

    with open(file_name, 'w', newline='') as file:
        #writes file header and column titles
        length = len(HEADERS)
        writer = csv.writer(file)
        writer.writerow(['ForeFlight Logbook Import'] + [''] * (length - 1))
        writer.writerow([''] * length)
        writer.writerow(['Flights Table'] + [''] * (length - 1))
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writeheader()

        #add each new line
        for flight_day in data:

            #Date
            Date = f"{year_month}/{flight_day["Date"]}"

            #Tail
            AircraftID = flight_day["AircraftID"]

            #Airport start and end
            start = flight_day["start"]
            end = flight_day["end"]

            #Route
            route = ""
            for i in flight_day["route"]:
                route = f"{route} {i}"
            route = route.strip(" ")

            #total time
            total_time = flight_day["total_time"]

            #PIC or SIC time
            PIC_time = total_time
            SIC_time = 0.0
            if not options.getboolean(configparser.UNNAMED_SECTION, "PIC"):
                SIC_time = total_time
                PIC_time = 0.0

            #night time
            night_time = flight_day["night_time"]

            #cross country tome
            cross_country_time = total_time

            #landings
            day_takeoffs = flight_day["day_takeoffs"]
            day_landings = flight_day["day_landings"]
            night_takeoffs = flight_day["night_takeoffs"]
            night_landings = flight_day["night_landings"]
            all_landings = day_landings + night_landings

            #IFR time
            IFR_time = flight_day["IFR_time"]

            #put it all in a new line on the CSV
            writer.writerow({'Date': Date,
                             'AircraftID': AircraftID,
                             'From': start,
                             'To': end,
                             'Route': route,
                             'TotalTime': total_time,
                             'PIC': PIC_time,
                             'SIC': SIC_time,
                             'Night': night_time,
                             'CrossCountry': cross_country_time,
                             'Takeoff Day': day_takeoffs,
                             'Landing Full-Stop Day': day_landings,
                             'Takeoff Night': night_takeoffs,
                             'Landing Full-Stop Night': night_landings,
                             'AllLandings': all_landings,
                             'ActualInstrument': IFR_time})

        print("Review for accuracy!!!")


def main():
    text, file_path = file_open("", True)
    year_month, data = parse(text)
    file_save(data, year_month, f"{file_path}FF_logbook_updater.csv")

if __name__ == "__main__":
    main()