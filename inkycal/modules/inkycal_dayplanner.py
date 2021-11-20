#!/usr/bin/python3
# -*- coding: utf-8 -*-
# noinspection SpellCheckingInspection
"""
Third party module template (inkycal-compatible module)

Copyright by aceisace
"""

#############################################################################
#                           Required imports (do not remove)
#############################################################################
# Required for setting up this module
import math

from inkycal.modules.ical_parser import iCalendar
from inkycal.modules.template import inkycal_module
from inkycal.custom import *
import images.merger
import json
import arrow

#############################################################################
#                           Built-in library imports (change as desired)
#############################################################################

# Built-in libraries go here
from random import shuffle

#############################################################################
#                         External library imports (always use try-except)
#############################################################################

# For external libraries, which require installing,
# use try...except ImportError to check if it has been installed
# If it is not found, print a short message on how to install this dependency
try:
    import feedparser
except ImportError:
    print('feedparser is not installed! Please install with:')
    print('pip3 install feedparser')

#############################################################################
#                         Filename + logging (do not remove)
#############################################################################

# Get the name of this file, set up logging for this filename
filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)


#############################################################################
#                         Class setup
#############################################################################

# Change 'Simple' to a different name, the first letter must be a Capital!
# Avoid naming the class with too long names


class DayPlanner(inkycal_module):
    """ DayPlanner Class
This is a custom single-day iCal calendar display.
  """

    # name is the name that will be shown on the web-ui
    # may be same or different to the class name (Do not remove this)
    name = "Day Planner"

    # create a dictionary containing variables which your module must have
    # to run correctly, e.g. if your module needs an 'api-key' and a 'name':
    requires = {
        "ical_url": {
            "label": "iCalendar URL",
        }

    }
    # The format for the above is: |"key_name": {"Description what this means"},|

    # create a dictionary containing variables which your module optionally
    # can have to run correctly, e.g. if your module needs has optional
    # parameters like: 'api-key' and a 'name':

    #########################################################################
    optional = {

    }

    ########################################################################

    # Initialise the class (do not remove)
    def __init__(self, config):
        """Initialize your module module"""

        # Initialise this module via the inkycal_module template (required)
        super().__init__(config)

        config = config['config']

        # Check if all required parameters are present
        # remove this if your module has no required parameters
        for param in self.requires:
            if param not in config:
                raise Exception('config is missing {}'.format(param))

        # the web-UI removes any blank space from the input
        # It can only output strings or booleans, integers and lists need to be
        # converted manually, e.g.

        # module specific parameters
        self.date_format = config['date_format']
        self.time_format = config['time_format']
        self.language = config['language']
        self.ical_url = config['ical_url']

        # Check if ical_files is an empty string
        if config['ical_url'] and isinstance(config['ical_url'], str):
            self.ical_urls = config['ical_url'].split(',')
        else:
            self.ical_url = config['ical_url']

        # Check if ical_files is an empty string
        if config['ical_files'] and isinstance(config['ical_files'], str):
            self.ical_files = config['ical_files'].split(',')
        else:
            self.ical_files = config['ical_files']

        # Additional config
        self.timezone = get_system_tz()

        self.day_start_hour = 11  # inclusive
        self.day_end_hour = 21  # exclusive

        self.ical = iCalendar()

        # give an OK message
        print(f'{filename} loaded')

        datetime_day_start_hour = arrow.now(self.timezone).floor("day").replace(hour=self.day_start_hour)
        datetime_day_end_hour = arrow.now(self.timezone).floor("day").replace(hour=self.day_end_hour)

        self.ical.load_url(self.ical_url)


    def generate_image(self):
        """Generate image for this module"""

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height
        logger.info('image size: {} x {} px'.format(im_width, im_height))

        # Use logger.info(), logger.debug(), logger.warning() to display
        # useful information for the developer
        logger.info('image size: {} x {} px'.format(im_width, im_height))

        # Create an image for black pixels and one for coloured pixels (required)
        im_black = Image.new('RGB', size=im_size, color='white')
        im_colour = Image.new('RGB', size=im_size, color='white')

        #################################################################

        #                    Your code goes here                        #

        # Write/Draw something on the image

        #   You can use these custom functions to help you create the image:
        # - write()               -> write text on the image
        # - get_fonts()           -> see which fonts are available
        # - get_system_tz()       -> Get the system's current timezone
        # - auto_fontsize()       -> Scale the fontsize to the provided height
        # - textwrap()            -> Split a paragraph into smaller lines
        # - internet_available()  -> Check if internet is available
        # - draw_border()         -> Draw a border around the specified area

        # If these aren't enough, take a look at python Pillow (imaging library)'s
        # documentation.

        #################################################################

        events = self.ical.get_events(arrow.now(self.timezone).floor("day").to("UTC"), arrow.now(self.timezone).ceil(
            "day").to("UTC"), self.timezone)
        events = self.flatten_events(self, events)

        # for _ in events:
        #   print(_["begin"].format('h:mm a ZZZ'), _["end"].format('h:mm a ZZZ'), _["title"])

        # Dateline
        dateline_font = ImageFont.truetype(fonts["NotoSansUI-Bold"], 48)
        today = str(arrow.now(self.timezone).floor("day").format("dddd, MMM DD"))
        line_under_dateline = ImageDraw.Draw(im_black)
        line_under_dateline.line(((0, 90), (im_width, 90)), fill="black", width=10)
        write(im_black, (0, 0), (im_width, 85), today, font=dateline_font, autofit=False, alignment="center")

        # Current time
        time_font = dateline_font = ImageFont.truetype(fonts["NotoSansUI-Regular"], 38)
        now = str(arrow.now(self.timezone).floor("minute").format("hh:mm a"))
        write(im_black, (0, 80), (im_width, 80), now, font=dateline_font, autofit=False, alignment="center")
        line_under_time = ImageDraw.Draw(im_black)
        line_under_time.line(((0, 150), (im_width, 150)), fill="black", width=5)

        # weather placeholder
        weather_font = ImageFont.truetype(fonts["NotoSansUI-Regular"], 25)
        line_under_weather = ImageDraw.Draw(im_black)
        line_under_weather.line(((0, 250), (im_width, 250)), fill="black", width=10)
        write(im_black, (0, 132), (im_width, 132), "Weather will go here", font=weather_font, autofit=False,
              alignment="center")

        # status and all day events placeholder
        all_day_events = []
        busy_all_day_events = []
        first_all_day_event: str = ""
        first_blocking_all_day_event: str = ""
        message: str = "Not in a meeting"
        for _ in reversed(events):
            # print(arrow.now(self.timezone).format("h:mm a"), _["begin"].format("h:mm a"), _["end"].format("h:mm a"),
            #   arrow.now(self.timezone).is_between(_["begin"], _["end"]))
            if arrow.now(self.timezone).is_between(_["begin"], _["end"], "[)"):
                if iCalendar.all_day(_):
                    print("is all day")
                    all_day_events.append(_)
                    first_all_day_event = _["title"]
                    if _["freebusy"] == "busy":
                        busy_all_day_events.append(_)
                        first_blocking_all_day_event = _["title"]
                        message = "Entire day is blocked off"
                        bg_colour = "red"
                        text_colour = "white"
                        im_to_use = im_colour
                        font_size = 25

                else:
                    message = "In a meeting until " + _["end"].format("h:mm a")
                    font_size = 25
                    bg_colour = "red"
                    text_colour = "white"
                    im_to_use = im_colour

            else:
                if self.next_event(self, events) is not None:
                    message = "Free until " + self.next_event(self, events)["begin"].format("h:mm a")
                    font_size = 14
                    bg_colour = "white"
                    text_colour = "black"
                    im_to_use = im_black

                else:
                    message = "Free for the rest of the day"
                    font_size = 14
                    bg_colour = "white"
                    text_colour = "black"
                    im_to_use = im_black

        # status_message
        status_font = ImageFont.truetype(fonts["NotoSansUI-Regular"], font_size)
        line_under_status = ImageDraw.Draw(im_colour)
        line_under_status.line(((0, 270), (im_width, 270)), fill=bg_colour, width=30)
        write(im_to_use, (0, 180), (im_width, 175), message, colour=text_colour, font=status_font,
              autofit=False,
              alignment="center")

        event_message: str = ''
        # all_day_event summary
        num_events = len(all_day_events)
        num_busy_events = len(busy_all_day_events)
        if num_events > 0:
            if num_busy_events > 1:
                event_message = "The day is blocked off for\"" + first_blocking_all_day_event + "\"."
            else:
                if (num_events == 1):
                    event_message = "All day: " + first_all_day_event
                else:
                    event_message = "There are " + str(num_events) + " all-day events today (" + str(
                        num_busy_events) + " blocking)."

        all_day_font = ImageFont.truetype(fonts["NotoSansUI-Bold"], 12)
        write(im_colour, (0, 280), (im_width, 50), event_message, colour="black", font=all_day_font,
              autofit=False,
              alignment="center")

        # grid
        working_hours: int = int(self.day_end_hour) - int(self.day_start_hour)
        minor_tick_thickness: int = 1
        major_tick_thickness: int = 3
        tick_distance: int = 12

        initial_y: int = 320
        y_cursor: int = initial_y
        margin: int = 80
        # print("working hours: " + str(working_hours))

        hour_font = ImageFont.truetype(fonts["NotoSansUI-Bold"], 12)
        datetime_day_start_hour = arrow.now(self.timezone).floor("day").replace(hour=self.day_start_hour)
        datetime_day_end_hour = arrow.now(self.timezone).floor("day").replace(hour=self.day_end_hour)
        working_minutes = (len([*arrow.Arrow.span_range('hour', datetime_day_start_hour,
                                                        datetime_day_end_hour)]) - 1) * 60
        elapsed_minutes = (
            len([*arrow.Arrow.span_range('minute', datetime_day_start_hour, arrow.now(self.timezone).floor("minute"))]))
        total_grid_height = working_hours * 4 * tick_distance

        if arrow.now(self.timezone).is_between(datetime_day_start_hour, datetime_day_end_hour, '[)'):
            caret_font = ImageFont.truetype(fonts["NotoSansUI-Bold"], 25)
            now_line_pos = int(math.floor(((elapsed_minutes / working_minutes) * total_grid_height + initial_y)))
            # print(str((elapsed_minutes / working_minutes) * total_grid_height), now_line_pos)
            now_line = ImageDraw.Draw(im_colour)
            now_line.line(((margin, now_line_pos), (im_width - margin, now_line_pos)), fill="red",
                          width=major_tick_thickness)
            write(im_colour, (im_width - margin - 5, now_line_pos - 27), (50, 50), "◄", colour="red", font=caret_font,
                  autofit=False, alignment="left")

        for x in range(working_hours * 4):
            # print(datetime_day_start_hour)
            # print(datetime_day_end_hour)
            # times = [*range(self.day_start_hour, self.day_end_hour, 1)]
            times = [*arrow.Arrow.span_range('hour', datetime_day_start_hour, datetime_day_end_hour)]

            if (x % 4 == 0):
                write(im_black, (margin - 60, y_cursor - 15), (55, 30), arrow.get(str(times[x // 4][1])).format("h a"),
                      font=hour_font, autofit=False, alignment="right")
                gridline = ImageDraw.Draw(im_black)
                gridline.line(((margin, y_cursor), (im_width - margin, y_cursor)), fill="black",
                              width=major_tick_thickness)
                y_cursor += tick_distance
                # print("y_cursor=" + str(y_cursor))
            else:
                gridline = ImageDraw.Draw(im_black)
                gridline.line(((margin, y_cursor), (im_width - margin, y_cursor)), fill="black",
                              width=minor_tick_thickness)
                y_cursor += tick_distance
                # print("y_cursor=" + str(y_cursor))
        final_y = y_cursor

        for _ in reversed(events):
            # print (arrow.get(_['begin']), arrow.now().floor("day"))
            # print(arrow.get(_['end']), arrow.now().shift(days=+1).floor("day"))
            if arrow.get(_['begin']) == arrow.now(self.timezone).floor("day") and arrow.get(_['end']) == arrow.now(
                    self.timezone).shift(days=+1).floor("day"):
                pass
                # print(_["title"] + " is all-day... skipping")
            else:
                total_grid_height = final_y - initial_y
                minutes_to_start: int = len(
                    [*arrow.Arrow.span_range('minutes', datetime_day_start_hour, _['begin'])])

                event_length_minutes: int = len([*arrow.Arrow.span_range('minutes', _['begin'], _['end'])]) - 1

                y_position: int = max(int(
                    math.floor(((minutes_to_start / working_minutes) * total_grid_height))) + initial_y, initial_y)

                event_height: int = int(math.floor((event_length_minutes / working_minutes) * total_grid_height))

                if _['begin'] < datetime_day_start_hour:
                    minutes_before_start = len([*arrow.Arrow.span_range('minutes', _['begin'],
                                                                        datetime_day_start_hour)])
                    event_height = event_height - int(math.floor(((
                                                                          minutes_before_start / working_minutes) *
                                                                  total_grid_height)))

                if event_height + y_position - initial_y > total_grid_height:
                    event_height = total_grid_height - y_position + initial_y

                label: str = _["begin"].format("h:mm a") + " -  " + _["end"].format("h:mm a")

                event_font = ImageFont.truetype(fonts["NotoSansUI-Bold"], 10)
                tiny_event_font = ImageFont.truetype(fonts["NotoSansUI-Bold"], 7)

                if event_length_minutes < 15:
                    write(im_black, (margin, y_position - 10),
                          ((im_width - (2 * margin) + 1), max(event_height, tick_distance)),
                          label + " ", colour="black", autofit=True,
                          font=tiny_event_font, alignment="right")
                    write(im_black, (margin, y_position),
                          ((im_width - (2 * margin) + 2), max(event_height, math.floor(tick_distance * 0.5))),
                          " ", colour="white", fill_colour='black', autofit=True, font=tiny_event_font,
                          alignment="right")
                else:
                    write(im_black, (margin, y_position), ((im_width - (2 * margin) + 2), max(event_height, 2)), " ",
                          colour="white", fill_colour='black', font=event_font, alignment="right")
                    write(im_black, (margin, y_position), ((im_width - (2 * margin) + 2), tick_distance + 4),
                          label + " ", autofit=True,
                          colour="white", fill_colour='black', font=tiny_event_font, alignment="right")
        # return the images ready for the display
        return im_black, im_colour

    @staticmethod
    def sort_by_start_time(event):
        return event["begin"]

    @staticmethod
    def next_event(self, events: list):
        events.sort(reverse=False, key=self.sort_by_start_time)
        for _ in events:
            if _["begin"] > arrow.now(self.timezone):
                return _
        return None

    @staticmethod
    def flatten_events(self, events):
        # order events chronologically
        events.sort(reverse=False, key=self.sort_by_start_time)
        # for each event
        x = 0
        while True:
            # if there's no event after, stop and return
            if x >= len(events) - 1:
                break
            else:
                # check to see if it's an all-day event
                if iCalendar.all_day(events[x]):
                    # if it is, let it be
                    x += 1
                else:
                    # check to see if the next event starts before this one does
                    if events[x + 1]["begin"] > events[x]["end"]:
                        # if it doesn't, leave it; they don't overlap
                        x += 1
                    else:
                        # otherwise, combine the events
                        events[x]["end"] = max(events[x + 1]["end"], events[x]["end"])
                        events[x]["title"] = events[x]["title"] + ", " + events[x + 1]["title"]
                        # remove the second event
                        events = events[:x + 1] + events[x + 2:]
                        # call self with the new event list
                        events = self.flatten_events(self, events)
        # return list of events
        return events


if __name__ == '__main__':
    print(f'running {filename} in standalone mode')
    with open('/Users/dcostoy/PycharmProjects/Inkycal/settings.json') as settings_file:
        settings = json.load(settings_file)
        img, color = DayPlanner(settings["modules"][0]).generate_image()
        img.save(f"moduledayplanner_black.png", "PNG")
        color.save(f"moduledayplanner_color.png", "PNG")
        merged = images.merger.merge("moduledayplanner_black.png", "moduledayplanner_color.png",
                                     "moduledayplanner_merged")

################################################################################
# Last steps
# Wow, you made your own module for the inkycal project! Amazing :D
# To make sure this module can be used with inkycal, you need to edit 2 files:

# 1) Inkycal/inkycal/modules/__init__.py
# Add this into the modules init file:
# from .filename import Class
# where filename is the name of your module
# where Class is the name of your class e.g. Simple in this case


# 2) Inkycal/inkycal/__init__.py
# Before the line # Main file, add this:
# import inkycal.modules.filename
# Where the filename is the name of your file inside the modules folder

# How do I now import my module?
# from inkycal.modules import Class
# Where Class is the name of the class inside your module (e.g. Simple)
