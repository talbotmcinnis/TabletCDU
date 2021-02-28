#!python2
from __future__ import print_function

import sys, pygame, math

from pygame.locals import *

import struct

class BitmapFontScreen:
    pos_map = {
        chr(0xA9):0, # SYS_ACTION / "bullseye"
        chr(0xAE):1, # ROTARY / up/down arrow
        chr(0xA1):2, # DATA_ENTRY / "[]" symbol
        chr(0xBB):3, # right arrow
        chr(0xAB):4, # left arrow
        b" ":5,
        b"!":6,
        b"#":7,
        b"(":8,
        b")":9,
        b"*":10,
        b"+":11,
        b"-":12,
        b".":13,
        b"/":14,
        b"0":15,
        b"1":16,
        b"2":17,
        b"3":18,
        b"4":19,
        b"5":20,
        b"6":21,
        b"7":22,
        b"8":23,
        b"9":24,
        b":":25,
        b"=":26,
        b"?":27,
        b"A":28,
        b"B":29,
        b"C":30,
        b"D":31,
        b"E":32,
        b"F":33,
        b"G":34,
        b"H":35,
        b"I":36,
        b"J":37,
        b"K":38,
        b"L":39,
        b"M":40,
        b"N":41,
        b"O":42,
        b"P":43,
        b"Q":44,
        b"R":45,
        b"S":46,
        b"T":47,
        b"U":48,
        b"V":49,
        b"W":50,
        b"X":51,
        b"Y":52,
        b"Z":53,
        b"[":54,
        b"]":55,
        chr(0xB6):56, # filled / cursor
        chr(0xB1):57, # plus/minus
        chr(0xB0):58  # degree
        }

    def __init__(self, screen, screenX, screenY, charColor, scale, lineSpacing):
        self.SCREEN = screen
        self.SCREEN_X = screenX
        self.SCREEN_Y = screenY
        self.CHARACTER_SIZE = int(21 * scale)
        self.CHARACTER_WIDTH = int(18 * scale)
        self.CHARACTER_HEIGHT = int(36 * scale)
        self.CHARACTER_COLOR = charColor
        self.LINE_SPACING = lineSpacing
        self.font = {}
        self.font_img = pygame.image.load("font_A-10_CDU.tga")  # 512x512 pixel, 8x8 characters

        # MAP the font into individual charaters
        for k in self.pos_map.keys():
                img = self.get_subimg(self.pos_map[k])
                for x in range(64):
                        for y in range(64):
                                r,g,b,a = img.get_at((x,y))
                                if a > 128:
                                        img.set_at((x,y), self.CHARACTER_COLOR)
                img = pygame.transform.scale(img, (self.CHARACTER_SIZE, self.CHARACTER_SIZE))
                self.font[k] = img

    def get_subimg(self, index):
            assert index >= 0 and index <= 63
            row = index // 8
            col = index - row*8
            img = self.font_img.subsurface(col*64, row*64, 64, 64)
            return img

    def set_char(self, line, column, c):
        if c not in self.font:
            c = b"?"
        self.SCREEN.blit(self.font[c], (self.SCREEN_X+self.CHARACTER_WIDTH*column, self.SCREEN_Y+(self.CHARACTER_HEIGHT+self.LINE_SPACING)*line))
