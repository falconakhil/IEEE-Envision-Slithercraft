import pygame
from pygame import Vector2 as v2
import sys
import threading
import socket
import pickle

class Socket:
    def __init__(self,ip,port):
        self.server=(ip,port)
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
    def send(self,data):
        serialized_data=pickle.dumps(data)
        data_length=len(serialized_data)    
        try:
            self.sock.sendall(f"{data_length:<10}".encode())
            self.sock.sendall(pickle.dumps(data))
        except:
            pass
        
    def reconnect(self):
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.connect(self.server)
        data=self.receive()
        return data.uid

    def receive(self):
        try:
        # First, read the header (10 bytes)
            header = self.sock.recv(10)
        # Decode the header to get the data length
            data_length = int(header.decode().strip())

        # Now, read the actual data
            data = b''
            while len(data) < data_length:
            # Read the remaining data
                chunk = self.sock.recv(data_length - len(data))
                if chunk == b'':
                    raise RuntimeError("socket connection broken")
                data += chunk

        # Deserialize the data
            return pickle.loads(data)
        except:
            pass

    def connect(self):
        self.sock.connect(self.server)
        data=self.receive()
        return data.uid
    
    def close(self):
        self.sock.setblocking(True)
        self.send("END")
        self.sock.close()

class PlayerState:
    def __init__(self,player):
        self.segments_x=[]
        self.segments_y=[]
        for seg in player.segments:
            self.segments_x.insert(0,seg.pos.x)
            self.segments_y.insert(0,seg.pos.y)
        self.score=player.score
        self.isAlive=player.isAlive
        self.uid=player.uid

class Segment:

    def __init__(self,pos,game):
        self.pos=pos #Position vector of top left corner
        self.game=game
        self.rect=pygame.Rect(float(pos.x),float(pos.y),30,30) #Pygame rect object

    #Draw the segment
    def draw(self,surface,trailing):
        self.rect = pygame.draw.circle(surface,(0,0,255) if trailing else (0,255,255) , self.game.camera.transformed_coords(self.pos), 15)

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
        self.uid=0
        self.game=game
        self.isAlive=True
        self.direction=v2(1,0)
        self.speed=20 # Speed in terms of update rate. Smaller => Faster
        self.segments=[]
        for i in range(0,121):
            self.segments.append(Segment(game.dimensions/2-i*v2(1,0),self.game))
    
    def draw(self):
        for index in range(len(self.segments)-1,-1,-1):
            self.segments[index].draw(self.game.window,index)

    def extend(self,segs):
        for i in range(0,segs):
            self.segments.append(Segment(v2(self.segments[-1].pos)-self.direction,self.game))

    def checkCollsison(self):
        for opp in self.game.opponents:
            for seg in opp.segments:
                if (v2(seg.pos)-v2(self.segments[0].pos)).length()<30:
                    return True

    def update(self):
        mouse_pos=v2(pygame.mouse.get_pos()) - self.segments[0].rect.center #Get mouse position relative to player
        body_vec=v2(self.segments[0].pos) - v2(self.segments[1].pos) #Get vector from head to body
        motion_angle=body_vec.angle_to(mouse_pos) #Get angle between body vector and mouse vector
        if mouse_pos!=v2(0,0):
                self.direction=self.direction.rotate(motion_angle/100 if abs(motion_angle)<180 else -motion_angle/100).normalize()
        else:
            self.direction=v2(0,0)

        self.segments=self.segments[:-1] #Remove last segment
        self.segments.insert(0,Segment(self.segments[0].pos+self.direction*1,self.game)) #Insert new segment at the front
        if self.checkCollsison():
            self.isAlive=False
            self.game.quit()

        self.game.socket.send(PlayerState(self))

class GameOver():
    def __init__(self,game):
        self.font=pygame.font.Font(None,100)
        self.pos=game.dimensions/2.0
        self.game=game
        self.color=(255,0,0)
        self.text_surface=self.font.render("Game Over !",True,self.color)
        self.text_rect=self.text_surface.get_rect(center=self.pos)
        # center_pos = (screen_rect.centerx - text_rect.width // 2, screen_rect.centery - text_rect.height // 2 + 36 * line)
    def draw(self):
        self.game.window.blit(self.text_surface,self.text_rect)
       
