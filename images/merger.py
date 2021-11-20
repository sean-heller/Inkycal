from PIL import Image
import numpy

image1_path = "/home/pi/Desktop/cal.png"
image2_path = "/home/pi/Desktop/cal2.png"
output_file = "/home/pi/Desktop/merged.png"


def merge(image1_path, image2_path, out_filename):
    """Merge black pixels from image2 into image 1
  module_name = name of the module generating the image
  out_filename = what name to give to the finished file
  """

    im1_name, im2_name = image1_path, image2_path
    im1 = Image.open(im1_name).convert('RGBA')
    im2 = Image.open(im2_name).convert('RGBA')


    # To-do - make foreground color red
    """ def black_to_red(img) -> Image: """


    def clear_white(img):
        """Replace all white pixels from image with transparent pixels
    """
        x = numpy.asarray(img.convert('RGBA')).copy()
        x[:, :, 3] = (255 * (x[:, :, :3] != 255).any(axis=2)).astype(numpy.uint8)
        return Image.fromarray(x)

    # im2 = black_to_red(im2)
    im2 = clear_white(im2)
    im1.paste(im2, (0, 0), im2)
    im1.save(out_filename + '.png', 'PNG')


print('Done')
