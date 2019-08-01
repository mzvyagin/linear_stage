# Script/module to get LDS Data from Robot through serial port
# Max Zvyagin
import serial
import time
import subprocess
import numpy

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
    # timeout of 3 seconds
    s=serial.Serial(s_port,timeout=10)
    return s
def close_session(s):
    s.close()
    return None
class lds():
    # this class relies on an already created session object (see above)
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
        response=response.decode("utf-8",errors="ignore")
        #print(response)
        results=[]
        all_degs=response.splitlines()
        # print(all_degs)
        # all_degs=all_degs[2:363]
        for i in all_degs:
            line=i.split(",")
            if line[0] != '' and line[0].isnumeric()==True and int(line[0])>=0 and int(line[0])<=359:
                #print(line[0])
                if len(line) == 4:
                    distance=int(line[1])
                    if line[2] != None and line[2].isnumeric()==True:
                        l2=int(line[2])
                    else:
                        l2=None
                    if line[3] != None and line[3].isnumeric()==True:
                        l3 = int(line[3])
                    else:
                        l3=None
                    new_read=[int(line[0]),distance,l2,l3]
                    results.append(new_read)
                # sometimes the strings get messed up and index errors get thrown, need to restart the scan
                else:
                    return None

        return results
    def deg_scan(self,s,deg:int):
        # this call gets all degrees
        response=s.reset_input_buffer()
        s.write(b'GetLDSScan\r\n')
        time.sleep(1)
        response=s.read(10000)
        response=response.decode("utf-8",errors="ignore")
        all_degs=response.splitlines()
        for i in all_degs:
            line=i.split(",")
            if line[0] != '' and line[0].isnumeric() ==True and line[0]==str(deg):
                if len(line) > 1:
                    distance=int(line[1])
                    if line[2] != None and line[2].isnumeric()==True:
                        l2=int(line[2])
                    else:
                        l2=None
                    if line[3] != None and line[3].isnumeric()==True:
                        l3 = int(line[3])
                    else:
                        l3=None
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
        # need to parse for important information here as requested by Pawel
        # irrelevant data is removed
        a=response.split("LCD Panel,0,0,0,",1)
        b=a[1].split("Locale",1)
        chunk1=b[0]
        c=b[1].split("MAG_SENSOR_ORIG",1)
        d=c[1].split("NTP URL",1)
        chunk2=d[0]
        e=d[1].split("Software Git")
        e[1]="Software Git"+e[1]
        f=e[1].split("UI Name")
        chunk3=f[0]

        parsed_data=chunk1+chunk2+chunk3

        parsed_data=parsed_data.splitlines()

        return parsed_data

    def calculate_offset(self,s):
        # get a full scan packet
        scan=self.full_scan(s)
        # check the scan for success
        counter=0
        # try to scan ten times, should work the first time but this is a failsafe 
        while scan==None and counter<10:
            scan=self.full_scan(s)
            counter=counter+1
        
        if scan==None and counter>=10:
            return None

        # initialize lists
        x=[]
        y=[]

        # pull data from the first ten degrees of the list
        for i in range(0,11):
            entry=scan[i]
            #print(entry)
            # check error code and distance
            if entry[3] == 0 and 450 <= entry[1] <= 525:
                # append degree 
                x.append(i)
                # append distance
                y.append(entry[1])
                #print(entry[1])
            else:
                print("Degree %d lost because of error or distance not between 450 and 525"%i)

        # pull data from the last ten degrees of list
        deg=-10
        for i in range(350,360):
            entry=scan[i]
            #print(entry)
            # check error code and distance 
            if entry[3] == 0 and 450 <= entry[1] <= 525:
                # append degree 
                x.append(deg)
                # append distance
                y.append(entry[1])
                #print(entry[1])
            else:
                print("Degree %d lost because of error or distance not between 450 and 525"%deg)
            # always increase the degree number    
            deg=deg+1

        # calculate the quadratic fit using the x and y arrays 
        r=numpy.polynomial.polynomial.Polynomial.fit(x,y,2)
        # extract coefficients
        coeff=r.convert().coef

        m=(-1*coeff[1])/(2*coeff[2])

        #print(coeff)
        print("This is the calculated true zero degree using a quadratic fit:")
        print(m)

        return m





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
                                                           
        
