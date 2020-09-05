#!python2
from __future__ import print_function

import sys, pygame

import socket
from pygame.locals import *
from time import sleep
from collections import namedtuple
from dcsbios import ProtocolParser, StringBuffer, IntegerBuffer

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
        pygame.scrap.put(SCRAP_TEXT, ('ARC210Button(' + str(self.X) + ',' + str(self.Y) + ',' + str(self.WIDTH) + ',' + str(self.HEIGHT) + ',\'\'),').encode('utf-8'))

def get_subimg(index):
        assert index >= 0 and index <= 63
        row = index // 8
        col = index - row*8
        img = font_img.subsurface(col*64, row*64, 64, 64)
        return img

def set_cdu_char(line, column, c):
    if c not in font:
        c = b"?"
    screen.blit(font[c], (178+CHARACTER_WIDTH*column, 117+CHARACTER_HEIGHT*line))

def set_arc210_char(line, column, c):
    if c not in font:
        c = b"X"
    screen.blit(font[c], (178+CHARACTER_WIDTH*column, 117+CHARACTER_HEIGHT*line))

def btn_press(btn):
    if(btn == '+'):
        msg1 = 'CDU_DATA 2'
        msg2 = 'CDU_DATA 1'
    elif(btn == '-'):
        msg1 = 'CDU_DATA 0'
        msg2 = 'CDU_DATA 1'
    elif(btn == 'PG+'):
        msg1 = 'CDU_PG 2'
        msg2 = 'CDU_PG 1'
    elif(btn == 'PG-'):
        msg1 = 'CDU_PG 0'
        msg2 = 'CDU_PG 1'
    elif(btn == 'SCROLL_L'):
        msg1 = 'CDU_SCROLL 0'
        msg2 = 'CDU_SCROLL 1'
    elif(btn == 'SCROLL_R'):
        msg1 = 'CDU_SCROLL 2'
        msg2 = 'CDU_SCROLL 1'
    else:
        msg1 = 'CDU_' + btn + ' 1'
        msg2 = 'CDU_' + btn + ' 0'
        
    s_tx.send(msg1+'\n')
    sleep(0.1)
    s_tx.send(msg2+'\n')

def rotate_control(control,amount):
    print('ROT: ' + control + ' ' + `(rotating_last_y-y)`)
    # TODO: For amount, send INC/DEC commands
            

# Setup the display callback for when parsed data changes
def update_display(address, data):
        #print('Parser update {}={}'.format(address,data))
        if address < CDUDISPLAY_START_ADDRESS or address >= CDUDISPLAY_START_ADDRESS + 10*24:
            #print('bad addr');
            return
        
        offset = address - CDUDISPLAY_START_ADDRESS
        data_bytes = struct.pack("<H", data)
        cdu_display_data[offset] = data_bytes[0]
        cdu_display_data[offset+1] = data_bytes[1]

# Constants
CDU_COLOR = (0, 255, 0)
CHARACTER_SIZE = 21
CHARACTER_WIDTH = 18
CHARACTER_HEIGHT = 36
CDUDISPLAY_START_ADDRESS = 0x11c0

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
               CDUButton(188,944,93,98,'SLASH'),
               CDUButton(2,944,93,98,'POINT'),
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
               CDUButton(46,163,118,70,'LSK_3L'),
               CDUButton(46,234,118,70,'LSK_5L'),
               CDUButton(46,303,118,67,'LSK_7L'),
               CDUButton(46,374,118,67,'LSK_9L'),
               CDUButton(631,163,118,70,'LSK_3R'),
               CDUButton(631,234,118,70,'LSK_5R'),
               CDUButton(631,303,118,67,'LSK_7R'),
               CDUButton(631,374,118,67,'LSK_9R'),
               CDUButton(316,1047,82,104,'BCK'),
               CDUButton(402,1047,82,104,'SPC'),
               CDUButton(485,1047,77,104,'Y'),
               CDUButton(564,1047,77,104,'Z'),
               CDUButton(656,1058,72,89,'+'),   ###
               CDUButton(656,1152,72,89,'-'),   ###
               CDUButton(566,1155,72,104,'FA'),
               CDUButton(483,1153,80,91,'CLR'),
               CDUButton(190,1153,80,91,'MK'),
               CDUButton(65,1153,80,91,'PG-'), ###
                CDUButton(65,1056,80,91,'PG+'), ###
               CDUButton(717,1,82,75,'QUIT'),
               CDUButton(284,1153,95,91,'SCROLL_L'),
               CDUButton(379,1153,95,91,'SCROLL_R'),
               CDUButton(1,1,82,75,'TOGGLE'),
               ]

