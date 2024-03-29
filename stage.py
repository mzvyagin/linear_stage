# Module to interact with the linear stage
# Max Zvyagin
import socket
import time

class stage:
    def __init__(self,conversion:int,offset:int):
        # this is the number of motor steps that is equal to 1 mm
        self.conversion=conversion
        # position value for the far end of the stage
        # this is for the 6m linear stage, change for another stage
        self.end_of_stage=conversion*(-5975-offset)
        # close end of the stage position = 0
        self.offset=offset
    # initializes the TCP connection
    def connect(self):
        m=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # these values won't change for the 6m linear stage but will be different for other instruments
        m.connect(("192.168.33.1",503))
        time.sleep(.1)
        #m.settimeout(15)
        return m
    def get_pos(self,m):
        # request and recieve position in motor steps, not millimeters
        m.send(b'PR P\r\n')
        try:
            r=m.recv(128)
            time.sleep(.1)
        except:
            print("pos exception")
            time.sleep(5)
            r=m.recv(128)
            time.sleep(.1)
        # r=r.encode("utf-8")
        l=r.splitlines()
        # return the last line of the response (in case there's other things in buffer)
        # convert string to a decimal number
        # remove this print statement once you know it's isolating the right value
        pos=int(l[-1],10)
        return pos
    def stage_pos(self,m):
        # returns the stage position in millimeters
        # offset calculated using laser tool is added to this position
        steps=self.get_pos(m)
        if steps==0:
            return self.offset
        else:
            real=steps/(self.conversion*-1)
            real=real+self.offset
            return round(real)
    # move the stage to an absolute position from home
    def move_ab(self,m,dist:int):
        # calculate the position:
        p=self.conversion*(dist-self.offset)*-1
        # need to check to make sure position isn't off the stage
        if p<=0 and p>=((self.end_of_stage-self.offset)*self.conversion):
            m.send(b'MA %d\r\n'%p)
            #pos=None
            #while pos!=p:
                #pos=self.get_pos(m)
                #time.sleep(1)
            return True
        else:
            print("Invalid position for absolute move")
            return False
    def move_rel(self,m,dist:int):
        # get the original position
        start=self.get_pos(m)
        # calculate the position to move
        p=self.conversion*(dist)*-1
        end=start+p
        # need to check to make sure final position isn't off the stage
        if end<=0 and end>=(-5975*self.conversion):
            m.send(b'MR %d\r\n'%p)
            #pos=None
            #while pos!=end:
                #pos=self.get_pos(m)
                #time.sleep(1)
            return True
        else:
            print("Invalid position for relative move")
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
        try:
            r=m.recv(128)
            time.sleep(.1)
        except:
            print("moving exception")
            time.sleep(5)
            r=m.recv(128)
            time.sleep(.1)
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
    
            

