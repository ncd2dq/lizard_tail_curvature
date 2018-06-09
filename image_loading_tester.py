from PIL import Image

im = Image.open('small_test.png')
im.load()

pixels = list(im.getdata())

width, height = im.size

