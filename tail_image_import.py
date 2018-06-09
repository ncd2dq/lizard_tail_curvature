from PIL import Image
from os import walk
import csv
from math import sqrt
from time import sleep
from itertools import tee
import matplotlib.pyplot as plt
# os.walk() iterates through all files in a directory




class ImageDownloader(object):
    def __init__(self):
        self.data_list = [] # [  {'x':[], 'y':[]}  ,  {'x':[], 'y':[]}  ]
        self.blank_space = [0, 0] # Avg, Std

    def getBrightness(self, pixel):
        '''
        formula for brightness
        sqrt(0.299 * r**2 + 0.587 * g**2 + 0.114 * b**2) 33% faster
        '''
        r = pixel[0]
        g = pixel[1]
        b = pixel[2]

        inside = 0.299 * (r**2) + 0.587 * (g**2) + 0.114 * (b**2)
        brightness = sqrt(inside)

        return brightness


    def imagePixelGenerator(self, img_path):
        '''
        Returns a generator that can be used to iterate through all pixels in an image.
        Call "for pixel in imagePixelTerator:""
        '''
        image = Image.open(img_path)
        image.load() # otherwise you have to open an dclose the image manually
        rgb = image.convert('RGB')
        pixelGenerator = image.getdata()

        return pixelGenerator


    def imageBrightnessIterator(self, img_path):
        '''
        Iterator of all the brightness values of an image
        '''
        imgGenerator = self.imagePixelGenerator(img_path)
        for pixel in imgGenerator:
            yield self.getBrightness(pixel)


    def determineAvgStd(self, brightness_iterator):
        '''
        Records the brightness value of every pixel in an image and calculates an average and std
        
        Formula used: Standard Deviation of a sample
        std_formula = E (x - average)**2
        sqrt(   (1 / (N - 1))   * std_formula )
        https://www.mathsisfun.com/data/standard-deviation-formulas.html
        '''

        ### Calculate average
        iter1, iter2 = tee(brightness_iterator) #creates a replica iterator
        count = 0
        total = 0

        for value in iter1:
            count += 1
            total += value

        average = total / count

        ### Calculate standard deviation
        bessel_correction = 1 / (total - 1)
        std_sum = 0.0

        for value in iter2:
            std_sum += (value - average)**2

        standard_deviation = sqrt(bessel_correction * std_sum)

        return average, standard_deviation


    def printStdAvg(self, img_path):
        avg, std = self.determineAvgStd(self.imageBrightnessIterator(img_path))
        print('Average Brightness: {}\nStandard Deviation: {}\n'.format(avg, std))


    def sampleBlankSpace(self, img_path):
        '''
        Takes in a sample blank space image to determine an avg/std pixel brightness, it will use this
        later to determine if a pixel IS NOT part of the blank space --> i.e. it is part of the tail
        '''
        # self.blank_space[0][1]
        avg, std = self.determineAvgStd(self.imageBrightnessIterator(img_path))
        self.blank_space[0] = avg
        self.blank_space[1] = std


    def sampleTail(self, img_path):
        '''
        Takes in a sample tail picture to determine an avg/std pixel brightness, it will use this later
        to determine if a pixel IS part of the tail

        this may slow it down too much?
        '''
        pass


    def recordCoordinates(self, img_path, blank_space_sensitivity=2):
        '''
        ### blank_space_sensitivity = standard deviations above average pixel brightness ###

        This method takes an image and sensitivty values.
        It will iterate through all the pixels as such: 
        col 1 --> every row
        col 2 --> every row 
        Reading the images from top to bottom and recording
        the x,y coordinate of the first pixel whose brightness value is greater than
        a certain threshold
        '''
        coordinate_dict = {'x': [], 'y': []} 
        img = Image.open(img_path)
        img.load()
        rgb = img.convert('RGB')

        for x in range(rgb.width):
            for y in range(rgb.height):
                pixel = rgb.getpixel((x, y))
                brightness = self.getBrightness(pixel)

                #testing
                if(x == 0 and y == 0):
                    print(self.blank_space[0] + self.blank_space[1] * blank_space_sensitivity)
                    print(brightness)
                    print(self.blank_space[0] - self.blank_space[1] * blank_space_sensitivity)

                if (brightness > self.blank_space[0] + self.blank_space[1] * blank_space_sensitivity) or (
                    brightness < self.blank_space[0] - self.blank_space[1] * blank_space_sensitivity):
                    coordinate_dict['x'].append(x)
                    coordinate_dict['y'].append(y)
                    break

        return coordinate_dict


    def plotSampleImg(self, coordinate_dict):
        '''Will plot the results of a given coordinate dictionary'''
        plt.plot(coordinate_dict['x'], coordinate_dict['y'])
        plt.ylabel('y position')
        plt.xlabel('x position')
        plt.show()




    #
    # THE PUBLIC SHOULD USE THE FOLLOWING METHODS
    #

    def runOnSampleImage(self):
        blank_space_path = input('Please enter blank space sample file path: ')
        self.sampleBlankSpace(blank_space_path)
        print('\nBackground Avg: {}\nBackground Std: {}'.format(self.blank_space[0], self.blank_space[1]))

        test_image_path = input('\nPlease enter test image file path: ')
        sensitivity = input('\nSelect sensitivity level (floating point)\nUniform backgrounds need higher sensitivity: ')

        sensitivity = float(sensitivity)

        coord_dict = self.recordCoordinates(test_image_path, blank_space_sensitivity=sensitivity)
        self.plotSampleImg(coord_dict)


    def toCSV(self):
        pass


if __name__ == '__main__':
    imgObj = ImageDownloader()
    imgObj.runOnSampleImage()

    sleep(10)