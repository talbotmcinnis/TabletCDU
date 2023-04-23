#!python2
from __future__ import print_function

import sys, pygame, math

from pygame.locals import *
from bitmapfontscreen import BitmapFontScreen

import struct

class TextScreenBuffer:
    WIDTH = 0
    HEIGHT = 0
    BUFFER = bytearray(1)
    BASE_ADDRESS = 0
    
    def __init__(self, baseAddress, width, height):
        self.WIDTH = width
        self.HEIGHT = height
        self.BASE_ADDRESS = baseAddress
        self.BUFFER = bytearray(self.WIDTH * self.HEIGHT)

    def notifyBytes(self, address, data):
        offset = address - self.BASE_ADDRESS
        data_bytes = struct.pack("<H", data)
        self.BUFFER[offset] = data_bytes[0]
        self.BUFFER[offset+1] = data_bytes[1]
        #print('Received',hex(address),hex(data_bytes[0]),hex(data_bytes[1]))

    def drawTo(self, fontScreen):
        for i in range(self.WIDTH*self.HEIGHT):
            row = i // self.WIDTH
            col = i - (row*self.WIDTH)
            #print('Printing',row,col,hex(self.BUFFER[i]))

            fontScreen.set_char(row, col, chr(self.BUFFER[i]))
