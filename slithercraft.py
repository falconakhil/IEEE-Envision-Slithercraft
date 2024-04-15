import pygame
from pygame import Vector2 as v2
import sys
import random

class Segment:
    def __init__(self,pos):
        self.pos=pos #Position vector of top left corner
        self.width=1
        self.height=40
        self.rect=pygame.Rect(int(pos.x),int(pos.y),self.width,self.height) #Pygame rect object

    # def update(self):
    #     print()

    #Draw the segment
    def draw(self,surface):
        pygame.draw.rect(surface,(0,0,255),self.rect)

class Camera:
    def __init__(self,game):
        self.game=game #Reference to the game object from where it is called
        self.pos=game.player.segments[0].pos
    
    #Sets camera position to player position
    def update(self):
        self.pos=self.game.player.segments[0].pos

    #Transforms coordinates to camera coordinates
    def transformed_coords(self,coords):
        # return coords - self.pos + (self.game.dimensions)/2 - (self.game.player.segments[0].pos)/2
        return coords - (self.pos - (self.game.dimensions)/2)

class Player:
    def __init__(self,game):
        self.score=0
        self.speed=1
        self.game=game
        self.segments=[]
        for i in range(0,121):
            self.segments.append(Segment(game.dimensions/2-i*v2(1,0)))
    
    def draw(self):
        for segment in self.segments:
            segment.draw(self.game.window)

    def update(self):
        mouse_pos=v2(pygame.mouse.get_pos()) - self.segments[0].rect.center #Get mouse position relative to player
        if mouse_pos!=v2(0,0):
            direction=mouse_pos.normalize()
        else:
            direction=v2(0,0)
        self.segments=self.segments[:-1] #Remove last segment
        self.segments.insert(0,Segment(self.segments[0].pos+direction*self.speed)) #Insert new segment at the front
        


class Orb:
    def __init__(self,pos,game):
        self.velocity=0
        self.color=(255,0,0)
        self.game=game
        pos=game.camera.transformed_coords(pos)
        self.rect=pygame.Rect(int(pos.x),int(pos.y),game.orb_size,game.orb_size)

    def draw(self):
        pygame.draw.rect(self.game.window,self.color,self.rect)

    def update(self):
        if pygame.Rect.colliderect(self.rect,self.game.player.segments[0].rect):
            return True
        self.rect.topleft=self.game.camera.transformed_coords(self.rect.topleft)

class Game:
    def __init__(self): 
        self.dimensions=v2(1200,800)
        self.orb_size=40

        pygame.init()
        self.SCREEN_UPDATE=pygame.USEREVENT
        pygame.time.set_timer(self.SCREEN_UPDATE,20)
        self.window=pygame.display.set_mode((self.dimensions.x,self.dimensions.y))
        self.clock=pygame.time.Clock()
        self.player=Player(self)
        self.camera=Camera(self)
        self.orbs=[]
        self.init_orbs()
        self.mainloop()

    def init_orbs(self):
        while len(self.orbs)<2:
            pos=v2(random.randint(0,self.dimensions.x-self.orb_size),random.randint(0,self.dimensions.y-self.orb_size))
            self.orbs.append(Orb(pos,self))
            for index1,orb1 in enumerate(self.orbs):
                for index2,orb2 in enumerate(self.orbs):
                    if pygame.Rect.colliderect(orb1.rect,orb2.rect) and index1!=index2:
                        self.orbs.pop(index1)
                        

    def render(self):
        for orb in self.orbs:
            orb.draw()
        self.player.draw()

    def update(self):
        self.player.update()
        self.camera.update()

        for seg in self.player.segments:
            seg.pos=self.camera.transformed_coords(seg.pos)
            seg.rect.topleft=seg.pos

        for orb in self.orbs:
            if orb.update():
                self.orbs.remove(orb)
                self.player.score+=1
                print(self.player.score)
                # self.orbs.append(Orb(pos,self))
    
    def mainloop(self):
        while True:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type==self.SCREEN_UPDATE:
                    self.update()
            self.clock.tick(60)
            self.window.fill((104, 175, 232))
            self.render()
            pygame.display.update()

Game()