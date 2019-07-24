# Module to interact with the linear stage
# Max Zvyagin
import socket
import time

class stage:
    def __init__(self,conversion:int):
        # this is the number of steps that is equal to 1 mm
        self.conversion=conversion
        # position value for the far end of the stage
        # this is for the 6m linear stage, change for another stage
        self.end_of_stage=conversion*-6000
        # close end of the stage position = 0
    # initializes the TCP connection
    def connect(self):
        m=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        m.bind
        m.connect(("192.168.33.1",503))
        m.settimeout(3)
        return m
    def get_pos(self,m):
        # request and recieve position in motor steps, not millimeters
        m.send(b'PR P\r\n')
        r=m.recv(1024)
        # r=r.encode("utf-8")
        l=r.splitlines()
        # return the last line of the response (in case there's other things in buffer)
        # convert string to a decimal number
        # remove this print statement once you know it's isolating the right value
        pos=int(l[-1],10)
        # print(pos)
        return pos
    def stage_pos(self,m):
        # returns the stage position in millimeters
        steps=self.get_pos(m)
        if steps==0:
            return 0
        else:
            real=steps/(self.conversion*-1)
            return round(real)
    # move the stage to an absolute position from home
    def move_ab(self,m,dist:int):
        # calculate the position:
        p=self.conversion*dist*-1
        # need to check to make sure position isn't off the stage
        if p<=0 and p>=self.end_of_stage:
            m.send(b'MA %d\r\n'%p)
            #pos=None
            #while pos!=p:
                #pos=self.get_pos(m)
                #time.sleep(1)
            return True
        else:
            return False
    def move_rel(self,m,dist:int):
        # get the original position
        start=self.get_pos(m)
        # calculate the position to move
        p=self.conversion*dist*-1
        end=start+p
        # need to check to make sure final position isn't off the stage
        if end<=0 and end>=self.end_of_stage:
            m.send(b'MR %d\r\n'%p)
            #pos=None
            #while pos!=end:
                #pos=self.get_pos(m)
                #time.sleep(1)
            return True
        else:
            return False
    def get_echo(self,m):
        m.send(b'PR EM\r\n')
        #time.sleep(1)
        r=m.recv(1024)
        l=r.splitlines()
        echo=int(l[-1],10)
        return echo
    def get_maxvel(self,m):
        m.send(b'PR VM\r\n')
        #time.sleep(1)
        r=m.recv(1024)
        l=r.splitlines()
        vel=int(l[-1],10)
        return vel
    def get_moving(self,m):
        # gets the moving flag to see if stage is still moving
        m.send(b'PR MV\r\n')
        #time.sleep(.3)
        r=m.recv(1024)
        l=r.splitlines()
        moving=int(l[-1],10)
        return moving
    # this function doesn't work
    def set_echo(self,m,mode):
        m.send(b'EM=%d\r\n'%mode)
        check=self.get_echo(m)
        if check==mode:
            return True
        else:
            return None
    # doesn't work even when sending the commands through the shell, not a function issue, permissions??
    def set_maxvel(self,m,maxv):
        m.send(b'VM=%d\r\n'%maxv)
        check=self.get_maxvel(m)
        if check==maxv:
            return True
        else:
            return None
    # also doesn't work
    def set_pos(self,m,pos):
        m.send(b'P=%d\r\n'%pos)
        check=self.get_pos(m)
        if check==pos:
            return True
        else:
            return None
    # important to call every time to end the TCP connection
    def disconnect(self,m):
        m.shutdown('SHUT_RDWR')
        m.close()
    
            

