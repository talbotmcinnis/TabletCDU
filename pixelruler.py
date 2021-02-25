#!python2
from __future__ import print_function

import sys, pygame, math

from pygame.locals import *

import struct

class PixelRuler:
    X = 0
    Y = 0
    WIDTH = 50
    HEIGHT = 50

    def __init__(self, x,y,width,height):
        self.X = x
        self.Y = y
        self.WIDTH = width
        self.HEIGHT = height

    def ToClipboard(self):
        pygame.scrap.put(SCRAP_TEXT, ('Control(' + str(self.X) + ',' + str(self.Y) + ',' + str(self.WIDTH) + ',' + str(self.HEIGHT) + ',\'\',\'BTN\'),').encode('utf-8'))
