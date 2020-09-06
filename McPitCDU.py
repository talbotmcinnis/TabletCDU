#!python2
from __future__ import print_function

import sys, pygame, math

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
        pygame.scrap.put(SCRAP_TEXT, ('Control(' + str(self.X) + ',' + str(self.Y) + ',' + str(self.WIDTH) + ',' + str(self.HEIGHT) + ',\'\',\'BTN\'),').encode('utf-8'))

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
    screen.blit(font[c], (205+CHARACTER_WIDTH*column, 365+CHARACTER_HEIGHT*line))

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
    elif(btn == 'SCROLL_R'):
        msg1 = 'CDU_SCROLL 0'
        msg2 = 'CDU_SCROLL 1'
    elif(btn == 'SCROLL_L'):
        msg1 = 'CDU_SCROLL 2'
        msg2 = 'CDU_SCROLL 1'
    elif(btn == 'TOGGLE'):
        return
    else:
        if mode == 'ARC210':
            msg1 = 'ARC210_' + btn + ' 1'
            msg2 = 'ARC210_' + btn + ' 0'
        else:
            msg1 = 'CDU_' + btn + ' 1'
            msg2 = 'CDU_' + btn + ' 0'

    click_sound.play()
    pygame.draw.rect(screen, (150,150,150),(ctl.X,ctl.Y,ctl.WIDTH,ctl.HEIGHT), 3)   # Apply a little click effect
    
    print('Sending'+msg1);
    s_tx.send(msg1+'\n')
    sleep(0.1)
    s_tx.send(msg2+'\n')

def rotate_control(control,amount):
    print('ROT: ' + control.PARAM + ' ' + `(rotating_last_y-y)`)
    # TODO: For amount, send INC/DEC commands

def select_control(control,angle):
    print( 'MOVING SELECTOR: ' + control.PARAM + ' Angle=' + `angle`)
    # TODO: Send the command that matches the angle
                        
# Setup the display callback for when parsed data changes
def update_display(address, data):
        #print('Parser update {}={}'.format(address,data))
        if mode == 'arc210':
            # TODO: Receive the SEL mode positions and rotate their knob accordingly
            
            if address >= ARC210DISPLAY_START_ADDRESS and address < ARC210DISPLAY_START_ADDRESS + 10*24: # TODO: ARC210 max?
                offset = address - ARC210DISPLAY_START_ADDRESS
                data_bytes = struct.pack("<H", data)
                arc210_display_data[offset] = data_bytes[0]
                arc210_display_data[offset+1] = data_bytes[1]

        else:
            if address >= CDUDISPLAY_START_ADDRESS and address < CDUDISPLAY_START_ADDRESS + 10*24:
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
ARC210DISPLAY_START_ADDRESS = 0x11c0 # TODO

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

Control = namedtuple("Control", "X Y WIDTH HEIGHT PARAM TYPE")
cdu_controls = [Control(66,531,79,86,'SYS', 'BTN'),
               Control(149,531,79,86,'NAV', 'BTN'),
               Control(232,531,79,86,'WP', 'BTN'),
               Control(318,530,79,86,'OSET', 'BTN'),
               Control(396,530,79,86,'FPM', 'BTN'),
               Control(482,531,79,86,'PREV', 'BTN'),
               Control(298,638,80,92,'A', 'BTN'),
               Control(379,638,80,92,'B', 'BTN'),
               Control(457,638,80,92,'C', 'BTN'),
               Control(538,638,80,92,'D', 'BTN'),
               Control(619,638,80,92,'E', 'BTN'),
               Control(700,638,80,92,'F', 'BTN'),
               Control(298,738,79,103,'G', 'BTN'),
               Control(379,738,79,103,'H', 'BTN'),
               Control(458,738,79,103,'I', 'BTN'),
               Control(539,738,79,103,'J', 'BTN'),
               Control(620,738,79,103,'K', 'BTN'),
               Control(702,738,79,103,'L', 'BTN'),
               Control(298,845,79,89,'M', 'BTN'),
               Control(379,845,79,89,'N', 'BTN'),
               Control(460,845,79,89,'O', 'BTN'),
               Control(540,845,79,86,'P', 'BTN'),
               Control(621,845,79,86,'Q', 'BTN'),
               Control(703,845,79,86,'R', 'BTN'),
               Control(297,944,79,93,'S', 'BTN'),
               Control(379,944,79,93,'T', 'BTN'),
               Control(461,944,79,93,'U', 'BTN'),
               Control(540,944,79,93,'V', 'BTN'),
               Control(620,944,79,93,'W', 'BTN'),
               Control(703,944,79,92,'X', 'BTN'),
               Control(188,944,93,98,'SLASH', 'BTN'),
               Control(2,944,93,98,'POINT', 'BTN'),
               Control(13,632,82,104,'1', 'BTN'),
               Control(102,632,82,104,'2', 'BTN'),
               Control(188,632,82,104,'3', 'BTN'),
               Control(14,736,82,104,'4', 'BTN'),
               Control(101,736,82,104,'5', 'BTN'),
               Control(188,736,82,104,'6', 'BTN'),
               Control(14,839,82,104,'7', 'BTN'),
               Control(99,839,82,104,'8', 'BTN'),
               Control(188,839,82,104,'9', 'BTN'),
               Control(99,944,82,104,'0', 'BTN'),
               Control(46,163,118,70,'LSK_3L', 'BTN'),
               Control(46,234,118,70,'LSK_5L', 'BTN'),
               Control(46,303,118,67,'LSK_7L', 'BTN'),
               Control(46,374,118,67,'LSK_9L', 'BTN'),
               Control(631,163,118,70,'LSK_3R', 'BTN'),
               Control(631,234,118,70,'LSK_5R', 'BTN'),
               Control(631,303,118,67,'LSK_7R', 'BTN'),
               Control(631,374,118,67,'LSK_9R', 'BTN'),
               Control(316,1047,82,104,'BCK', 'BTN'),
               Control(402,1047,82,104,'SPC', 'BTN'),
               Control(485,1047,77,104,'Y', 'BTN'),
               Control(564,1047,77,104,'Z', 'BTN'),
               Control(656,1058,72,89,'+', 'BTN'),
               Control(656,1152,72,89,'-', 'BTN'),
               Control(566,1155,72,104,'FA', 'BTN'),
               Control(483,1153,80,91,'CLR', 'BTN'),
               Control(190,1153,80,91,'MK', 'BTN'),
               Control(65,1153,80,91,'PG-', 'BTN'),
               Control(65,1056,80,91,'PG+', 'BTN'),
               Control(717,1,82,75,'QUIT', 'BTN'),
               Control(284,1153,95,91,'SCROLL_L', 'BTN'),
               Control(379,1153,95,91,'SCROLL_R', 'BTN'),
               Control(1,1,82,75,'TOGGLE', 'BTN'),
               ]

