import pymupdf
import csv
import easygui
import sys
import configparser
import datetime
from pathlib import Path

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

class DataMonth:
    def __init__(self, year_month, data):
        self.year = int(year_month.split("/")[0])
        self.month = int(year_month.split("/")[1])
        self.data = data
        self.date = datetime.date(self.year, self.month, 1)

    def __str__(self):
        #TODO fix
        return f"{self.year}/{self.month}"


class LogbookUpdater:
    def __init__(self):
        self.data = []

        # determines OS and configures the path to the users downloads folder
        self.os = sys.platform
        self.path = Path(__file__).absolute()
        if 'linux' in self.os:
            self.downloads_path = str(self.path.parents[2]) + '/Downloads/'
        elif 'win' in self.os:
            self.downloads_path = str(self.path.parents[2]) + '\\Downloads\\'
        elif 'Mac' in self.os:
            #TODO
            print("get fukt")

        # opens the file select GUI window and grabs all the text off the file
        self.file_names = easygui.fileopenbox(default=self.downloads_path, multiple=True)

        # loads config file to 'options' object
        self.options = configparser.ConfigParser(allow_unnamed_section=True)
        self.options.read_file(open(f"{self.path.parents[0]}/options.cfg"))

    #for each file, open, get text, parse, organize

    def parse_text(self, text):
        """
        strips useless stuff and organizes text from PDF
        :param text: STR all the text converted from the PDF file
        :return: STR year_month month and year in yyyy/mm
            DICT data_dict organized data ready to be formatted to foreflight
        """

        # removes the header and column titles
        header, _, text = text.partition("T\nL\nT\nL\n")
        header = header.split("\n")
        text = text.split("\n")

        # reads the month and year from the report
        year_month = header[0]
        year_month = year_month.split(" ")
        year_month[0] = MONTHS[year_month[0]]
        year_month = f"{year_month[1]}/{year_month[0]}"

        # filters through lines to only keep days with flight time (looks for part 91/135 label)
        data = []
        for i, line_text in enumerate(text):
            if "135" in line_text or "91" in line_text:
                data.append(text[i - 17:i])

        # loops through filtered flight days to clean up tabs
        for i, line_text in enumerate(data):
            date = line_text[0].split("\xa0")
            date = date[-1]
            data[i][0] = date

            tail = line_text[1].split("\xa0")
            tail = tail[-1]
            data[i][1] = tail

            # processes remarks column to start, end, and route. prefixes with 'K' if necessary
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

        # organizes data into usable dict
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

    def process_files(self):
        for file_name in self.file_names:
            doc = pymupdf.open(f"{file_name}")
            text = doc.get_page_text(0)
            year_month, data_dict = self.parse_text(text)
            log_month = DataMonth(year_month, data_dict)
            self.data.append(log_month)
            self.data.sort(key=lambda x: x.date)

    def format_FF_file(self):
        # writes file header and column titles
        with open(f"{self.downloads_path}FF_logbook_updater.csv", 'w+', newline='') as file:
            length = len(HEADERS)
            writer = csv.writer(file)
            writer.writerow(['ForeFlight Logbook Import'] + [''] * (length - 1))
            writer.writerow([''] * length)
            writer.writerow(['Flights Table'] + [''] * (length - 1))
            writer = csv.DictWriter(file, fieldnames=HEADERS)
            writer.writeheader()

            for log_month in self.data:
                # add each new line
                for flight_day in log_month.data:

                    # Date
                    Date = f"{log_month.year}/{log_month.month}/{flight_day["Date"]}"

                    # Tail
                    AircraftID = flight_day["AircraftID"]

                    # Airport start and end
                    start = flight_day["start"]
                    end = flight_day["end"]

                    # Route
                    route = ""
                    for i in flight_day["route"]:
                        route = f"{route} {i}"
                    route = route.strip(" ")

                    # total time
                    total_time = flight_day["total_time"]

                    # PIC or SIC time
                    PIC_time = total_time
                    SIC_time = 0.0
                    if not self.options.getboolean(configparser.UNNAMED_SECTION, "PIC"):
                        SIC_time = total_time
                        PIC_time = 0.0

                    # night time
                    night_time = flight_day["night_time"]

                    # cross country time
                    cross_country_time = total_time

                    # landings
                    day_takeoffs = flight_day["day_takeoffs"]
                    day_landings = flight_day["day_landings"]
                    night_takeoffs = flight_day["night_takeoffs"]
                    night_landings = flight_day["night_landings"]
                    all_landings = day_landings + night_landings

                    # IFR time
                    IFR_time = flight_day["IFR_time"]

                    # put it all in a new line on the CSV
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
        file.close()


def main():
    updater = LogbookUpdater()
    updater.process_files()
    updater.format_FF_file()


if __name__ == "__main__":
    main()
