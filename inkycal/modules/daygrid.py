from inkycal.modules.ical_parser import iCalendar
from inkycal.modules.template import inkycal_module
from inkycal.custom import *
from inkycal.modules.inkycal_dayplanner import DayPlanner
from inkycal.modules.inkycal_calendar import Calendar
import arrow
import math


class DayGrid:
    def __init__(self, dayplanner: DayPlanner,
                 im_black: Image.Image,
                 im_colour: Image.Image,
                 margin: int = 80,
                 minor_tick_thickness: int = 1,
                 major_tick_thickness: int = 3,
                 tick_distance: int = 12,
                 hour_font: ImageFont = ImageFont.truetype(fonts["NotoSansUI-Bold"], 12),
                 initial_y: int = 0):

        self.margin = margin
        self.width = dayplanner.width - margin
        self.pos = {"y": initial_y, "x": self.width - 2 * self.margin}
        self.minor_tick_thickness = minor_tick_thickness
        self.major_tick_thickness = major_tick_thickness
        self.tick_distance = 12
        self._now = arrow.now(dayplanner.timezone)

        self._datetime_day_start_hour = self._now.floor("day").replace(hour=dayplanner.day_start_hour)
        self._datetime_day_end_hour = self._now.floor("day").replace(hour=dayplanner.day_end_hour)
        self._working_hours: int = int(dayplanner.day_end_hour) - int(dayplanner.day_start_hour)
        self._working_minutes = (len([*arrow.Arrow.span_range('hour', self._datetime_day_start_hour,
                                                              self._datetime_day_end_hour)]) - 1) * 60
        y_cursor: int = initial_y
        for x in range((self._working_hours * 4) + 1):
            times = [*arrow.Arrow.span_range('hour', self._datetime_day_start_hour, self._datetime_day_end_hour)]

            if x % 4 == 0:
                write(im_black, (margin - 60, y_cursor - 15), (55, 30), arrow.get(str(times[x // 4][1])).format(
                    "h a"),
                      font=hour_font, autofit=False, alignment="right")
                gridline = ImageDraw.Draw(im_black)
                gridline.line(((margin, y_cursor), (self.width, y_cursor)), fill="black",
                              width=major_tick_thickness)
                y_cursor += tick_distance
            else:
                gridline = ImageDraw.Draw(im_black)
                gridline.line(((margin, y_cursor), (self.width, y_cursor)), fill="black",
                              width=minor_tick_thickness)
                y_cursor += tick_distance
        self.height = y_cursor - initial_y - tick_distance
        return

    def draw_caret(self, dayplanner, im: Image.Image):

        # calculate the elapsed minutes in the working day until now
        elapsed_minutes: int = (len([*arrow.Arrow.span_range('minute', self._datetime_day_start_hour,
                                                        self._now.floor("minute"))]))

        if self._now.is_between(self._datetime_day_start_hour, self._datetime_day_end_hour, '[)'):
            now_line_pos = int(math.floor(((elapsed_minutes / self._working_minutes) *
                                           self.height + self.pos["y"])))
            ImageDraw.Draw(im).line(((self.margin, now_line_pos),
                                    (self.width, now_line_pos)),
                                    fill="black",
                                    width=self.major_tick_thickness)
            write(im,
                  (self.width - 5, now_line_pos - 27),
                  (50, 50),
                  text="◄",
                  colour="black",
                  font=ImageFont.truetype(fonts["NotoSansUI-Bold"], 25),
                  autofit=False,
                  alignment="left")

    def draw_events(self, dayplanner, im: Image.Image, events):
        for _ in reversed(events):
            if iCalendar.all_day(_):
                pass
            else:
                if (_["begin"] < self._datetime_day_start_hour and _["end"] < self._datetime_day_start_hour) or \
                        (_["begin"] > self._datetime_day_end_hour and _["end"] > self._datetime_day_end_hour):
                    pass
                else:
                    minutes_to_start: int = len([*arrow.Arrow.span_range('minutes',
                                                                         self._datetime_day_start_hour,
                                                                         _['begin'])])
                    event_length_minutes: int = len([*arrow.Arrow.span_range('minutes', _['begin'], _['end'])]) - 1
                    y_position: int = max(int(
                        math.floor(((minutes_to_start / self._working_minutes) * self.height))) + self.pos["y"],
                                          self.pos["y"])
                    event_height: int = int(math.floor((event_length_minutes / self._working_minutes) * self.height))

                    if _['begin'] < self._datetime_day_start_hour:
                        minutes_before_start = len([*arrow.Arrow.span_range('minutes', _['begin'],
                                                                            self._datetime_day_start_hour)])
                        event_height = event_height - int(math.floor(((minutes_before_start / self._working_minutes) *
                                                                      self.height)))
                    if event_height + y_position - self.pos["y"] > self.height:
                        event_height = self.height - y_position + self.pos["y"]

                    label: str = _["begin"].format("h:mm a") + " -  " + _["end"].format("h:mm a")
                    event_font = ImageFont.truetype(fonts["NotoSansUI-Bold"], 12)
                    tiny_event_font = ImageFont.truetype(fonts["NotoSansUI-Bold"], 12)
                    if event_length_minutes < 15:
                        write(im,
                              (self.margin, y_position - 12),
                              ((self.width - self.margin + 1), self.tick_distance),
                              text=label + " ",
                              colour="black",
                              autofit=True,
                              font=tiny_event_font,
                              alignment="right")

                        write(im,
                              (self.margin, y_position),
                              ((self.width - self.margin + 1),
                               max(event_height, math.floor(self.tick_distance * 0.5))),
                              text=" ",
                              colour="white",
                              fill_colour='black',
                              font=event_font,
                              alignment="right")
                    else:
                        write(im,
                              (self.margin, y_position) ,
                              ((self.width - self.margin + 1), max(event_height, 2)),
                              text=" ",
                              colour="white",
                              fill_colour='black',
                              font=event_font,
                              alignment="right")
                        write(im,
                              (self.margin, y_position),
                              ((self.width - self.margin + 1), self.tick_distance + 5),
                              text=label + " ",
                              colour="white",
                              fill_colour="black",
                              font=event_font, alignment="right")


