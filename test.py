# Module to run testing of the LDS on the linear stage

import lds
from lds import serial_port
import stage
import time
import csv
from openpyxl import Workbook
import threading

lds_reads=[]
stage_reads=[]

e=threading.Event()

class trial_counter():
    def __init__(self,num):
        self.num=num

global z_run
# used to create a pointer which can be shared/updated between two different modules
z_run=trial_counter(0)

class test_result:
    def __init__(self,deg,dist,inten,error,act_dist):
        self.deg=deg
        self.dist=dist
        self.inten=inten
        self.error=error
        self.act_dist=act_dist


class test:
    def __init__(self,conversion:int,offset:int):
        self.conversion=conversion
        self.offset=offset
        self.stage=stage.stage(self.conversion,self.offset)
        time.sleep(1)
        # initialize connection to motor (TCP)
        self.motor=self.stage.connect()
        time.sleep(1)
        self.serial=lds.create_session(serial_port)
        time.sleep(1)
        self.laser=lds.lds()
        time.sleep(1)
        # start the laser spinning
        self.laser.start(self.serial)
        time.sleep(1)
        # do a full scan
        self.serial.write(b'GetLDSScan\r\n')
        time.sleep(1)
    


    def start_laser(self):
        self.laser.start(self.serial)
    def stop_laser(self):
        self.laser.stop(self.serial)

    # used to obtain all of the version information from the bot (serial command)
    def get_bot_info(self):
        r=self.laser.bot_info(self.serial)
        return r

    # used to close connections and stop laser     
    def quit(self):
        # move to home
        self.home()
        # stop the laser
        self.stop_laser()
        # close serial connection
        try:
            self.serial.close()
        # close TCP connection
        except:
            pass
        try:
            self.stage.disconnect(self.motor)
        except:
            pass
        return True


    def home(self):
        self.stage.move_ab(self.motor,self.offset)
        time.sleep(1)
        mflag=self.stage.get_moving(self.motor)
        # pause the program while the motor is still moving
        while mflag != 0:
            time.sleep(1)
            mflag=self.stage.get_moving(self.motor)

    def convert_to_excel(self,results,file_name):
        wb=Workbook()
        j=1
        # might not need this once the information gets properly parsed
        bot_ver=self.get_bot_info()
        p=''
        for i in bot_ver:
            if i.isprintable():
                p=p+i
        p=p.split(",")
        for x in p:
            wb.active.append([x])
        for i in results:
            ws=wb.create_sheet("Trial "+str(j))
            for x in i:
                ws.append(x)
            ws.append([])
            ws.append([])
            j=j+1
        if file_name==None:
            file_name='test_results'
        name=file_name+'.xlsx'
        wb.save(filename=name)   
    
    # this has been deprecated, now using excel to output the data 
    def convert_to_csv(self,results,file_name):
        if file_name==None:
            file_name='test_results.csv'
        else:
            file_name=file_name+'.csv'
        with open(file_name,mode='w',newline='') as test_results:
            results_writer=csv.writer(test_results,delimiter=',',quotechar='"')
            for i in results:
                results_writer.writerow(i)
            test_results.close()

    # automated test
    def auto_test(self,deg,A,B,step,readings,runs,file_name):
        global latest_lds_read
        global latest_stage_read
        global lds_reads
        global stage_reads
        global z_run
        #lds_reads=[]
        #stage_reads=[]
        # error checking
        if deg>359 or deg<0:
            print("Error:invalid degree parameter")
            return None
        if A < self.offset:
            print ("Error: A value is too small")
            return None
        if B > self.stage.end_of_stage:
            print("Error: B value is too large")
        if step<=self.offset or step>self.stage.end_of_stage:
            print("Error: invalid step value")
            return None
        if B < A:
            print("Error: B is smaller than A")
            return None
        if readings<1:
            print("Invalid number of readings at each interval")
            return None
        if runs<1:
            print("Invalid number of runs")
            return None
        num_of_ints=(B-A)/step
        # check this one
        if num_of_ints.is_integer() is not True:
            print("Error: interval doesn't give an equal spacing")
            return None

        # counter for number of runs
        full_results=[]
        z_run.num=1
        while z_run.num<=runs:
            # initialize list of results
            # used for a list of test_result class
            # results=[]
            # used for a string of results
            lds_reads.clear()
            stage_reads.clear()
            results_list=[['Degree','Actual Distance','Laser Distance','Intensity','Error',]]
            count=0
            # starts at distance A
            if e.isSet() == False:
                self.stage.move_ab(self.motor,A)
                time.sleep(1)
                mflag=self.stage.get_moving(self.motor)
                # pause the program while the motor is still moving
                while mflag != 0:
                    time.sleep(1)
                    mflag=self.stage.get_moving(self.motor)
                p=self.stage.stage_pos(self.motor)
            else:
                return
            # get a reading from the lds a specified number of times
            if e.isSet()==False:
                for i in range(0,readings):
                    scan=self.laser.deg_scan(self.serial,deg)
                    if scan==None:
                        print("Error in LDS scan")
                        return None
                    else:
                        #data=test_result(scan.deg,scan.dist,scan.inten,scan.error,p)
                        data_list=[scan.deg,p,scan.dist,scan.inten,scan.error]
                        latest_lds_read=str(scan.dist)
                        latest_stage_read=str(p)
                        lds_reads.append(float(scan.dist))
                        stage_reads.append(float(p))
                        #print(vars(data))
                        #results.append(data)
                        results_list.append(data_list)
                count = count+1
            else:
                return
            # move to new distance
            while count<=num_of_ints and e.isSet()==False:
                if e.isSet()==True:
                    return
                self.stage.move_rel(self.motor,step)
                time.sleep(1)
                mflag=self.stage.get_moving(self.motor)
                # pause the program while the motor is still moving
                while mflag != 0:
                    time.sleep(1)
                    mflag=self.stage.get_moving(self.motor)
                p=self.stage.stage_pos(self.motor)
                # get a reading from the lds a specified number of times
                if e.isSet()==False:
                    for i in range(0,readings):
                        if e.isSet()==False:
                            scan=self.laser.deg_scan(self.serial,deg)
                            if scan==None:
                                print("Error in LDS scan")
                                return None
                            else:
                                #data=test_result(scan.deg,scan.dist,scan.inten,scan.error,p)
                                data_list=[scan.deg,p,scan.dist,scan.inten,scan.error]
                                latest_lds_read=str(scan.dist)
                                latest_stage_read=str(p)
                                #print(latest_lds_read)
                                #print(latest_stage_read)
                                lds_reads.append(float(scan.dist))
                                stage_reads.append(float(p))
                                #results.append(data)
                                results_list.append(data_list)
                        else:
                            return
                    count=count+1
                else:
                    return
            
            # return the results
            #name=file_name+'_trial'+str(z_run.num)
            #self.convert_to_csv(results_list,name)
            #return results

            z_run.num=z_run.num+1
            full_results.append(results_list)
       
        # reset the counter at the end of the trials
        z_run.num=0
        self.convert_to_excel(full_results,file_name)


        