ARC210Button = namedtuple("ARC210Button", "X Y WIDTH HEIGHT PARAM TYPE")
arc210_buttons = [
                ARC210Button(717,1,82,75,'QUIT', 'BTN'),
                ARC210Button(1,1,82,75,'TOGGLE', 'BTN'),

                ARC210Button(515,205,110,68,'RTSELECT', 'BTN'),
                ARC210Button(403,205,80,68,'GPS', 'BTN'),
                ARC210Button(292,205,80,68,'TOD_RCV', 'BTN'),
                ARC210Button(143,207,80,68,'TOD_SND', 'BTN'),
                ARC210Button(40,345,97,68,'LSK_1', 'BTN'),
                ARC210Button(40,473,97,68,'LSK_2', 'BTN'),
                ARC210Button(40,604,97,68,'LSK_3', 'BTN'),
                ARC210Button(8,694,61,94,'BRT_INC', 'BTN'),
                ARC210Button(10,827,57,80,'BRT_DEC', 'BTN'),
                ARC210Button(603,320,78,93,'SQL_OFF', 'BTN'),
                ARC210Button(685,320,78,93,'SQL_ON', 'BTN'),
                ARC210Button(718,465,68,90,'AM_FM', 'BTN'),
                ARC210Button(715,600,71,95,'OFFSET_RCV', 'BTN'),
                ARC210Button(611,600,71,95,'XMT_RCV_SND', 'BTN'),
                ARC210Button(612,467,71,95,'MENU_TIME', 'BTN'),
                ARC210Button(724,723,63,173,'ENTER', 'BTN'),
                ARC210Button(91,752,88,104,'FREQ_X00_MHZ', 'ROT'),
                ARC210Button(222,752,92,104,'FREQ_X0_MHZ', 'ROT'),
                ARC210Button(354,752,85,104,'FREQ_X_MHZ', 'ROT'),
                ARC210Button(488,752,85,104,'FREQ_X00_KHZ', 'ROT'),
                ARC210Button(617,744,85,104,'FREQ_0XXKHZ', 'ROT'),
                ARC210Button(345,897,101,117,'CHANNEL', 'ROT'),
               ]

# Initialization

# use UDP (configure a UDPSender in BIOSConfig.lua
# to send the data to the host running this script)
# Line is:
# BIOS.protocol_io.UDPSender:create({ port = 7779, host = "127.0.0.1" })
CONNECTION = {
    "host":"192.168.0.29"
}

print ('Waiting to connect...')

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", 7779))
s.settimeout(0)

print('Connected.  Opening outbound socket')

s_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_tx.connect((CONNECTION["host"], 7778))
s_tx.settimeout(0)

print('Connected.')

pygame.init()
pygame.mixer.init()

cdu_display_data = bytearray(24*10)
arc210_display_data = bytearray(24*10)

mode = "cdu"

size = width, height = 800, 1280
screen = pygame.display.set_mode(size, pygame.DOUBLEBUF , 32)
# | pygame.NOFRAME | pygame.FULLSCREEN

#Loading
font_img = pygame.image.load("font_A-10_CDU.tga")  # 512x512 pixel, 8x8 characters

cdu_bg = pygame.image.load("cdu_bg.bmp")
cdu_bg = pygame.transform.scale(cdu_bg, (width,height))

arc210_bg = pygame.image.load("arc-210_bg.bmp")
arc210_bg = pygame.transform.scale(arc210_bg, (width,height))

#cdu_bg_rect = cdu_bg.get_rect()

click_sound = pygame.mixer.Sound("click.wav")

for k in pos_map.keys():
        img = get_subimg(pos_map[k])
        for x in range(64):
                for y in range(64):
                        r,g,b,a = img.get_at((x,y))
                        if a > 128:
                                img.set_at((x,y), CDU_COLOR)
        img = pygame.transform.scale(img, (CHARACTER_SIZE, CHARACTER_SIZE))
        font[k] = img

