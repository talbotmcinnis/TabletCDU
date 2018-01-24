import sys, pygame

from pygame.locals import *
from time import sleep
from collections import namedtuple
from dcsbios import ProtocolParser, StringBuffer, IntegerBuffer

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
        pygame.scrap.put(SCRAP_TEXT, ('CDUButton(' + str(self.X) + ',' + str(self.Y) + ',' + str(self.WIDTH) + ',' + str(self.HEIGHT) + ',\'\'),').encode('utf-8'))

CDU_COLOR = (0, 255, 0)
CHARACTER_SIZE = 21
CHARACTER_WIDTH = 18
CHARACTER_HEIGHT = 36

pygame.init()
pygame.mixer.init()

font_img = pygame.image.load("font_A-10_CDU.tga")  # 512x512 pixel, 8x8 characters
click_sound = pygame.mixer.Sound("click.wav")

parser = ProtocolParser()

def get_subimg(index):
        assert index >= 0 and index <= 63
        row = index // 8
        col = index - row*8
        img = font_img.subsurface(col*64, row*64, 64, 64)
        return img

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

font = {}

for k in pos_map.keys():
        img = get_subimg(pos_map[k])
        for x in range(64):
                for y in range(64):
                        r,g,b,a = img.get_at((x,y))
                        if a > 128:
                                img.set_at((x,y), CDU_COLOR)
        img = pygame.transform.scale(img, (CHARACTER_SIZE, CHARACTER_SIZE))
        font[k] = img

def set_char(line, column, c):
        if c not in font:
            c = b"?"
        print(font[c])
        screen.blit(font[c], (180+CHARACTER_WIDTH*column, 117+CHARACTER_HEIGHT*line))

CDUDISPLAY_START_ADDRESS = 0x11c0
cdu_display_data = bytearray(24*10)

# Setup the display callback for when parsed data changes
def update_display(address, data):
        
        if address < CDUDISPLAY_START_ADDRESS or address >= CDUDISPLAY_START_ADDRESS + 10*24:
                return
        # print('Parser update {}={}'.format(address,data))
        offset = address - CDUDISPLAY_START_ADDRESS
        data_bytes = struct.pack("<H", data)
        cdu_display_data[offset] = data_bytes[0]
        cdu_display_data[offset+1] = data_bytes[1]

parser.write_callbacks.add(update_display)

size = width, height = 800, 1280

screen = pygame.display.set_mode(size, pygame.DOUBLEBUF | pygame.NOFRAME, 32)

pygame.scrap.init()

cdu_bg = pygame.image.load("cdu_bg.bmp")
cdu_bg = pygame.transform.scale(cdu_bg, (800,1280))
cdu_bg_rect = cdu_bg.get_rect()

