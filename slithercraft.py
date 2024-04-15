import pygame
from pygame import Vector2 as v2
import sys
import random

class Player:
    def __init__(self):
        self.score=0

class Orb:
    def __init__(self,pos,size):
        self.velocity=0
        self.color=(255,0,0)
        self.rect=pygame.Rect(int(pos.x),int(pos.y),size,size)

    def draw(self,game):
        # pygame.draw.rect(surface,(255,0,0),rect)
        
        pygame.draw.rect(game.window,self.color,self.rect)

class Game:
    def __init__(self): 
        self.dimensions=v2(1200,800)
        self.orb_size=40

        pygame.init()
        self.window=pygame.display.set_mode((self.dimensions.x,self.dimensions.y))
        self.clock=pygame.time.Clock()
        self.orbs=[]
        self.init_orbs()
        self.mainloop()

    def init_orbs(self):
        while len(self.orbs)<2:
            pos=v2(random.randint(0,self.dimensions.x-self.orb_size),random.randint(0,self.dimensions.y-self.orb_size))
            self.orbs.append(Orb(pos,self.orb_size))
            for index1,orb1 in enumerate(self.orbs):
                for index2,orb2 in enumerate(self.orbs):
                    if pygame.Rect.colliderect(orb1.rect,orb2.rect) and index1!=index2:
                        print("Removing ")
                        self.orbs.pop(index1)
                        

    def render(self):
        for orb in self.orbs:
            orb.draw(self)
    
    def mainloop(self):
        while True:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.clock.tick(60)
            self.window.fill((104, 175, 232))
            self.render()
            pygame.display.update()

Game()