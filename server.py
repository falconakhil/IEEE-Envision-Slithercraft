import pickle
import socket
# import pygame
import sys
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
            raise RuntimeError("Failed to send data")

class GameServer:
    def __init__(self):
        self.sock=Socket('localhost',8000)
        self.players={}
        print("Listening on "+self.sock.ip+":"+str(self.sock.port))
        print("Press Ctrl+C to stop server")
        self.mainLoop()
        
    def mainLoop(self):
        while True:
            newClient=self.sock.acceptNewClient()
            if newClient!=None:
                self.players[newClient]=PlayerState(len(self.players))
                self.sock.send(newClient,self.players[newClient])
            
            for client in self.players:
                data=self.sock.receiveData(client)
                if data !=None:  
                    if isinstance(data,PlayerState):
                        self.players[client]=data
                        # print(data.segments_x[0],data.segments_y[0],data.segments_x[1],data.segments_y[1])
                    elif isinstance(data,str):
                        if data=="OPPONENTS":
                           opponents=[self.players[oppclient] for oppclient in self.players if oppclient!=client]
                           self.sock.send(client,opponents)
                        elif data=="END":
                            self.players.pop(client)
                            client.close()
                            break
                        
            
                # for others in self.players:  
                #     if others!=client:
                #         try:
                #             others.send(self.players[client])
                #         except:
    
    
                #             pass

GameServer()