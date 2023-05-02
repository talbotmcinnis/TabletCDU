#!python2
from __future__ import print_function

import sys, pygame, math

import socket
from pygame.locals import *
from time import sleep
from collections import namedtuple
from dcsbios import ProtocolParser, StringBuffer, IntegerBuffer

from pixelruler import PixelRuler
from textscreenbuffer import TextScreenBuffer
from bitmapfontscreen import BitmapFontScreen

import struct

# use UDP (configure a UDPSender in BIOSConfig.lua
# to send the data to the host running this script)
# Line is:
# BIOS.protocol_io.UDPSender:create({ port = 7779, host = "127.0.0.1" })
CONNECTION = {
    "host":"192.168.84.139"
}

rotating_control = None
rotating_last_y = 0
selector_initial_xy = (0,0)

arc210_leftknob_rotation = 0
arc210_rightknob_rotation = 0
arc210_squelch_on = False

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
    elif(btn == 'TOGGLE'):
        return
    else:
        msg1 = btn + ' 1'
        msg2 = btn + ' 0'

    click_sound.play()
    pygame.draw.rect(screen, (150,150,150),(ctl.X,ctl.Y,ctl.WIDTH,ctl.HEIGHT), 3)   # Apply a little click effect
    
    print('Sending'+msg1);
    s_tx.send(msg1+'\n')
    sleep(0.1)
    s_tx.send(msg2+'\n')

def rotate_control(control,amount):
    #print('ROT: ' + control.PARAM + ' ' + str(amount))
    s_tx.send(control.PARAM+ ' ' + str(amount) +'\n')

def select_control(control,angle):
    numpos = int(control.TYPE.replace('SEL_',''))
    
    pos = math.floor(angle / 360 * numpos)
    pos = int((pos + (numpos/2)) % numpos) 
    s_tx.send(control.PARAM+ ' ' + str(pos) +'\n')
    # Debug only; test rotation UI
    #global arc210_leftknob_rotation
    #arc210_leftknob_rotation = (pos*360/numpos) - 180

    #print( 'MOVING SELECTOR: ' + control.PARAM + ' Angle=' + `angle` + ' Pos=' + `pos` + ' ImgAngle=' + `arc210_leftknob_rotation`)

cduScreenBuffer = TextScreenBuffer(0x11b4, 24,10)   # Note: 0x11C0 is the DCS offset for the CDU screen data
#arc210ScreenBuffer = TextScreenBuffer(0x11c0, 18,6)    # TODO: Find the offset for the ARC210 data  Derp, this won't ever work due to mixed sized fonts.

# Setup the display callback for when parsed data changes
def parser_callback(address, data):
        # print('Parser update {}={}'.format(address,data))
        if mode == 'arc210':
            if address == 0x12d4:
                newValue = (data & 0x0700) >> 8
                global arc210_leftknob_rotation
                arc210_leftknob_rotation = ((newValue+1)*360/8) - 180
                #print('Arc210 left knob to ', arc210_leftknob_rotation)                

                newValue = (data & 0x3800) >> 11
                global arc210_rightknob_rotation
                arc210_rightknob_rotation = ((newValue+1)*360/8) - 180
                #print('Arc210 right knob to ', arc210_rightknob_rotation)                
            elif address == 0x12e8:
                newValue = (data & 0x0004) >> 2
                global arc210_squelch_on
                arc210_squelch_on = newValue>0
                #print('Arc210 squelch to ', arc210_squelch_on)                
        else:
            if address >= cduScreenBuffer.BASE_ADDRESS and address < cduScreenBuffer.BASE_ADDRESS + cduScreenBuffer.WIDTH*cduScreenBuffer.HEIGHT:
                #print('CDU data...')
                cduScreenBuffer.notifyBytes(address, data)