class Opponent:
    def __init__(self,playerState,game):
        self.score=playerState.score
        self.uid=playerState.uid
        self.game=game
        self.isAlive=playerState.isAlive
        self.segments=[]
        for (x,y) in zip(playerState.segments_x,playerState.segments_y):
            self.segments.insert(0,Segment(v2(x,y),self.game))
    
    def draw(self):
        for index in range(len(self.segments)-1,-1,-1):
            self.segments[index].draw(self.game.window,index)

class Score():
    def __init__(self,game):
        self.game=game
        self.font=pygame.font.Font(None,36)
        self.color=(0,0,0)
        self.playerColor=(255,0,0)
        self.pos=(1000,600)
        self.text=""
    
    def update(self):
        self.text=[self.font.render(f"Score:",True,self.color),self.font.render(f"{self.game.player.uid}:{self.game.player.score}",True,self.playerColor)]
        for opp in self.game.opponents:
            self.text.append(self.font.render(f"{opp.uid}{'' if opp.isAlive else '*'}:{opp.score}",True,self.color))
    
    def draw(self):
        surface=self.game.window
        for line in range(len(self.text)):
            surface.blit(self.text[line],self.pos+v2(0,36*line))

class Orb:
    def __init__(self,pos,game):
        self.color=(255,0,0)
        self.game=game
        self.pos=pos
        self.orb_size=game.orb_size
        self.rect=pygame.Rect(float(pos.x),float(pos.y),game.orb_size,game.orb_size)

    def draw(self):
        pos=self.game.camera.transformed_coords(self.pos)
        tempRect=pygame.Rect(float(pos.x),float(pos.y),self.orb_size,self.orb_size)
        pygame.draw.rect(self.game.window,self.color,tempRect)

    def update(self):
        if pygame.Rect.colliderect(self.rect,self.game.player.segments[0].rect):
            return True

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

        self.opponents=[]

        self.socket=Socket('localhost',8000)
        self.player.uid=self.socket.connect()

        self.camera=Camera(self)
            
        self.orbs=[]
        self.eaten=[]

        self.score=Score(self)

        self.stateUpdateThread=threading.Thread(target=self.generateOppOrbs,args=())
        self.stateUpdateThread.daemon=True
        self.stateUpdateThread.start()

        self.end=False

        self.mainloop()
                        
    def render(self):
        for orb in self.orbs:
            orb.draw()
        self.player.draw()
        for opp in self.opponents:
            opp.draw()
        self.score.draw()
        if self.end:
            self.gameOverText.draw()

    def update(self):
        if not self.end:
            self.player.update()
            self.camera.update()

        for orb in range(0,len(self.orbs)):
            if self.orbs[orb].update():
                self.player.score+=1
                self.player.extend(30)
                self.eaten.append(tuple(self.orbs[orb].pos))
                self.socket.send(tuple(self.orbs[orb].pos))
                self.orbs.pop(orb)
                print("Score:",self.player.score)
                break
        
        self.score.update()

    def generateOppOrbs(self):
        while True:
            data=self.socket.receive()
            if data!=[] and  data!=None:
                if isinstance(data[0],PlayerState):
                    self.opponents=[]
                    for state in data:
                        if state.uid!=self.player.uid:
                            self.opponents.append(Opponent(state,self))
                elif isinstance(data[0],tuple):
                    tmp=[]
                    allNew=True
                    for pos in data:
                        if pos not in self.eaten:
                            tmp.append(Orb(v2(pos),self))
                        else:
                            allNew=False
                    if tmp!=[]:        
                        self.orbs=tmp
                    if allNew: 
                        self.eaten=[]
        
    def quit(self):
        self.gameOverText=GameOver(self)
        self.end=True
      

    
    def mainloop(self):
        while True:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    self.quit()
                    self.socket.send('END')
                    pygame.quit()
                    sys.exit()
                elif event.type==self.PLAYER_UPDATE:
                    self.update()
            self.window.fill(self.bgcolor)
            self.render()
            pygame.display.update()
            self.clock.tick(60)


Game()