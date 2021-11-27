#!/usr/bin/python3
# -*- coding: utf-8 -*-
# noinspection SpellCheckingInspection
"""
Dayplanner module (inkycal-compatible module)

Copyright by dcostoy
"""

#############################################################################
#                           Required imports
#############################################################################

from inkycal.modules.ical_parser import iCalendar
from inkycal.modules.template import inkycal_module
from inkycal.custom import *
import arrow
import json


# Get the name of this file, set up logging for this filename
filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)

#############################################################################
#                         DayPlanner Class
#############################################################################


class DayPlanner(inkycal_module):
    """ This is a custom single-day iCal calendar free-busy display."""

    # name is the name that will be shown on the web-ui
    # may be same or different to the class name (Do not remove this)
    name = "Day Planner"

    # create a dictionary containing variables which your module must have
    # to run correctly, e.g. if your module needs an 'api-key' and a 'name':
    requires = {
        "ical_urls": {
            "label": "iCalendar URLs, separated by commas",
        }

    }
    # The format for the above is: |"key_name": {"Description what this means"},|

    # create a dictionary containing variables which your module optionally
    # can have to run correctly, e.g. if your module needs has optional
    # parameters like: 'api-key' and a 'name':
    optional = {
        # "time_format": {
        #     "label": "ISO date format string (if not set, defaults to \'h:mm a\') "
        # }
    }

    # Initialise the class (do not remove)

    def __init__(self, config):
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

        self.language = config['language']
        self.ical_urls = config['ical_urls']

        # Check if ical_files is an empty string
        if config['ical_urls'] and isinstance(config['ical_urls'], str):
            self.ical_urls = config['ical_urls'].split(',')
        else:
            self.ical_urls = config['ical_urls']

        # Check if ical_files is an empty string
        if config['ical_files'] and isinstance(config['ical_files'], str):
            self.ical_files = config['ical_files'].split(',')
        else:
            self.ical_files = config['ical_files']

        # Additional config
        self.timezone = get_system_tz() # e.g., self.timezone = "Pacific/Honolulu"

        self.day_start_hour = 8  # inclusive
        self.day_end_hour = 19  # exclusive
        self.datetime_day_start_hour = arrow.now(self.timezone).floor("day").replace(hour=self.day_start_hour)
        self.datetime_day_end_hour = arrow.now(self.timezone).floor("day").replace(hour=self.day_end_hour)

        # give an OK message
        print(f'{filename} loaded')

    def generate_image(self):
        from inkycal.modules.daygrid import DayGrid
        """Generate image for this module"""

        # once per refresh is sufficient
        now: arrow.Arrow.arrow = arrow.now(self.timezone)

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height
        margin = 80

        logger.info('image size: {} x {} px'.format(im_width, im_height))

        # Create an image for black pixels and one for coloured pixels (required)
        im_black = Image.new('RGB', size=im_size, color='white')
        im_colour = Image.new('RGB', size=im_size, color='white')

        # Gets all events from midnight today local time to midnight tomorrow local time. (Have to use UTC tz, not local
        # tz with UTC offset.)



        self.ical = iCalendar()

        # Load icalendar from config
        parser = self.ical

        if self.ical_urls:
            parser.load_url(self.ical_urls)

        if self.ical_files:
            parser.load_from_file(self.ical_files)

        # Load events from all icalendar in timerange

        # empty out this array to be safe then repopulate
        events = []
        events = parser.get_events(now.floor("day").to("UTC"), now.ceil("day").to("UTC"), self.timezone)

        # combine adjacent and intersecting events into single blocks of busy time
        events = self._flatten_events(events)

        # status and all-day events placeholder
        self.get_status_banner(im_black=im_black, im_colour=im_colour, events=events, now=now)

        # for _ in events:
        #     print ('* ' + _['title'] + ": " + _["begin"].format("h:mm a") + " - " + _["end"].format("h:mm a"))


        # set the message for all-day events
        allday_message_position = (0, 40)
        self.get_allday_message(im_black, events, margin, allday_message_position)

        self.get_status_banner(im_black, im_colour, events, now)

        # grid
        grid = DayGrid(self, im_black=im_black, im_colour=im_colour, minor_tick_thickness=1, major_tick_thickness=3,
                       tick_distance=9, initial_y=120, margin=margin)
        grid.draw_caret(self, im_colour)
        grid.draw_events(self,im_black, events)

        # draw_border(im_black, xy=(0-24, 0-34), size=((self.width+46), (im_black.height-20)))
        # return the images ready for the display
        return im_black, im_colour

    @staticmethod
    def get_next_event(events: list, now: arrow.Arrow):
        def _sort_by_start_time(event):
            return event["begin"]

        events.sort(reverse=False, key=_sort_by_start_time)
        for _ in events:
            if _["begin"] > now:
                return _
        return None

    @staticmethod
    def get_first_current_event(events: list, now: arrow.Arrow, exclude_all_day=False):
        for _ in events:
            if _["begin"] <= now <= _["end"]:
                if (excludeAllDay and not iCalendar.all_day(_)) or (not exclude_all_day):
                    return  _

    @staticmethod
    def get_allday_events(events, blocking_only=False):
        all_day_events = []
        for _ in events:
            if iCalendar.all_day(_):
                if blocking_only is False:
                    all_day_events.append(_)
                else:
                    if blocking_only is True and _["freebusy"] == "busy":
                        all_day_events.append(_)
        return all_day_events

    @staticmethod
    def get_status_now(events, now: arrow.Arrow):
        for _ in events:
            if now.is_between(_["begin"], _["end"]) and not iCalendar.all_day(_):
                return "busy"
            if iCalendar.all_day(_) and _["freebusy"] == "busy":
                return "busy"
        return "free"

    def get_status_banner(self, im_black: Image.Image, im_colour: Image.Image, events: list, now: arrow.Arrow):
        if self.get_status_now(events, now) == "busy":
            current_event = self.get_first_current_event(events, now, exclude_all_day=True)
            current_event_is_all_day = iCalendar.all_day(current_event)
            if current_event_is_all_day:
                if current_event["freebusy"] == "busy":
                    write(
                        im_colour,
                        (0, 0),
                        (self.width, 40),
                        text="In a meeting all day",
                        font=ImageFont.truetype(fonts["NotoSansUI-Bold"], 25),
                        colour="white",
                        fill_colour="black"
                    )
            else:
                write(
                    im_colour,
                    (0, 0),
                    (self.width, 40),
                    text="In meetings until " + self.get_first_current_event(events, now, excludeAllDay=True)["end"]
                        .format('h:mm a'),
                    font=ImageFont.truetype(fonts["NotoSansUI-Bold"], 25),
                    colour="white",
                    fill_colour="black"
                )
        else:
            write(
                im_black,
                (0, 0),
                (self.width, 40),
                text=("Free until " + self.get_next_event(events, now)["begin"].format('h:mm a')) if
                self.get_next_event(events, now) else "Free for the rest of the day",
                font=ImageFont.truetype(fonts["NotoSansUI-Bold"], 25),
                colour="white",
                fill_colour="black"
            )

    def get_allday_message(self, im: Image.Image, events, margin, pos):
        all_day_events: list = []
        blocking_all_day_events: list = []
        num_all_day_events = 0
        num_blocking_all_day_events = 0
        all_day_events = self.get_allday_events(events)
        blocking_all_day_events = self.get_allday_events(events, blocking_only=True)
        all_day_event_message = ''
        num_all_day_events = len(all_day_events)
        num_blocking_all_day_events = len(blocking_all_day_events)

        if num_blocking_all_day_events > 0:
            all_day_event_message = str(num_all_day_events) + " all-day events (" + \
                                    str(num_blocking_all_day_events) + " blocking)"
        if num_blocking_all_day_events == 0 and num_all_day_events > 0:
            if num_all_day_events == 1:
                all_day_event_message = "All day: " + all_day_events[0]['title']
            else:
                all_day_event_message = str(num_all_day_events) + " all-day events"

        all_day_font = ImageFont.truetype(fonts["NotoSansUI-Bold"], 25)

        write(im, pos, (self.width, 52), all_day_event_message, colour="black",
              fill_colour=None, font=all_day_font,
              alignment="center")

    def _flatten_events(self, events):
        # order events chronologically
        def _sort_by_start_time(event):
            return event["begin"]
        events.sort(reverse=False, key=_sort_by_start_time)
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
                        events = self._flatten_events(events)
        # return list of events
        return events

if __name__ == '__main__':
    from images.merger import merge
    print(f'running {filename} in standalone mode')
    with open('/Users/dcostoy/PycharmProjects/Inkycal/settings.json') as settings_file:
        settings = json.load(settings_file)
        img, color = DayPlanner(settings["modules"][1]).generate_image()
        img.save(f"module_dayplanner_black.png", "PNG")
        color.save(f"module_dayplanner_color.png", "PNG")
        merged = merge("module_dayplanner_black.png", "module_dayplanner_color.png",
                                     "module_dayplanner_merged")