Control = namedtuple("Control", "X Y WIDTH HEIGHT PARAM TYPE")
cdu_controls = [Control(66,531,79,86,'CDU_SYS', 'BTN'),
               Control(149,531,79,86,'CDU_NAV', 'BTN'),
               Control(232,531,79,86,'CDU_WP', 'BTN'),
               Control(318,530,79,86,'CDU_OSET', 'BTN'),
               Control(396,530,79,86,'CDU_FPM', 'BTN'),
               Control(482,531,79,86,'CDU_PREV', 'BTN'),
               Control(298,638,80,92,'CDU_A', 'BTN'),
               Control(379,638,80,92,'CDU_B', 'BTN'),
               Control(457,638,80,92,'CDU_C', 'BTN'),
               Control(538,638,80,92,'CDU_D', 'BTN'),
               Control(619,638,80,92,'CDU_E', 'BTN'),
               Control(700,638,80,92,'CDU_F', 'BTN'),
               Control(298,738,79,103,'CDU_G', 'BTN'),
               Control(379,738,79,103,'CDU_H', 'BTN'),
               Control(458,738,79,103,'CDU_I', 'BTN'),
               Control(539,738,79,103,'CDU_J', 'BTN'),
               Control(620,738,79,103,'CDU_K', 'BTN'),
               Control(702,738,79,103,'CDU_L', 'BTN'),
               Control(298,845,79,89,'CDU_M', 'BTN'),
               Control(379,845,79,89,'CDU_N', 'BTN'),
               Control(460,845,79,89,'CDU_O', 'BTN'),
               Control(540,845,79,86,'CDU_P', 'BTN'),
               Control(621,845,79,86,'CDU_Q', 'BTN'),
               Control(703,845,79,86,'CDU_R', 'BTN'),
               Control(297,944,79,93,'CDU_S', 'BTN'),
               Control(379,944,79,93,'CDU_T', 'BTN'),
               Control(461,944,79,93,'CDU_U', 'BTN'),
               Control(540,944,79,93,'CDU_V', 'BTN'),
               Control(620,944,79,93,'CDU_W', 'BTN'),
               Control(703,944,79,92,'CDU_X', 'BTN'),
               Control(188,944,93,98,'CDU_SLASH', 'BTN'),
               Control(2,944,93,98,'CDU_POINT', 'BTN'),
               Control(13,632,82,104,'CDU_1', 'BTN'),
               Control(102,632,82,104,'CDU_2', 'BTN'),
               Control(188,632,82,104,'CDU_3', 'BTN'),
               Control(14,736,82,104,'CDU_4', 'BTN'),
               Control(101,736,82,104,'CDU_5', 'BTN'),
               Control(188,736,82,104,'CDU_6', 'BTN'),
               Control(14,839,82,104,'CDU_7', 'BTN'),
               Control(99,839,82,104,'CDU_8', 'BTN'),
               Control(188,839,82,104,'CDU_9', 'BTN'),
               Control(99,944,82,104,'CDU_0', 'BTN'),
               Control(46,163,118,70,'CDU_LSK_3L', 'BTN'),
               Control(46,234,118,70,'CDU_LSK_5L', 'BTN'),
               Control(46,303,118,67,'CDU_LSK_7L', 'BTN'),
               Control(46,374,118,67,'CDU_LSK_9L', 'BTN'),
               Control(631,163,118,70,'CDU_LSK_3R', 'BTN'),
               Control(631,234,118,70,'vLSK_5R', 'BTN'),
               Control(631,303,118,67,'CDU_LSK_7R', 'BTN'),
               Control(631,374,118,67,'CDU_LSK_9R', 'BTN'),
               Control(316,1047,82,104,'CDU_BCK', 'BTN'),
               Control(402,1047,82,104,'CDU_SPC', 'BTN'),
               Control(485,1047,77,104,'CDU_Y', 'BTN'),
               Control(564,1047,77,104,'CDU_Z', 'BTN'),
               Control(656,1058,72,89,'CDU_+', 'BTN'),
               Control(656,1152,72,89,'CDU_-', 'BTN'),
               Control(566,1155,72,104,'CDU_FA', 'BTN'),
               Control(483,1153,80,91,'CDU_CLR', 'BTN'),
               Control(190,1153,80,91,'CDU_MK', 'BTN'),
               Control(65,1153,80,91,'CDU_PG-', 'BTN'),
               Control(65,1056,80,91,'CDU_PG+', 'BTN'),
               Control(717,1,82,75,'QUIT', 'BTN'),
               Control(284,1153,95,91,'SCROLL_L', 'BTN'),
               Control(379,1153,95,91,'SCROLL_R', 'BTN'),
               Control(1,1,82,75,'TOGGLE', 'BTN'),
               ]

arc210_controls = [
                Control(717,1,82,75,'QUIT', 'BTN'),
                Control(1,1,82,75,'TOGGLE', 'BTN'),

                Control(515,205,110,68,'ARC210_TRANS_REC_SEL', 'BTN'),
                Control(403,205,80,68,'ARC210_GPS', 'BTN'),
                Control(292,205,80,68,'ARC210_TOD_REC', 'BTN'),
                Control(143,207,80,68,'ARC210_TOD_SEND', 'BTN'),
                Control(40,345,97,68,'ARC210_FSK_UP', 'BTN'),
                Control(40,473,97,68,'ARC210_FSK_MID', 'BTN'),
                Control(40,604,97,68,'ARC210_FSK_LOW', 'BTN'),
                Control(8,694,61,94,'ARC210_BRIGHT_INC', 'BTN'),
                Control(10,827,57,80,'ARC210_BRIGHT_DEC', 'BTN'),
                Control(718,465,68,90,'ARC210_AMP_FREQ_MODUL', 'BTN'),
                Control(715,600,71,95,'ARC210_OFF_FREQ', 'BTN'),
                Control(611,600,71,95,'ARC210_TRANS_REC_FUNC', 'BTN'),
                Control(612,467,71,95,'ARC210_MENU', 'BTN'),
                Control(724,723,63,173,'ARC210_ENTER', 'BTN'),
                Control(91,752,88,104,'ARC210_100MHZ_SEL', 'ROT'),
                Control(222,752,92,104,'ARC210_10MHZ_SEL', 'ROT'),
                Control(354,752,85,104,'ARC210_1MHZ_SEL', 'ROT'),
                Control(488,752,85,104,'ARC210_100KHZ_SEL', 'ROT'),
                Control(617,744,85,104,'ARC210_25KHZ_SEL', 'ROT'),
                Control(345,897,101,117,'ARC210_CHN_KNB', 'ROT_3200'),

                Control(153,900,103,125,'ARC210_MASTER', 'SEL_8'),
                Control(543,892,103,125,'ARC210_SEC_SW', 'SEL_8'),
                Control(640,329,90,87,'ARC210_SQUELCH', 'SEL_2'),
               ]

