# Code to create GUI for the LDS testing interface for the linear stage
# Max Zvyagin, July 2019

from appJar import gui
import test # module with functions controlling testing
import socket
import time
import threading
import multiprocessing
import os

# set up of the gui
#app=gui(useTtk=True)
app=gui()
app.setLocation("CENTER")


conv=2556.7
off=485
test_object=test.test(conv,off)

app.setTitle("LDS Testing on 6 Meter Linear Stage")
#app.setTtkTheme("equilux")
#app.ttkStyle.configure("TLabel",font=20)
#app.ttkStyle.configure("TButton",font=20)

app.addLabel("params","Input Parameters for the System")
app.addLabelNumericEntry("Conversion (default is 2556.7): ")
app.addLabelNumericEntry("Offset (default is 485): ")

def sys_params():
  global test_object
  global conv
  conv=app.getEntry("Conversion (default is 2556.7): ")
  if conv!=None:
    test_object.conversion=conv
    test_object.stage.conversion=conv
    print(test_object.conversion)
  global off
  off=app.getEntry("Offset (default is 485): ")
  if off!=None:
    test_object.offset=off
    test_object.laser.offset=off
    print(test_object.offset)
  

app.addButton("Update Parameters",lambda:sys_params())

# manual side of the interface
app.startFrame("LEFT",row=0,column=0)
app.setPadding(15,15)

# start the laser
app.addButton("Start LDS Laser",lambda:test_object.start_laser())
# stop the laser
app.addButton("Stop LDS Laser",lambda:test_object.stop_laser())

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
  # clear out the last trial
  app.deleteAllTableRows("Scan Results")
  # perform the scan and parsing
  results=test_object.laser.full_scan(test_object.serial)
  # add the results to the table
  app.addTableRows("Scan Results",results)

app.addButton("Test Laser Scan",lambda:test_scan())

app.stopFrame()

# automated side of the interface
app.startFrame("RIGHT",row=0,column=1)
app.setPadding(15,15)

# auto test functionality
app.addLabelEntry("Desired Degree: ",row=1)
app.addLabelEntry("Starting Distance A: ",row=2)
app.addLabelEntry("Ending Distance B: ",row=3)
app.addLabelEntry("Step Interval: ",row=4)
app.addLabelEntry("Readings per Interval: ",row=5)
app.addLabelEntry("Custom File Name: ",row=6)
def gui_auto_test():
  d=int(app.getEntry("Desired Degree: "))
  a=int(app.getEntry("Starting Distance A: "))
  b=int(app.getEntry("Ending Distance B: "))
  s=int(app.getEntry("Step Interval: "))
  r=int(app.getEntry("Readings per Interval: "))
  f=app.getEntry("Custom File Name: ")
  if f=="":
    f=None
  t=threading.Thread(target=test_object.auto_test,args=(d,a,b,s,r,f,))
  t.start()
  #t.join()
  app.destroySubWindow("Auto Test Running")
  return

def auto_test_wrapper():
  app.startSubWindow("Auto Test Running",modal=False)
  app.addLabel("The auto test is currently running. To stop the test please close this window then exit the program. Note that this will result in loss of test data.")
  app.stopSubWindow()
  app.showSubWindow("Auto Test Running")
  time.sleep(1)
  try:
    app.thread(gui_auto_test)
  except:
    app.destroySubWindow("Auto Test Running")
  time.sleep(1)

app.addButton("Auto Test",lambda:auto_test_wrapper(),row=7)

def open_csv():
  most_recent_test=app.getEntry("Custom File Name: ")
  if most_recent_test=='':
    most_recent_test='test_results.csv'
  else:
    most_recent_test=most_recent_test+'.csv'
  os.startfile(most_recent_test)

app.addButton("Open Most Recent Test Results",lambda:open_csv(),row=8)

# widget to show the current position of the linear stage
app.addLabel("Current Stage Position","Current Stage Position",row=0,column=0)
def update_pos():
  try:
    pos= test_object.stage.stage_pos(test_object.motor)
    app.setLabel("Current Stage Position","Current Stage Position : "+str(pos)+" (mm)")
  except:
    pass

# should update the position widget constantly
app.registerEvent(update_pos)

app.stopFrame()
# sequence to quit the app
app.setStopFunction(lambda:test_object.quit())

# start the app
app.go()