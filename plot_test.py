from appJar import gui

app=gui()

axes=app.addPlot("Results",[0,1,2,3,4,5],[0,1,2,3,4,5])
axes.set_xlabel("Actual Distance")
axes.set_ylabel("Reported Distance")

# this demonstrates that the update plot function isn't used to append
# updatePlot leads to wiping of old data
# simple update
def update():
    app.updatePlot("Results",[10,9,8,7,6],[10,9,8,7,6])
    app.refreshPlot("Results")

app.addButton("Update",lambda:update())

app.go()


