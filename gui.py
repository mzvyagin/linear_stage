# Code to create GUI for the LDS testing interface for the linear stage
# Max Zvyagin, July 2019

from appJar import gui
import test # module with functions controlling testing
from test import e, lds_reads, stage_reads
import stage
import lds
import socket
import time
import threading
from multiprocessing import Process, Pipe
from multiprocessing.managers import BaseManager
import os
import ttkthemes

global e
global lds_reads
global stage_reads

conv=2556.7
off=485
test_object=test.test(conv,off)

global most_recent_test

# set up of the gui
# if not using ttk themes, just use app=gui()
app=gui(useTtk=True)
app.setLocation("CENTER")
app.setStretch("both")
app.setSticky("nesw")

app.setTitle("LDS Testing on 6 Meter Linear Stage")

# this theme can be configured using any of the options found on the site, entirely optional, comment out if desired
app.setTtkTheme("arc")
app.ttkStyle.configure("TLabel",font=20)
app.ttkStyle.configure("TButton",font=20)

app.addLabel("params","Input Parameters for the System")
app.addLabelNumericEntry("Conversion (default is 2556.7): ")
app.addLabelNumericEntry("Offset (default is 485): ")
app.addLabelEntry("COM Port: ")

def sys_params():
  global test_object
  global conv
  conv=app.getEntry("Conversion (default is 2556.7): ")
  # None is used here because this is numeric entry
  if conv!=None:
    test_object.conversion=conv
    test_object.stage.conversion=conv
    #print(test_object.conversion)
  global off
  off=app.getEntry("Offset (default is 485): ")
  # None is used here because this is numeric entry
  if off!=None:
    test_object.offset=off
    test_object.laser.offset=off
    #print(test_object.offset)
  global com
  com=app.getEntry("COM Port: ")
  # "" is used here because this is a general entry
  if com!="":
    print("COM Changed")
    test_object.stop_laser()
    test_object.serial.close()
    test_object.serial=lds.create_session(com)
    test_object.laser.start(test_object.serial)
  

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

app.startSubWindow("Robot Version Info")
app.setStretch("both")
app.setSticky("nesw")
app.addScrolledTextArea("Version",colspan=10,rowspan=10)
app.stopSubWindow()
bot=test_object.get_bot_info()
app.setTextArea("Version",bot)
app.hideSubWindow("Robot Version Info")

# a button used to get a pop-up with all of the version information for the robot
def print_bot_info():
  app.showSubWindow("Robot Version Info")
app.addButton("Get Robot Version Info",lambda:print_bot_info())

app.stopFrame()

# automated side of the interface
app.startFrame("CENTER",row=0,column=1)
app.setPadding(15,15)

# auto test functionality
app.addLabelEntry("Desired Degree: ",row=1)
app.addLabelEntry("Starting Distance A: ",row=2,rowspan=1)
app.addLabelEntry("Ending Distance B: ",row=3)
app.addLabelEntry("Step Interval: ",row=4)
app.addLabelEntry("Readings per Interval: ",row=5)
app.addLabelEntry("Custom File Name: ",row=6)
def gui_auto_test():
  global test_object
  global most_recent_test
  global lds_reads
  global stage_reads
  lds_reads.clear()
  stage_reads.clear()
  d=int(app.getEntry("Desired Degree: "))
  a=int(app.getEntry("Starting Distance A: "))
  b=int(app.getEntry("Ending Distance B: "))
  s=int(app.getEntry("Step Interval: "))
  r=int(app.getEntry("Readings per Interval: "))
  f=app.getEntry("Custom File Name: ")
  most_recent_test=f+'.csv'
  if f=="":
    f=None
    most_recent_test='test_results.csv'
  #test_object.auto_test(d,a,b,s,r,f)
  t=threading.Thread(target=test_object.auto_test,args=(d,a,b,s,r,f,),daemon=True)
  t.start()
  t.join()
  #app.thread(test_object.auto_test,d,a,b,s,r,f)
  app.destroySubWindow("Auto Test Running")
  e.clear()
  return

# this e is initialized in the test module
def set_flag():
  global e
  e.set()
  return

def auto_test_wrapper():
  app.startSubWindow("Auto Test Running",modal=True)
  app.addLabel("The auto test is currently running. To stop the test please hit the quit button below. Note that any collected data may be lost.")
  app.addButton("Quit Auto Test",lambda:set_flag())
  app.stopSubWindow()
  app.showSubWindow("Auto Test Running")
  time.sleep(1)
  try:
    app.thread(gui_auto_test)
  except:
    app.destroySubWindow("Auto Test Running")
  time.sleep(1)

app.addButton("Auto Test",lambda:auto_test_wrapper(),row=7)

# this could theoretically be altered to open any file in the folder

def open_csv():
  global most_recent_test
  os.startfile(most_recent_test)

app.addButton("Open Most Recent Test Results",lambda:open_csv(),row=8)
app.stopFrame()
app.startFrame("RIGHT",row=0,column=2)

# widget to show the current position of the linear stage
app.addLabel("Current Stage Position","Current Stage Position",row=0,column=0)
def update_pos():
  try:
    pos= test_object.stage.stage_pos(test_object.motor)
    app.setLabel("Current Stage Position","Current Stage Position : "+str(pos)+" (mm)")
  except:
    pass


app.addLabel("Latest Stage Reading : ","Latest Stage Reading : ",row=1,column=0)
def latest_stage():
  try:
    latest_stage_read=stage_reads[-1]
    #print(latest_stage_read)
    app.setLabel("Latest Stage Reading : ", "Latest Stage Reading : "+str(latest_stage_read)+" (mm)")
  except:
    pass
app.addLabel("Latest LDS Reading : ","Latest LDS Reading : ",row=2,column=0)
def latest_lds():
  try:
    latest_lds_read=lds_reads[-1]
    #print(latest_lds_read)
    app.setLabel("Latest LDS Reading : ","Latest LDS Reading : "+str(latest_lds_read)+" (mm)")
  except:
    pass


axes=app.addPlot("Results",stage_reads,lds_reads,row=3,column=0)
axes.set_xlabel("Actual Distance (mm)")
axes.set_ylabel("Reported Distance (mm)")

def update_plot():
  app.updatePlot("Results",stage_reads,lds_reads,keepLabels=True)
  app.refreshPlot("Results")


# functions which the GUI runs all the time (to update values and plot)
app.registerEvent(update_pos)
app.registerEvent(latest_lds)
app.registerEvent(latest_stage)
app.registerEvent(update_plot)

app.stopFrame()
# sequence to quit the app
app.setStopFunction(lambda:test_object.quit())

# start the app
app.go()