CDUButton = namedtuple("CDUButton", "X Y WIDTH HEIGHT PARAM")
cdu_buttons = [CDUButton(66,531,79,86,'SYS'),
               CDUButton(149,531,79,86,'NAV'),
               CDUButton(232,531,79,86,'WP'),
               CDUButton(318,530,79,86,'OSET'),
               CDUButton(396,530,79,86,'FPM'),
               CDUButton(482,531,79,86,'PREV'),
               CDUButton(298,638,80,92,'A'),
               CDUButton(379,638,80,92,'B'),
               CDUButton(457,638,80,92,'C'),
               CDUButton(538,638,80,92,'D'),
               CDUButton(619,638,80,92,'E'),
               CDUButton(700,638,80,92,'F'),
               CDUButton(298,738,79,103,'G'),
               CDUButton(379,738,79,103,'H'),
               CDUButton(458,738,79,103,'I'),
               CDUButton(539,738,79,103,'J'),
               CDUButton(620,738,79,103,'K'),
               CDUButton(702,738,79,103,'L'),
               CDUButton(298,845,79,89,'M'),
               CDUButton(379,845,79,89,'N'),
               CDUButton(460,845,79,89,'O'),
               CDUButton(540,845,79,86,'P'),
               CDUButton(621,845,79,86,'Q'),
               CDUButton(703,845,79,86,'R'),
               CDUButton(297,944,79,93,'S'),
               CDUButton(379,944,79,93,'T'),
               CDUButton(461,944,79,93,'U'),
               CDUButton(540,944,79,93,'V'),
               CDUButton(620,944,79,93,'W'),
               CDUButton(703,944,79,92,'X'),
               CDUButton(188,944,93,98,'/'),
               CDUButton(2,944,93,98,'.'),
               CDUButton(13,632,82,104,'1'),
               CDUButton(102,632,82,104,'2'),
               CDUButton(188,632,82,104,'3'),
               CDUButton(14,736,82,104,'4'),
               CDUButton(101,736,82,104,'5'),
               CDUButton(188,736,82,104,'6'),
               CDUButton(14,839,82,104,'7'),
               CDUButton(99,839,82,104,'8'),
               CDUButton(188,839,82,104,'9'),
               CDUButton(99,944,82,104,'0'),
               CDUButton(46,163,118,70,'LSK1'),
               CDUButton(46,234,118,70,'LSK2'),
               CDUButton(46,303,118,67,'LSK3'),
               CDUButton(46,374,118,67,'LSK4'),
               CDUButton(631,163,118,70,'RSK1'),
               CDUButton(631,234,118,70,'RSK2'),
               CDUButton(631,303,118,67,'RSK3'),
               CDUButton(631,374,118,67,'RSK4'),
               CDUButton(316,1047,82,104,'BCK'),
               CDUButton(402,1047,82,104,'SPC'),
               CDUButton(485,1047,77,104,'Y'),
               CDUButton(564,1047,77,104,'Z'),
               CDUButton(656,1058,72,89,'+'),
               CDUButton(656,1152,72,89,'-'),
               CDUButton(566,1155,72,104,'FA'),
               CDUButton(483,1153,80,91,'CA'),
               CDUButton(190,1153,80,91,'MK'),
               CDUButton(65,1153,80,91,'PG-'),
                CDUButton(65,1056,80,91,'PG+')
               ]

#pixelRuler = PixelRuler(300,900,82,104)

running = True
while running == True:
    screen.blit(cdu_bg, (0,0))

    #Debug only print all button outlines
    #for btn in cdu_buttons:
    #    pygame.draw.rect(screen, (0,255,0),(btn.X,btn.Y,btn.WIDTH,btn.HEIGHT), 1)
    #pygame.draw.rect(screen, (255,0,0),(pixelRuler.X,pixelRuler.Y,pixelRuler.WIDTH,pixelRuler.HEIGHT), 1)

    # Debug print the pixel ruler
    """keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        pixelRuler.X -= 1
        pixelRuler.ToClipboard()
    elif keys[pygame.K_RIGHT]:
        pixelRuler.X += 1
        pixelRuler.ToClipboard()
    if keys[pygame.K_UP]:
        pixelRuler.Y -= 1
        pixelRuler.ToClipboard()
    if keys[pygame.K_DOWN]:
        pixelRuler.Y += 1;
        pixelRuler.ToClipboard()
    if keys[pygame.K_a]:
        pixelRuler.WIDTH -= 1
        pixelRuler.ToClipboard()
    if keys[pygame.K_d]:
        pixelRuler.WIDTH += 1
        pixelRuler.ToClipboard()
    if keys[pygame.K_w]:
        pixelRuler.HEIGHT -= 1
        pixelRuler.ToClipboard()
    if keys[pygame.K_s]:
        pixelRuler.HEIGHT += 1
        pixelRuler.ToClipboard()"""

    # Copy data from cdu data array to screen
    for i in range(24*10):
        row = i // 24
        col = i - (row*24)
        set_char(row, col, chr(cdu_display_data[i]))
			
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif( event.type is MOUSEBUTTONDOWN ):
            pos = pygame.mouse.get_pos()
            x,y = pos
            for btn in cdu_buttons:
                if( x >= btn.X and x < (btn.X+btn.WIDTH) and y >= btn.Y and (y < btn.Y+btn.HEIGHT) ):
                    print(btn.PARAM)
                    click_sound.play()
                    pygame.draw.rect(screen, (150,150,150),(btn.X,btn.Y,btn.WIDTH,btn.HEIGHT), 3)
        
    pygame.display.flip()
    
    sleep(0.5)

pygame.quit()
sys.exit()
