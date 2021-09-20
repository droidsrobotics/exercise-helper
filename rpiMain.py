from TKItems import *
import os


class VideoSelector(object):
    def __init__(self, width, height, app):
        ## define basic vars and modes
        self.width, self.height = width, height
        self.app = app
        self.btns = []
        self.files = ["None"]+os.listdir("videos/")
        y = 0
        x = 0
        for file in self.files:
            if (".mp4" in file and "flip" not in file) or file == "None":
                btn = TKButton(file, x, y+45, 200, 60, self.btnCallback, fontSize=12)
                self.btns.append(btn)
                y+=60
                if y>self.height-90:
                    y = 0
                    x+=200

    def btnCallback(self, button):
        self.app.video = button.text

    ## check button presses
    def mousePressed(self, event):
        for button in self.btns:
                button.mousePressed(event)

    ## check button releases
    def mouseReleased(self, event):
        for button in self.btns:
                button.mouseReleased(event)

    ## draw all the buttons and title
    def redrawAll(self, canvas):
        canvas.create_rectangle(0, 0, self.width, self.height, fill="lightgrey")
        canvas.create_text(self.width/2, 12, text="Video: "+self.app.video, 
                        fill="black", font="Times 12")
        for button in self.btns:
            button.draw(canvas)


class Settings(object):
    def __init__(self, width, height, app):
        ## define basic vars and modes
        self.width, self.height = width, height
        self.modes = ["Py Term", "None"]
        self.mode = 1
        self.levels = ["situp", "pushup", "squat"]
        self.app = app
        ## define buttons for changing modes, difficulty, and level, and to start
        self.modeBtn = TKButton("Show/Hide\nPyTerm", 
                    self.width/5-100, self.height-100, 200, 90, self.changeMode)

        self.level = 0
        self.levelBtn = TKButton("Exercise:\n"+str(self.levels[self.level]), 
                    2.5*self.width/5-100, self.height/3, 200, 100, 
                    self.changeLevel)
        
        self.videoBtn = TKButton("Video:\n"+self.app.video, 
                    2.5*self.width/5-100, self.height-100, 200, 90, 
                                 self.videoSelect, fontSize=12)

        self.wicdBtn = TKButton("Network\nManager", 
                                 4*self.width/5-100, self.height-100, 200, 90, 
                                 self.wicd)

        self.start = TKButton("Start!", self.width/2-50, 2*self.height/3-20, 
                        100, 50, self.startGame)
        self.btns = [self.modeBtn, self.start, self.videoBtn,
                        self.levelBtn, self.wicdBtn]
        self.games = [None] * 10

    ## draw all the buttons and title
    def redrawAll(self, canvas):
        canvas.create_rectangle(0, 0, self.width, self.height, fill="lightgrey")
        canvas.create_text(self.width/2, 100, text="Vitruvio: Exercise Helper", 
                        fill="black", font="Times 28")
        for button in self.btns:
            button.draw(canvas)

    def videoSelect(self, button):
        button.text = "Video:\n"+self.app.video
        self.app.settings = VideoSelector(self.width, self.height, self.app)

    ## alternate between terminal/keyboard mode
    def changeMode(self, button):
        self.mode = (self.mode + 1)%2
        # button.text = "Show Terminal:\n"+self.modes[self.mode]
        self.app.useTerminal = self.mode == 0

    def changeMultiplayer(self, button):
        self.multiplayer = not self.multiplayer
        button.text = "Multiplayer:\n"+str(self.multiplayer)

    ## set difficulty
    def changeDifficulty(self, button):
        self.difficulty = (self.difficulty + 1)%8
        button.text = "Difficulty:\n"+str(self.difficulty)

    ## set level
    def changeLevel(self, button):
        self.level = (self.level + 1)%len(self.levels)
        button.text = "Exercise:\n"+str(self.levels[self.level])

    def startGame(self, button):
        print("Starting...")
        os.system("python3 camera-rpiCam-client.py "+self.levels[self.level]+" "+self.app.ip+" "+self.app.ip2+" "+self.app.video)

    def wicd(self, button):
        print("Starting WICD...")
        os.system("wicd-client &")

    ## check button presses
    def mousePressed(self, event):
        for button in self.btns:
                button.mousePressed(event)

    ## check button releases
    def mouseReleased(self, event):
        for button in self.btns:
                button.mouseReleased(event)

class myApp(object):
    timerDelay = 0.030 ## in seconds
    def __init__(self, width, height):
        self.width, self.height = width, height
        ## Define UI components  
        self.timerDelay = int(myApp.timerDelay*1000)
        self.mouseMovedDelay = int(myApp.timerDelay*1000)
        self.gameStarted = False
        self.simulator = None
        self.video = "None"
        self.score = 0
        self.ip = "192.168.1.168"
        self.ip2 = "192.168.1.175"
        self.settings = Settings(self.width, self.height, self)
        self.terminal = Terminal(self)
        self.useTerminal = False
        self.showHelp = False
        self.home = TKButton("Home", self.width-100, 0, 100, 40, self.home, fontSize=12)
        self.btns = [self.home]

    ## show home screen
    def home(self, button):
        self.gameStarted = False
        self.simulator = None
        self.settings = Settings(self.width, self.height, self)

    ## show help screen
    def help(self, button):
        self.showHelp = not self.showHelp

    ## check mousedpressed in each component
    def mousePressed(self, event):
        if self.gameStarted:
            self.simulator.mousePressed(event)            
        else:
            self.settings.mousePressed(event)
        for button in self.btns:
                button.mousePressed(event)

    ## check mousereleased and other events:
    def mouseReleased(self, event):
        if not self.gameStarted:
            self.settings.mouseReleased(event)   
        for button in self.btns:
                button.mouseReleased(event)

    def mouseDragged(self, event):
        if self.gameStarted:
            self.simulator.mouseDragged(event)  

    def mouseScrolled(self, event):
        if self.gameStarted:
            self.simulator.mouseScrolled(event)  

    def keyPressed(self, event):
        if self.gameStarted:
            self.simulator.keyPressed(event)
        if self.useTerminal:
            self.terminal.keyPressed(event)

    def timerFired(self):
        try:
            if self.gameStarted:
                self.simulator.timerFired() 
            if self.useTerminal:
                self.terminal.timerFired()
        except Exception as e:
            print(e)

    ## draw components and score. If score == 20, draw "You Win!"
    def redrawAll(self, canvas):
        self.settings.redrawAll(canvas)

        for button in self.btns:
            button.draw(canvas)

        if self.useTerminal:
            self.terminal.redrawAll(canvas)

    ## on stop, kill all threads
    def appStopped(self):
        sys.exit()

from tkinter import *
# derived from http://www.krivers.net/15112-s19/notes/notes-oopy-animation.html
def run(width=300, height=300):
    app = myApp(width, height)
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        app.redrawAll(canvas)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        app.mousePressed(event)
        redrawAllWrapper(canvas, data)

    def mouseReleasedWrapper(event, canvas, data):
        app.mouseReleased(event)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        app.keyPressed(event)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        app.timerFired()
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    # init(data)
    # create the root and the canvas
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<ButtonRelease-1>", lambda event:
                            mouseReleasedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(800, 440)
