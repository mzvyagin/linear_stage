# Script to start interacting with LDS through robot serial port
# Max Zvyagin
import serial
import time

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
    print(response.decode("utf-8"))
    s.write(b'SetLDSRotation Off\r\n')
    time.sleep(1)
    s.close()
