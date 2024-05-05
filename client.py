import socket
import pickle

class PlayerState():
    def __init__(self):
        self. name='test'
        self.length=5
        

sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(('localhost',8000))
sock.send(pickle.dumps(PlayerState()))
while True:
    continue
