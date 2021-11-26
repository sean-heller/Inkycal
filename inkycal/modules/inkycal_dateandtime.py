from inkycal.modules.ical_parser import iCalendar
from inkycal.modules.template import inkycal_module
from inkycal.custom import *
import arrow
import json
from images import merger

# Get the name of this file, set up logging for this filename
filename = os.path.basename(__file__).split('.py')[0]
logger = logging.getLogger(filename)


class DateAndTime(inkycal_module):
     # name is the name that will be shown on the web-ui
     # may be same or different to the class name (Do not remove this)
     name = "Date and Time"

     # create a dictionary containing variables which your module must have
     # to run correctly, e.g. if your module needs an 'api-key' and a 'name':
     requires = {}

     def __init__(self, config):
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
          self.timezone = get_system_tz()

          # give an OK message
          print(f'{filename} loaded')

     def generate_image(self):
          im_width = int(self.width - (2 * self.padding_left))
          im_height = int(self.height - (2 * self.padding_top))
          im_size = im_width, im_height

          logger.info('image size: {} x {} px'.format(im_width, im_height))

          # Create an image for black pixels and one for coloured pixels (required)
          im_black = Image.new('RGB', size=im_size, color='white')
          im_colour = Image.new('RGB', size=im_size, color='white')

          # Dateline
          dateline_font = ImageFont.truetype(fonts["NotoSansUI-Bold"], 48)
          today = str(arrow.now(self.timezone).floor("day").format("dddd, MMM DD"))
          line_under_dateline = ImageDraw.Draw(im_black)
          line_under_dateline.line(((0, 90), (im_width, 90)), fill="black", width=10)
          write(im_black, (0, 0), (im_width, 85), today, font=dateline_font, autofit=False, alignment="center")

          # Current time
          time_font = dateline_font = ImageFont.truetype(fonts["NotoSansUI-Regular"], 38)
          now = str(arrow.now(self.timezone).floor("minute").format("h:mm a"))
          write(im_black, (0, 80), (im_width, 80), now, font=dateline_font, autofit=False, alignment="center")
          line_under_time = ImageDraw.Draw(im_black)
          line_under_time.line(((0, 150), (im_width, 150)), fill="black", width=5)

          # weather placeholder
          weather_font = ImageFont.truetype(fonts["NotoSansUI-Regular"], 25)
          line_under_weather = ImageDraw.Draw(im_black)
          line_under_weather.line(((0, 250), (im_width, 250)), fill="black", width=10)
          write(im_black,
                (0, 132),
                (im_width, 132),
                text="Weather will go here",
                font=weather_font,
                autofit=False,
                alignment="center")
          return im_black, im_colour

if __name__ == '__main__':
    print(f'running {filename} in standalone mode')
    with open('/Users/dcostoy/PycharmProjects/Inkycal/settings.json') as settings_file:
        settings = json.load(settings_file)
        img, color = DateAndTime(settings["modules"][2]).generate_image()
        img.save(f"module_dateandtime_black.png", "PNG")
        color.save(f"module_dateandtime_color.png", "PNG")
        merged = merger.merge("module_dateandtime_black.png", "module_dateandtime_color.png",
                                     "module_dateandtime_merged")
