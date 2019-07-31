import test
import time

t=test.test(2556.7,493)
time.sleep(1)
while True:
    localtime = time.asctime(time.localtime(time.time()))
    print("Local current time : " + str(localtime))
    position=t.stage.stage_pos(t.motor)
    print("Position : " + str(position))