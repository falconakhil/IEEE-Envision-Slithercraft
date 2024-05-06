import pickle
import socket
import random
# from pygame import Rect
# import sys
# import threadijng

class PlayerState:
    def __init__(self,uid):
        self.segments_x=[]
        self.segments_y=[]
        self.score=0
        self.isAlive=True
        self.uid=uid


class Socket:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)
        self.socket.bind((self.ip,self.port))
        self.socket.listen(10)        
    

    def acceptNewClient(self):
        try:
            client,addr=self.socket.accept()
            client.setblocking(False)
            return client
        except:
            return None        

    def receiveData(self,client):
        try:
        # First, read the header (10 bytes)
            header = client.recv(10)
        # Decode the header to get the data length
            data_length = int(header.decode().strip())

        # Now, read the actual data
            data = b''
            while len(data) < data_length:
            # Read the remaining data
                chunk = client.recv(data_length - len(data))
                if chunk == b'':
                    raise RuntimeError("socket connection broken")
                data += chunk
        # Deserialize the data
            return pickle.loads(data)
        except:
            pass
        
    def send(self,client,data):
        serialized_data=pickle.dumps(data)
        data_length=len(serialized_data)
        try:
            client.send(f"{data_length:<10}".encode())
            sent=0
            while sent<data_length:
                sent=client.send(serialized_data)

        except:
            # raise RuntimeError("Failed to send data")
            pass

class GameServer:
    def __init__(self):
        self.sock=Socket('localhost',8000)
        self.players={}
        self.opponents={}
        self.orbs=[]
        self.uid_counter=0

        self.init_orbs(100)
        print("Listening on "+self.sock.ip+":"+str(self.sock.port))
        print("Press Ctrl+C to stop server")
        self.mainLoop()

    def init_orbs(self,number_of_orbs):
        for i in range(0,number_of_orbs):
            pos=(random.randint(-2400,2400),random.randint(-1600,1600))
            self.orbs.append(pos)
        
    def mainLoop(self):
        while True:
            newClient=self.sock.acceptNewClient()
            if newClient!=None:
                self.opponents[newClient]=list(self.players.values()).copy()
                self.players[newClient]=PlayerState(self.uid_counter)
                self.uid_counter+=1
                for client in self.players:
                    if client!=newClient:
                        self.opponents[client].append(self.players[newClient])
                self.sock.send(newClient,self.players[newClient])
            
            for client in self.players:
                flag=False
                data=self.sock.receiveData(client)
                while data !=None:
                    # req+=1
                    if isinstance(data,PlayerState):
                        self.players[client]=data
                    elif isinstance(data,str):
                        if data=="OPPONENTS":
                            opponents=[self.players[oppclient] for oppclient in self.players if oppclient!=client]
                            # print(self.opponents[client])
                            self.sock.send(client,opponents)
                        if data=="ORBS":
                            self.sock.send(client,self.orbs)
                        if data=="END":
                            self.players.pop(client)
                            flag=True
                            client.close()
                            break
                    elif isinstance(data,tuple):
                        for i in range(0,len(self.orbs)):
                            if self.orbs[i][0]==data[0] and self.orbs[i][1]==data[1]:
                                self.orbs.pop(i)
                                break
                        self.init_orbs(1)
                    data=self.sock.receiveData(client)

                if(flag):
                    break
                        
GameServer()