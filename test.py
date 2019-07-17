# Script to start interacting with LDS through robot serial port
# Max Zvyagin
import serial
import time
import argparser

class degree_result:
    def __init__(self,deg,dist,inten,error):
        self.deg=deg
        self.dist=dist
        self.inten=inten
        self.error=error


if __name__=="__main__":
    s=serial.Serial('/dev/ttyACM0',timeout=3)
    s.write(b'TestMode On\r\n')
    time.sleep(1)
    s.write(b'GetWifiStatus\r\n')
    time.sleep(1)
    #response=s.read(100)
    #print(response.decode("utf-8"))
    s.write(b'SetLDSRotation On\r\n')
    time.sleep(5)
    s.write(b'GetLDSScan\r\n')
    time.sleep(1)
    response=s.read(6000)
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
    # match a degree paramater - implement this with argparser
    for i in scan:
        if i[0]="0"
        line=i,split(",")
        # implement a way to store the data in different fields: create a class?
        
