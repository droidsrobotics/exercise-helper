"""
Program that defines custom UI components for TKinter
Buttons
Terminal
"""
import io
import time
import sys

## Create a button in Tkinter using rectangles
class TKButton(object):
    ## generate dimensions and defaults
    def __init__(self, text, x, y, width, height, bind, fontSize=20):
        self.text = text
        self.font = fontSize
        self.x = x
        self.y = y
        self.width, self.height = width, height
        self.fill = "pink"
        self.clicked = False
        self.bind = bind

    ## draw button as rectangle with text    
    def draw(self, canvas):
        canvas.create_rectangle(self.x, self.y, self.x+self.width, 
                self.y+self.height, fill=self.fill)
        canvas.create_text(self.x+self.width/2, self.y+self.height/2,
                            text=self.text, fill="black", font="Arial "+str(self.font))
    
    ## if mouse pressed on button, toggle color to red and execute bound command
    def mousePressed(self, event):
        if (event.x > self.x and event.x < self.x+self.width and
            event.y > self.y and event.y < self.y+self.height):
            self.clicked = True
            self.fill = "red"
            self.bind(self)

    ## on release, revert to pink
    def mouseReleased(self, event):
        self.clicked = False
        self.fill = "pink"

## Terminal class for Tkinter
class Terminal(object):
    ## define dimensions and command history  
    def __init__(self, app, x0=0, y0=0, x1=640, y1=192, client=False):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.app = app
        self.cmd = ""
        self.cmdHistory = []
        self.cmdRunning = ""
        self.cmdTime = -1
        self.client = client

    ## draw terminal and past 8 commands to the screen
    def redrawAll(self, canvas):
        canvas.create_rectangle(0,0,640,192, fill="black")
        canvas.create_text(10,182,text=">> "+self.cmd,fill="white",anchor="sw")
        for i in range(len(self.cmdHistory[-8:])):
            text = self.cmdHistory[-8:][i][0]
            color = self.cmdHistory[-8:][i][1]
            canvas.create_text(10,20*i+20,text=text,fill=color,anchor="sw")

    ## handle letters being entered into the terminal and space/backspace
    ## on Enter, place command in history and execute it
    def keyPressed(self, event):
        print(event.keysym)
        if event.keysym == "Return":
            self.cmdRunning = self.cmd
            self.cmd = ""
            self.cmdHistory.append((self.cmdRunning, "green"))
            self.cmdTime = time.time()
        elif event.keysym == "Space":
            self.cmd += " "
        elif event.keysym == "BackSpace":
            self.cmd = self.cmd[:-1]
        elif len(event.char) == 1:
            self.cmd += event.char
        
    ## Execute commands as needed
    def timerFired(self):
        if self.cmdTime != -1: ## if commmand running
            ## client uses terminal to connect to host in port 8000      
            ## if game has started, and is an accelerate command, accelerate
            ## in desired direction for time/acc value
            ## if not, try running as python command (pycommands enables)
            ## enable for more scripting --> e.g. locate robot, but disabled
            ## as exploitable
            pycommands = True
            if pycommands:
                try:
                    ## use builtin io module to extrapolate command output
                    f = io.StringIO("")
                    tmp = sys.stdout
                    sys.stdout = f
                    ## try running
                    exec(self.cmdRunning)
                    ## restore console output
                    sys.stdout = tmp
                    self.cmdTime = -1
                    self.cmdHistory.append((f.getvalue().strip(), 
                        "lightblue"))
                    self.cmdHistory.append(("Complete", "lightblue"))
                except:
                    ## show error if failed
                    sys.stdout = tmp
                    self.cmdHistory.append(("Malformed command", "red"))
                    self.cmdTime = -1
            else:
                self.cmdHistory.append(("Malformed command", "red"))
                self.cmdTime = -1
