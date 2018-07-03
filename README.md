# pylaunchcal
Create an ics calendar file for future space flight launches.

The scripts parses the [launch schedule of spaceflightnow](https://spaceflightnow.com/launch-schedule/) and creates an iCalendar file that can be imported into any common calendar application.

Note that only launches are considered that already have a specific date (month and day) set. Launches where the exact launch time is still TBD are displayed as all-day events. Launches that have a launch window are displayed at the beginning of the launch window.  

# Installation
Use `pip install beatifulsoup4 ics` to install all necessary packages. Then just clone this repository. 

# Usage
Run the script with `python3 launch_calendar.py -o PATH_TO_OUTPUT_FILE`. Set up a cron job to run the script automatically. 

# Subscription
You can subscribe to a daily updated webcal [here](https://momadoki.uber.space/launches/launches.ics). 

# TODO
- Docstrings
- Write a `setup.py`
- Display correct end of launch windows
