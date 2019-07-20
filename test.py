# Module to run testing of the LDS on the linear stage
import lds
import stage
import time

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
        # initialize stage object
        self.stage=stage.stage(self.conversion)
        # initialize connection to motor (TCP)
        self.motor=self.stage.connect()
        self.serial=lds.create_session()
        self.laser=lds.lds(self.offset)
        # start the laser spinning
        self.laser.start(self.serial)
        self.laser.full_scan(self.serial)

    def start_laser(self):
        self.laser.start(self.serial)
    def stop_laser(self):
        self.laser.stop(self.serial)

    # used to close connections and stop laser     
    def quit(self):
        # stop the laser
        self.stop_laser()
        # close serial connection
        self.serial.close()
        # close TCP connection
        self.stage.disconnect(self.motor)

    # automated test
    def auto_test(self,deg,A,B,step,readings):
        # error checking
        if A > 6000:
            print ("Error: A value is too large")
            return None
        if B < 0:
            print("Error: B value is too small")
        if step<=0 or step>6000:
            print("Error: invalid step value")
            return None
        if A < B:
            print("Error: A is smaller than B")
            return None
        if readings<1:
            print("Invalid number of readings at each interval")
            return None
        num_of_ints=(A-B)/step
        # check this one
        if num_of_ints.is_integer() is not True:
            print("Error: interval doesn't give an equal spacing")
            return None

        # initialize list of results
        results=[]
        count=0
        # starts at distance A
        self.stage.move_ab(self.motor,A)
        time.sleep(1)
        mflag=self.stage.get_moving(self.motor)
        # pause the program while the motor is still moving
        while mflag != 0:
            time.sleep(1)
            mflag=self.stage.get_moving(self.motor)
        p=self.stage.stage_pos(self.motor)
        # get a reading from the lds a specified number of times
        for i in range(0,readings):
            scan=self.laser.deg_scan(self.serial,deg)
            if scan==None:
                print("Error in LDS scan")
                return None
            else:
                data=test_result(scan.deg,scan.dist,scan.inten,scan.error,p)
                #print(vars(data))
                results.append(vars(data))
        count = count+1
        # move to new distance
        while count<=num_of_ints:
            self.stage.move_rel(self.motor,(step*-1))
            time.sleep(1)
            mflag=self.stage.get_moving(self.motor)
            # pause the program while the motor is still moving
            while mflag != 0:
                time.sleep(1)
                mflag=self.stage.get_moving(self.motor)
            p=self.stage.stage_pos(self.motor)
            # get a reading from the lds a specified number of times
            for i in range(0,readings):
                scan=self.laser.deg_scan(self.serial,deg)
                if scan==None:
                    print("Error in LDS scan")
                    return None
                else:
                    data=test_result(scan.deg,scan.dist,scan.inten,scan.error,p)
                    #print(vars(data))
                    results.append(vars(data))
            count=count+1
        # return the results
        return results
        