arc210_controls = [
                Control(717,1,82,75,'QUIT', 'BTN'),
                Control(1,1,82,75,'TOGGLE', 'BTN'),

                Control(515,205,110,68,'RTSELECT', 'BTN'),
                Control(403,205,80,68,'GPS', 'BTN'),
                Control(292,205,80,68,'TOD_RCV', 'BTN'),
                Control(143,207,80,68,'TOD_SND', 'BTN'),
                Control(40,345,97,68,'LSK_1', 'BTN'),
                Control(40,473,97,68,'LSK_2', 'BTN'),
                Control(40,604,97,68,'LSK_3', 'BTN'),
                Control(8,694,61,94,'BRT_INC', 'BTN'),
                Control(10,827,57,80,'BRT_DEC', 'BTN'),
                Control(718,465,68,90,'AM_FM', 'BTN'),
                Control(715,600,71,95,'OFFSET_RCV', 'BTN'),
                Control(611,600,71,95,'XMT_RCV_SND', 'BTN'),
                Control(612,467,71,95,'MENU_TIME', 'BTN'),
                Control(724,723,63,173,'ENTER', 'BTN'),
                Control(91,752,88,104,'FREQ_X00_MHZ', 'ROT'),
                Control(222,752,92,104,'FREQ_X0_MHZ', 'ROT'),
                Control(354,752,85,104,'FREQ_X_MHZ', 'ROT'),
                Control(488,752,85,104,'FREQ_X00_KHZ', 'ROT'),
                Control(617,744,85,104,'FREQ_0XXKHZ', 'ROT'),
                Control(345,897,101,117,'CHANNEL', 'ROT'),

                Control(153,900,103,125,'ARC210_LEFT_MODE', 'SEL'),
                Control(543,892,103,125,'ARC210_RIGHT_MODE', 'SEL'),
                Control(640,329,90,87,'SQUELCH', 'SEL'),
               ]

# Initialization

# use UDP (configure a UDPSender in BIOSConfig.lua
# to send the data to the host running this script)
# Line is:
# BIOS.protocol_io.UDPSender:create({ port = 7779, host = "127.0.0.1" })
CONNECTION = {
    "host":"192.168.84.139"
}

print ('Waiting to connect...')

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(0)
#s.bind(("0.0.0.0", 7779)) # Todo: put these back in for production


print('Connected.  Opening outbound socket')

s_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_tx.settimeout(0)
#s_tx.connect((CONNECTION["host"], 7778)) # Todo: put these back in for production

print('Connected.')

pygame.init()
pygame.mixer.init()

cdu_display_data = bytearray(24*10)
arc210_display_data = bytearray(24*10)

mode = "cdu"

size = width, height = 800, 1280
screen = pygame.display.set_mode(size, pygame.DOUBLEBUF , 32)
# | pygame.NOFRAME | pygame.FULLSCREEN  # Todo: put these back in for production

