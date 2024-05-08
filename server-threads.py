import pickle
import socket
import random
import threading

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
        self.socket.bind((self.ip,self.port))
        self.socket.listen(10)        
    

    def acceptNewClient(self):
        try:
            client,addr=self.socket.accept()
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
            client.sendall(f"{data_length:<10}".encode())
            client.sendall(serialized_data)

        except:
            pass

class GameServer:
    def __init__(self):
        self.sock=Socket('localhost',8000)
        self.players={}
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

    def broadcast(self,data):
        players=self.players.copy()
        for client in players:
            self.sock.send(client,data)
    
    def acceptNewPlayer(self):
        while True:
            newClient=self.sock.acceptNewClient()
            if newClient!=None:
                state=PlayerState(self.uid_counter)
                self.uid_counter+=1
                self.sock.send(newClient,state)
                self.players[newClient]=state
                t=threading.Thread(target=self.handlerThread,args=(newClient,))
                t.daemon=True
                t.start()

    def broadcasterThread(self):
        while True:
            self.broadcast(list(self.players.values()))
            self.broadcast(self.orbs)
            
    def handlerThread(self,client):
        while True:
            data=self.sock.receiveData(client)
            if isinstance(data,PlayerState):
                self.players[client]=data
            elif isinstance(data,str):
                if data=="END":
                    self.players.pop(client)
                    client.close()
                    break
            elif isinstance(data,tuple):
                for i in range(0,len(self.orbs)):
                    if self.orbs[i][0]==data[0] and self.orbs[i][1]==data[1]:
                        self.orbs.pop(i)
                        break
            
        
    def mainLoop(self):
            accepterThread=threading.Thread(target=self.acceptNewPlayer,args=())
            accepterThread.daemon=True
            accepterThread.start()
            broadcasterThread=threading.Thread(target=self.broadcasterThread,args=())
            broadcasterThread.daemon=True
            broadcasterThread.start()
            while True:
                pass
                 
GameServer()