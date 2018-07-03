import urllib
import datetime
from bs4 import BeautifulSoup
from ics import Calendar, Event

WEBSITE = "https://spaceflightnow.com/launch-schedule/"
MONTHES = {"Jan": 1, "Feb": 2, "March": 3, "April": 4, "May": 5, "June": 6,
           "July": 7, "Aug": 8, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12}

CURRENT_YEAR = datetime.datetime.today().year
CURRENT_MONTH = datetime.datetime.today().month


def get_year(datename):
    year = CURRENT_YEAR
    month = get_month(datename)
    if not month:
        return None
    if month < CURRENT_MONTH:
        year += 1

    return year

def get_month(datename):
    date = datename.find('span', attrs={'class': 'launchdate'}).text
    for possible_month in MONTHES:
        if possible_month in date:
            return MONTHES[possible_month]

    #print(date, "has no valid month")
    return None

def get_day(datename, missiondata):
    date = datename.find('span', attrs={'class': 'launchdate'}).text
    day = "".join([letter for letter in date if (letter.isdigit() or letter == "/")])
    if not day:
        return None

    # Now we get the time of the launch
    timetype, _ = missiondata.findAll("span")
    launchtime = timetype.next_sibling

    # If the launch is on different days in different time zones find the day that is on GMT
    if "/" in day:
        day = launchtime.split("GMT on")[1].split("(")[0]
        day = "".join([l for l in day if l.isdigit()])

    day = int(day)
    if day > 31:
        return None

    return day

def get_mission(datename):
    mission = datename.find('span', attrs={'class': 'mission'})
    mission = mission.text.replace(" • ", ": ")
    return mission

def get_location(missiondata):
    _, location = missiondata.findAll("span")
    location = location.next_sibling
    while location[0] == " ":
        location = location[1::]
    return location

def get_launchtime(missiondata):
    # If the time is not yet set, make the event all day
    timetype, _ = missiondata.findAll("span")
    launchtime = timetype.next_sibling

    if "TBD" in launchtime or "GMT" not in launchtime:
        #print(launchtime, "is not a valid time stamp")
        return 0, 0, 0, True

    launchtime = launchtime.split("GMT")[0].replace(" ", "").replace(":", "")

    launchstart = launchtime.split("-")[0]

    if len(launchstart) == 4:
        launchstart += "00"
    if not launchstart.isdigit():
        #print(launchstart, "is not a valid time stamp")
        return 0, 0, 0, True

    assert len(launchstart) == 6

    hour = launchstart[0:2]
    minute = launchstart[2:4]
    second = launchstart[4:6]

    return int(hour), int(minute), int(second), False

def make_ics_timestamp(year, month, day, hour, minute):
    timestamp = str(year)
    timestamp += str(month).zfill(2)
    timestamp += str(day).zfill(2)
    timestamp += "T"
    timestamp += str(hour).zfill(2)
    #timestamp += ":"
    timestamp += str(minute).zfill(2)
    #timestamp += ":"
    #timestamp += str(second).zfill(2)
    return timestamp

def parse_website():
    page = urllib.request.urlopen(WEBSITE)
    soup = BeautifulSoup(page, 'html5lib')


    datename = soup.findAll('div', attrs={'class': 'datename'})
    missiondata = soup.findAll('div', attrs={'class': 'missiondata'})
    missisondescription = soup.findAll('div', attrs={'class': 'missdescrip'})

    return datename, missiondata, missisondescription

def get_full_launchtime(datename, missiondata):
    year = get_year(datename)
    month = get_month(datename)
    day = get_day(datename, missiondata)
    hour, minute, _, is_all_day = get_launchtime(missiondata)

    if not None in [year, month, day]:
        begin = make_ics_timestamp(year, month, day, hour, minute)
    else:
        begin = None

    return begin, is_all_day

def main():
    calendar = Calendar()
    datenames, missiondatas, descriptions = parse_website()

    for datename, data, desc in zip(datenames, missiondatas, descriptions):
        mission = get_mission(datename)
        location = get_location(data)
        begin, is_all_day = get_full_launchtime(datename, data)

        if begin and not is_all_day:
            event = Event()
            event.begin = begin
            event.description = desc.text
            event.name = mission
            if is_all_day:
                event.make_all_day()
            event.location = location
            event.uid = mission.replace(" ", "")

            calendar.events.add(event)

    with open("launches.ics", "w") as outfile:
        outfile.writelines(calendar)

    print(calendar.events)

if __name__ == "__main__":
    main()
