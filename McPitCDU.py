import sys, pygame
from pygame.locals import *
from time import sleep
from collections import namedtuple

pygame.init()
pygame.mixer.init()
click_sound = pygame.mixer.Sound("click.wav")

size = width, height = 600, 1024

screen = pygame.display.set_mode(size, pygame.DOUBLEBUF, 32)

cdu_bg = pygame.image.load("cdu_bg.bmp")
cdu_bg = pygame.transform.scale(cdu_bg, (600,1024))
cdu_bg_rect = cdu_bg.get_rect()

CDUButton = namedtuple("CDUButton", "X Y WIDTH HEIGHT PARAM")
cdu_buttons = [CDUButton(18,502,55,90,'1'),
               CDUButton(78,502,55,90,'2'),
               CDUButton(145,502,55,90,'3')
               ]

while 1:
    #screen.fill(0,0,0)
    screen.blit(cdu_bg, (0,0))

    for btn in cdu_buttons:
        pygame.draw.rect(screen, (0,0,150),(btn.X,btn.Y,btn.WIDTH,btn.HEIGHT), 3)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        elif( event.type is MOUSEBUTTONDOWN ):
            pos = pygame.mouse.get_pos()
            x,y = pos
            for btn in cdu_buttons:
                if( x >= btn.X and x < (btn.X+btn.WIDTH) and y >= btn.Y and (y < btn.Y+btn.HEIGHT) ):
                    print(btn.PARAM)
                    click_sound.play()
                    pygame.draw.rect(screen, (150,150,150),(btn.X,btn.Y,btn.WIDTH,btn.HEIGHT), 3)
                        
        #elif(event.type is MOUSEBUTTONUP)
        
    pygame.display.flip()

    sleep(0.1)


