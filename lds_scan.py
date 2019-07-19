# Script to get LDS Data from Robot through serial port
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

# potentially make the serial port a parameter
def create_session():
    # need to call this command otherwise not permitted to make serial connection
    #subprocess.call(['sudo chmod 666 /dev/ttyACM0'],shell=True)
    #initialize the session
    s=serial.Serial('COM5',timeout=3)
    return s
def close_session(s):
    s.close()
class lds_scan:
    # desired degree of reading and already created session
    def start(self,s):
        # starts the LDS
        s.write(b'TestMode On\r\n')
        time.sleep(1)
        s.write(b'SetLDSRotation On\r\n')
        # how long does the LDS need to warm up?
        time.sleep(5)
    def full_scan(self,s):
        # returns a list(?) of the reading at all degrees
        s.reset_output_buffer()
        s.write(b'GetLDSScan\r\n')
        time.sleep(1)
        response=s.read(10000)
        response=response.decode("utf-8")
        all_degs=response.splitlines()
        return all_degs
    def deg_scan(self,s,deg:int):
        # returns the reading at a specified degree
        s.reset_output_buffer()
        s.write(b'GetLDSScan\r\n')
        time.sleep(1)
        response=s.read(10000)
        #response=response.decode("utf-8")
        all_degs=response.splitlines()
        for i in all_degs:
            # make sure the types get matched properly here
            print(i)
            if i[0]==str(deg):
                line=i.split(",")
                new_read=reading(line[0],line[1],line[2],line[3])
                return new_read
        return None
    def stop(self,s):
        s.write(b'SetLDSRotation Off\r\n')
        time.sleep(1)

if __name__=="__main__":
    s=serial.Serial('COM5',timeout=3)
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
                                                           
        
