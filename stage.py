# module to interact with the linear stage 
import socket
import time

class stage:
    def __init__(self,conversion:int):
        # this is the number of steps that is equal to 1 mm
        self.conversion=conversion
    # initializes the TCP connection
    def connect(self):
        m=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        m.connect(("192.168.33.1",503))
        return m
    def get_pos(self,m):
        # request and recieve position
        m.send(b'PR P\r\n')
        r=m.recv(1024)
        # r=r.encode("utf-8")
        l=r.splitlines()
        # return the last line of the response (in case there's other things in buffer)
        # convert string to a decimal number
        # remove this print statement once you know it's isolating the right value
        pos=int(l[-1],10)
        print(pos)
        return pos
    # move the stage to an absolute position from home
    def move_ab(self,m,dist):
        # calculate the position:
        p=self.conversion*dist*-1
        m.send(b'MA %d\r\n'%p)
        pos=None
        while pos!=p:
            # doesn't let you do anything while it's still moving the stage
            #time.sleep(3)
            pos=self.get_pos(m)
        print(pos)
        return pos
    def move_rel(self,m,dist):
        # get the original position
        start=self.get_pos(m)
        # calculate the position to move
        p=self.conversion*dist*-1
        end=start-p
        m.send(b'MR %d\r\n'%p)
        pos=None
        while pos!=end:
            # doesn't let you do anything while it's still moving the stage
            pos=self.get_pos(m)
        print(pos)
        return pos
quit
            

