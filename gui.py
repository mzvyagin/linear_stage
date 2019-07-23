# Code to create GUI for the LDS testing interface for the linear stage
# Max Zvyagin, July 2019

from appJar import gui
import test # module with functions controlling testing
import socket
import time

conv=2556.7
off=490
test_object=test.test(conv,off)
# set up of the gui
app=gui()
app.addLabel("title","LDS Testing on Linear Stage")
app.setLabelBg("title","green")
#app.setStartFunction(test_object.system_init)

# start the laser
app.addButton("Start LDS Laser",lambda:test_object.start_laser())
# stop the laser
app.addButton("Stop LDS Laser",lambda:test_object.stop_laser())

# widget to show the current position of the linear stage
app.addLabel("Current Stage Position","Current Stage Position")
def update_pos():
  pos= test_object.stage.stage_pos(test_object.motor)
  app.setLabel("Current Stage Position","Current Stage Position : "+str(pos)+" (mm)")

# should update the position widget constantly
app.registerEvent(update_pos)

# manual movement of the linear stage - absolute position
app.addLabelEntry("Move to absolute position (mm):")
app.setEntryDefault("Move to absolute position (mm):",0)
def manual_abs():
  abs_pos=app.getEntry("Move to absolute position (mm):")
  abs_pos=int(abs_pos)
  test_object.stage.move_ab(test_object.motor,abs_pos)
app.addNamedButton("Go","absolute",lambda:manual_abs())

# manual movement of the linear stage - relative position
app.addLabelEntry("Move to relative position (mm):")
app.setEntryDefault("Move to relative position (mm):",0)
def manual_rel():
  abs_pos=app.getEntry("Move to relative position (mm):")
  abs_pos=int(abs_pos)
  test_object.stage.move_rel(test_object.motor,abs_pos)
app.addNamedButton("Go","relative",lambda:manual_rel())

app.addLabel("Single Test Scan Results:")
app.addTable("Scan Results",[["Degree","Distance","Intensity","Error"]])
def test_scan():
  app.deleteAllTableRows("Scan Results")
  results=test_object.laser.full_scan(test_object.serial)
  app.addTableRows("Scan Results",results)
  
app.addButton("Test Laser Scan",lambda:test_scan())

# auto test functions
app.addButton("Auto Test",lambda:test_object.auto_test(0,1000,100,100,1))

# sequence to quit the app
app.setStopFunction(lambda:test_object.quit())

# start the app
app.go()