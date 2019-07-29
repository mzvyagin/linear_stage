# Script/module to get LDS Data from Robot through serial port
# Max Zvyagin
import serial
import time
import subprocess

class reading:
    def __init__(self,deg,dist,inten,error):
        self.deg=deg
        self.dist=dist
        self.inten=inten
        self.error=error
# parameter for serial port so it can be edited from the GUI
# it's set automatically to what it was when the code was written
global serial_port
serial_port='COM5'

def create_session(s_port):
    # need to call this command otherwise not permitted to make serial connection - only on Linux
    #subprocess.call(['sudo chmod 666 /dev/ttyACM0'],shell=True)
    #initialize the session
    s=serial.Serial(s_port,timeout=3)
    return s
def close_session(s):
    s.close()
    return None
class lds():
    # this class relies on an already created session object (see above)
    def __init__(self,offset):
        self.offset=offset
    def start(self,s):
        # starts the LDS
        s.write(b'TestMode On\r\n')
        time.sleep(1)
        s.write(b'SetLDSRotation On\r\n')
        # how long does the LDS need to warm up? Does this matter?
        time.sleep(3)
    def full_scan(self,s):
        # returns a list of readings 
        response=s.reset_input_buffer()
        s.write(b'GetLDSScan\r\n')
        time.sleep(1)
        response=s.read(10000)
        response=response.decode("utf-8")
        results=[]
        all_degs=response.splitlines()
        # print(all_degs)
        # all_degs=all_degs[2:363]
        for i in all_degs:
            line=i.split(",")
            if line[0] != '' and line[0]>='0' and line[0]<='359': # if not empty string
                print(line)
                if len(line) > 1:
                    distance=int(line[1],10)
                    if distance==0:
                        distance==0
                    else:
                        distance=distance-self.offset
                    if line[2] != '':
                        l2=int(line[2])
                    if line[3] != '':
                        l3 = int(line[3])
                    new_read=[int(line[0]),distance,l2,l3]
                    results.append(new_read)
        return results
    def deg_scan(self,s,deg:int):
        # returns a list of readings 
        response=s.reset_input_buffer()
        s.write(b'GetLDSScan\r\n')
        time.sleep(1)
        response=s.read(10000)
        response=response.decode("utf-8")
        all_degs=response.splitlines()
        # print(all_degs)
        # all_degs=all_degs[2:363]
        for i in all_degs:
            line=i.split(",")
            if line[0] != '' and line[0]==str(deg):
                #print(line)
                if len(line) > 1:
                    distance=int(line[1],10)
                    if distance==0:
                        distance==0
                    else:
                        distance=distance-self.offset
                    if line[2] != '':
                        l2=int(line[2])
                    if line[3] != '':
                        l3 = int(line[3])
                    new_read=reading(int(line[0]), distance, l2, l3)
                    return new_read
        return None
    def stop(self,s):
        s.write(b'SetLDSRotation Off\r\n')
        time.sleep(1)

    # Returns 
    def bot_info(self,s):
        s.reset_input_buffer()
        s.write(b'GetVersion\r\n')
        time.sleep(1)
        response=s.read(10000)
        response=response.decode("utf-8")
        return response

if __name__=="__main__":
    s=serial.Serial(serial_port,timeout=3)
    s.write(b'TestMode On\r\n')
    time.sleep(1)
    #s.write(b'GetWifiStatus\r\n')
    #time.sleep(1)
    #response=s.read(100)
    #print(response.decode("utf-8"))
    s.write(b'SetLDSRotation On\r\n')
    time.sleep(5)
    s.write(b'GetLDSScan\r\n')
    time.sleep(1)
    response=s.read(10000)
    response=response.decode("utf-8")
    print(response)
    s.write(b'SetLDSRotation Off\r\n')
    time.sleep(1)
    s.reset_output_buffer()
    s.close()

    # isolate 0th degree data
    scan=response.split("GetLDSScan")
    scan=scan[-1]
    scan=scan.split("\n")
    for i in scan:
        # print(i)
        if i[0]=="0":
            # isolate values
            line=i.split(",")
            # store results in an object
            new_read=reading(line[0],line[1],line[2],line[3])
            # print(vars(new_read))
                                                           
        