# Initialization

print ('Waiting to connect...')

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(0)
s.bind(("0.0.0.0", 7779))

print ('Connected.  Opening outbound socket')

s_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_tx.settimeout(0)
s_tx.connect((CONNECTION["host"], 7778))

print('Connected.')

pygame.init()
pygame.mixer.init()

mode = "cdu"

size = width, height = 800, 1280
screen = pygame.display.set_mode(size, pygame.DOUBLEBUF , 32)
# | pygame.NOFRAME | pygame.FULLSCREEN  # Todo: put these back in for production

#Loading

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

cduFont = BitmapFontScreen(screen, 178, 117, (0, 255, 0), 1.0, 0)
#arc210Font = BitmapFontScreen(screen, 205, 365, (0, 0, 255), 1.15, 10)

# DCS-Bios Parser
parser = ProtocolParser()
parser.write_callbacks.add(parser_callback)

pygame.scrap.init()
#pixelRuler = PixelRuler(650,400,82,104)

clock = pygame.time.Clock()
looprate_max = 60 # Keep the loop fast to receive DCS data (45hz actual), but only display it at a fraction of that
display_divider = 4
display_counter = 0

print('Starting main loop')
running = True

while running == True:
    # Slow down the loop so we don't kill the CPU
    msThisFrame = clock.tick(looprate_max)
    #print('FPS:' + str(1000/msThisFrame))

    # PyGame event loop
    for event in pygame.event.get():
        #print(event.type)
        if event.type == pygame.QUIT:
            running = False
        elif( event.type == MOUSEMOTION ):
            #print( 'MOUSEMOTION' )
            if rotating_control is not None:
                if rotating_control.TYPE.startswith('SEL_'):
                    #print( 'Rotating brah' )
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
                elif( rotating_control.TYPE == 'ROT' ):
                    x,y = pygame.mouse.get_pos()
                    if( y-rotating_last_y > 50 ):
                        rotate_control(rotating_control, "DEC")
                        rotating_last_y = y
                    elif( y-rotating_last_y < -50 ):
                        rotate_control(rotating_control, "INC")
                        rotating_last_y = y
                elif( rotating_control.TYPE == 'ROT_3200' ):
                    x,y = pygame.mouse.get_pos()
                    if( y-rotating_last_y > 50 ):
                        rotate_control(rotating_control, "-3200")
                        rotating_last_y = y
                    elif( y-rotating_last_y < -50 ):
                        rotate_control(rotating_control, "+3200")
                        rotating_last_y = y
        elif( event.type == MOUSEBUTTONUP ):
            rotating_control = None
            #print( 'MOUSEBUTTONUP' )        
        elif( event.type == MOUSEBUTTONDOWN ):
            #print( 'MOUSEBUTTONDOWN' )
            pos = pygame.mouse.get_pos()
            x,y = pos
            activeControls = arc210_controls if mode == 'arc210' else cdu_controls
                        
            for ctl in activeControls:
                if( x >= ctl.X and x < (ctl.X+ctl.WIDTH) and y >= ctl.Y and (y < ctl.Y+ctl.HEIGHT) ):
                    if( ctl.TYPE == 'ROT' or ctl.TYPE == 'ROT_3200' ):
                        print('Start ROT: ' + ctl.PARAM)
                        rotating_control = ctl
                        rotating_last_y = y
                        click_sound.play()
                    elif( ctl.TYPE.startswith('SEL_') ):
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
            #arc210ScreenBuffer.drawTo(arc210Font)
            left_knob_image = pygame.transform.rotate(rotator_img, -arc210_leftknob_rotation)
            left_knob_width,left_knob_height = left_knob_image.get_size()
            screen.blit(left_knob_image, (206 - (left_knob_width/2),961 - (left_knob_height/2)))

            right_knob_image = pygame.transform.rotate(rotator_img, -arc210_rightknob_rotation)
            right_knob_width,right_knob_height = right_knob_image.get_size()
            screen.blit(right_knob_image, (594 - (right_knob_width/2),956 - (right_knob_height/2)))

            #print('Drawing squelch: ',arc210_squelch_on)
            squelch_knob_image = pygame.transform.flip(squelch_img, arc210_squelch_on, False)
            squelch_knob_width,squelch_knob_height = squelch_knob_image.get_size()
            screen.blit(squelch_knob_image, (684 - (squelch_knob_width/2),366 + 7 - (squelch_knob_height/2)))
            
        else:
            cduScreenBuffer.drawTo(cduFont)

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
