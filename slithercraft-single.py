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

    #Draw the segment
    def draw(self,surface,trailing):
        # pygame.draw.rect(surface,(0,0,255),self.rect)
        self.rect = pygame.draw.circle(surface,(0,0,255) if trailing else (0,255,255) , self.pos, 15)

class Camera:
    def __init__(self,game):
        self.game=game #Reference to the game object from where it is called
        self.pos=game.player.segments[0].pos
    
    #Sets camera position to player position
    def update(self):
        self.pos=self.game.player.segments[0].pos

    #Transforms coordinates to camera coordinates
    def transformed_coords(self,coords):
        return coords - (self.pos - (self.game.dimensions)/2)

class Player:
    def __init__(self,game):
        self.score=0
        self.game=game
        self.speed=14 # Speed in terms of update rate. Smaller => Faster
        self.segments=[]
        for i in range(0,121):
            self.segments.append(Segment(game.dimensions/2-i*v2(1,0)))
    
    def draw(self):
        for index in range(len(self.segments)-1,-1,-1):
            self.segments[index].draw(self.game.window,index)

    def update(self):
        mouse_pos=v2(pygame.mouse.get_pos()) - self.segments[0].rect.center #Get mouse position relative to player
        if mouse_pos!=v2(0,0):
            direction=mouse_pos.normalize()
        else:
            direction=v2(0,0)

        self.segments=self.segments[:-1] #Remove last segment
        self.segments.insert(0,Segment(self.segments[0].pos+direction*1)) #Insert new segment at the front

class Orb:
    def __init__(self,pos,game):
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
        self.bgcolor=(104, 175, 232)
        self.orb_size=40
        self.number_of_orbs=5

        pygame.init()

        self.window=pygame.display.set_mode((self.dimensions.x,self.dimensions.y))

        self.clock=pygame.time.Clock()
        
        self.player=Player(self)
        self.PLAYER_UPDATE=pygame.USEREVENT
        pygame.time.set_timer(self.PLAYER_UPDATE,self.player.speed)

        self.camera=Camera(self)
        
        self.orbs=[]
        self.init_orbs(self.number_of_orbs)

        self.mainloop()

    def init_orbs(self,number_of_orbs):
        for i in range(0,number_of_orbs):
            pos=v2(random.randint(0,self.dimensions.x-self.orb_size),random.randint(0,self.dimensions.y-self.orb_size))
            self.orbs.append(Orb(pos,self))

            #Check for overlapping orbs
            for index1,orb1 in enumerate(self.orbs):
                for index2,orb2 in enumerate(self.orbs):
                    if pygame.Rect.colliderect(orb1.rect,orb2.rect) and index1!=index2:
                        self.orbs.pop(index1)
                        self.init_orbs(1)

            #Check for overlapping orbs with player
            for orb in self.orbs:
                for seg in self.player.segments:
                    if pygame.Rect.colliderect(orb.rect,seg.rect):
                        self.orbs.remove(orb)
                        self.init_orbs(1)
                        
    def render(self):
        for orb in self.orbs:
            orb.draw()
        self.player.draw()

    def update(self):
        self.player.update()
        self.camera.update()

        for seg in self.player.segments:
            seg.pos=self.camera.transformed_coords(seg.pos)

        for orb in self.orbs:
            if orb.update():
                self.orbs.remove(orb)
                self.init_orbs(1)
                self.player.score+=1
                print("Score:",self.player.score)
    
    def mainloop(self):
        while True:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type==self.PLAYER_UPDATE:
                    self.update()
            self.clock.tick(60)
            self.window.fill(self.bgcolor)
            self.render()
            pygame.display.update()

Game()