# DCS-Bios Parser
parser = ProtocolParser()
parser.write_callbacks.add(update_display)

pygame.scrap.init()
pixelRuler = PixelRuler(50,900,82,104)

clock = pygame.time.Clock()
frame_count = 0
looprate_max = 60 # Keep the loop fast to receive DCS data (45hz actual), but only display it at a fraction of that
display_divider = 4
display_counter = 0

print('Starting main loop')
running = True
rotating_control = 0
rotating_last_y = 0
while running == True:
    # Slow down the loop so we don't kill the CPU
    msThisFrame = clock.tick(looprate_max)
    #print('FPS:' + str(1000/msThisFrame))
  
    # PyGame event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif( rotating_control != 0 ):
            x,y = pygame.mouse.get_pos()
            rotate_control(rotating_control, rotating_last_y-y)
            rotating_last_y = y
        elif( event.type is MOUSEBUTTONUP ):
            rotating_control = 0
        elif( event.type is MOUSEBUTTONDOWN ):
            pos = pygame.mouse.get_pos()
            x,y = pos
            if mode == "arc210":
                for btn in arc210_buttons:
                    if( x >= btn.X and x < (btn.X+btn.WIDTH) and y >= btn.Y and (y < btn.Y+btn.HEIGHT) ):
                        
                        if( btn.TYPE == 'ROT' ):
                            print('Start ROT: ' + btn.PARAM)
                            rotating_control = btn.PARAM
                            rotating_last_y = y
                            click_sound.play()
                        else:
                            print('Click: ' + btn.PARAM)
                            btn_press(btn.PARAM)
                            if( btn.PARAM == "QUIT" ):
                                running = False
                            elif( btn.PARAM == "TOGGLE" ):
                                mode = "cdu"
                            else:
                                click_sound.play()
                                pygame.draw.rect(screen, (150,150,150),(btn.X,btn.Y,btn.WIDTH,btn.HEIGHT), 3)
            
            elif( mode == "cdu"):
                for btn in cdu_buttons:
                    if( x >= btn.X and x < (btn.X+btn.WIDTH) and y >= btn.Y and (y < btn.Y+btn.HEIGHT) ):
                        print(btn.PARAM)
                        btn_press(btn.PARAM)
                        if( btn.PARAM == "QUIT" ):
                            running = False
                        elif( btn.PARAM == "TOGGLE" ):
                            mode = "arc210"
                        else:
                            click_sound.play()
                            pygame.draw.rect(screen, (150,150,150),(btn.X,btn.Y,btn.WIDTH,btn.HEIGHT), 3)
                                      

    # Receive new data from DCS
    while 1:
        try:
            data = s.recv(8192)
            if data:
                #print('Data: ',end='')
                for c in data:
                    #print(c,end='')
                    parser.processByte(c)
                #print('')
            else:
                print('No Data')
        except BaseException as e:
            #print('Parser Exception: '+ str(e))
            break;
        
    # See if its time to display a frame
    display_counter = display_counter+1
    if display_counter == display_divider:
        display_counter = 0
        #Draw the background
        screen.blit(arc210_bg if mode == "arc210" else cdu_bg, (0,0))

        # Draw the screen data
        if mode=="arc210":
            for i in range(24*10):
                row = i // 24
                col = i - (row*24)

                set_arc210_char(row, col, chr(arc210_display_data[i]))
        else:
            for i in range(24*10):
                row = i // 24
                col = i - (row*24)

                set_cdu_char(row, col, chr(cdu_display_data[i]))
                    
                #print('data{},{}={} []'.format(row,col,format(cdu_display_data[i],'02x'),chr(cdu_display_data[i])))

        #Debug only print all button outlines
        for btn in arc210_buttons:
            pygame.draw.rect(screen, (0,255,0),(btn.X,btn.Y,btn.WIDTH,btn.HEIGHT), 1)
        pygame.draw.rect(screen, (255,0,0),(pixelRuler.X,pixelRuler.Y,pixelRuler.WIDTH,pixelRuler.HEIGHT), 1)

        # Debug print the pixel ruler
        keys = pygame.key.get_pressed()
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
            pixelRuler.ToClipboard()
        
        pygame.display.flip()

pygame.quit()
sys.exit()