#Loading
font_img = pygame.image.load("font_A-10_CDU.tga")  # 512x512 pixel, 8x8 characters

cdu_bg = pygame.image.load("cdu_bg.bmp")
cdu_bg = pygame.transform.scale(cdu_bg, (width,height))

arc210_bg = pygame.image.load("arc-210_bg.bmp")
arc210_bg = pygame.transform.scale(arc210_bg, (width,height))

rotator_img = pygame.image.load("rotator.png")
rotator_img = pygame.transform.scale(rotator_img, (90,90))

squelch_img = pygame.image.load("squelch_knob.png")
squelch_img = pygame.transform.scale(squelch_img, (70,70))


#cdu_bg_rect = cdu_bg.get_rect()

click_sound = pygame.mixer.Sound("click.wav")

# MAP the font into individual charaters
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
#pixelRuler = PixelRuler(650,400,82,104)

clock = pygame.time.Clock()
frame_count = 0
looprate_max = 60 # Keep the loop fast to receive DCS data (45hz actual), but only display it at a fraction of that
display_divider = 4
display_counter = 0

print('Starting main loop')
running = True
rotating_control = None
rotating_last_y = 0
selector_initial_xy = (0,0)

while running == True:
    # Slow down the loop so we don't kill the CPU
    msThisFrame = clock.tick(looprate_max)
    #print('FPS:' + str(1000/msThisFrame))
  
    # PyGame event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif( event.type is MOUSEMOTION ):
            if rotating_control is not None:
                if rotating_control.TYPE == 'SEL':
                    x,y = pygame.mouse.get_pos()
                    sel_x, sel_y = selector_initial_xy;
                    dx = x - sel_x
                    dy = y - sel_y
                    magnitude = abs(math.sqrt(dx*dx + dy*dy))
                    if( magnitude > 75 ):
                        angle = 0
                        if dx == 0 :
                            if dy >= 0:
                                angle = 0
                            else:
                                angle = 180
                        else:
                            angle = math.degrees(math.atan(dy/float(dx)))
                            if dx > 0:
                                angle += 90
                            else:
                                angle += 270

                        select_control(rotating_control, angle)                        
        elif( event.type is MOUSEBUTTONUP ):
            rotating_control = None
            #print( 'MOUSEBUTTONUP' )
        elif( rotating_control is not None ):
            x,y = pygame.mouse.get_pos()
            rotate_control(rotating_control, rotating_last_y-y)
            rotating_last_y = y
        elif( event.type is MOUSEBUTTONDOWN ):
            pos = pygame.mouse.get_pos()
            x,y = pos
            activeControls = arc210_controls if mode == 'arc210' else cdu_controls
                        
            for ctl in activeControls:
                if( x >= ctl.X and x < (ctl.X+ctl.WIDTH) and y >= ctl.Y and (y < ctl.Y+ctl.HEIGHT) ):
                    if( ctl.TYPE == 'ROT' ):
                        print('Start ROT: ' + ctl.PARAM)
                        rotating_control = ctl
                        rotating_last_y = y
                        click_sound.play()
                    elif( ctl.TYPE == 'SEL' ):
                        print('Start SEL: ' + ctl.PARAM)
                        rotating_control = ctl
                        selector_initial_xy = pos
                    else:
                        if( ctl.PARAM == "QUIT" ):
                            running = False
                        elif( ctl.PARAM == "TOGGLE" ):
                            mode = "cdu" if mode == 'arc210' else 'arc210'
                        else:
                            btn_press(ctl.PARAM)
                    break
            
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

            left_knob_image = pygame.transform.rotate(rotator_img, -45)
            left_knob_width,left_knob_height = left_knob_image.get_size()
            screen.blit(left_knob_image, (206 - (left_knob_width/2),961 - (left_knob_height/2)))

            right_knob_image = pygame.transform.rotate(rotator_img, -90)
            right_knob_width,right_knob_height = right_knob_image.get_size()
            screen.blit(right_knob_image, (594 - (right_knob_width/2),956 - (right_knob_height/2)))

            squelch_knob_image = pygame.transform.rotate(squelch_img, -22.5)
            squelch_knob_width,squelch_knob_height = squelch_knob_image.get_size()
            screen.blit(squelch_knob_image, (684 - (squelch_knob_width/2),366 + 7 - (squelch_knob_height/2)))
        else:
            for i in range(24*10):
                row = i // 24
                col = i - (row*24)

                set_cdu_char(row, col, chr(cdu_display_data[i]))
                    
                #print('data{},{}={} []'.format(row,col,format(cdu_display_data[i],'02x'),chr(cdu_display_data[i])))
"""
        #Debug only print all button outlines
        for btn in arc210_controls:
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
"""

        pygame.display.flip()

pygame.quit()
sys.exit()
