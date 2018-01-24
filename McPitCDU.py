import sys, pygame
from pygame.locals import *
from time import sleep
from collections import namedtuple

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
    
pygame.init()
pygame.mixer.init()

click_sound = pygame.mixer.Sound("click.wav")

size = width, height = 800, 1280

screen = pygame.display.set_mode(size, pygame.DOUBLEBUF, 32)

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
