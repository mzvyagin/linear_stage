# Code to create GUI for the LDS testing interface for the linear stage
# Max Zvyagin, July 2019

from appJar import gui
import test # module with functions controlling testing
import stage
import lds

# set up of the gui
app=gui()
app.addLabel("title","LDS Testing on Linear Stage")
app.setLabelBg("title","green")

# universal variables to store conversion factor and offset (mm)
conv=2556.7
off=490
test_object=test.test(conv,off)
test_object.system_init()

# start the laser
app.addButton("Start LDS Laser",test_object.start_laser())
# stop the laser
app.addButton("Stop LDS Laser",test_object.stop_laser())

# widget to show the current position of the linear stage
app.addLabel("Current Stage Position")
#def update_pos():
  #  pos=test_object.stage.get_pos(test_object.motor)
 #   app.setLabel("Current Stage Position",pos)

# should update the position widget constantly
#app.registerEvent(update_pos)

# manual movement of the linear stage - absolute position
app.addLabelEntry("Move to absolute position:")
app.setEntryDefault("Move to absolute position:",0)
def manual_abs():
    abs_pos=app.getEntry("Move to absolute position:")
    abs_pos=int(abs_pos)
    test_object.stage.move_ab(test_object.motor,abs_pos)
app.addNamedButton("Go","absolute",manual_abs)

# manual movement of the linear stage - relative position
app.addLabelEntry("Move to relative position:")
app.setEntryDefault("Move to relative position:",0)
def manual_rel():
    abs_pos=app.getEntry("Move to relative position:")
    abs_pos=int(abs_pos)
    test_object.stage.move_rel(test_object.motor,abs_pos)
app.addNamedButton("Go","relative",manual_rel)

# sequence to quit the app
app.setStopFunction(test_object.quit())

# start the app
app.go()