class App(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [["_","_","_"],
                      ["_","_","_"],
                      ["_","_","_"]]
        self.player = "X"
        self.win = ""
    
    def mousePressed(self, event):
        print(event.x, event.y)
        r = event.y//25
        c = event.x//25
        self.board[r][c] = self.player
        if self.player == "X":
            self.player = "O"
        else:
            self.player = "X"
    
    def keyPressed(self, event):
        print(event.key)

    def timerFired(self):
        if self.checkWin("X"):
            self.win = "X wins"
        elif self.checkWin("O"):
            self.win = "O wins"
        else:
            tie = True
            for row in self.board:
                for col in row:
                    if col == "_":
                        tie = False
            if tie:
                self.win = "No one wins"

    def checkWin(self, player):
        # checks rows
        if [player, player, player] in self.board:
            return True
        # check columns
        elif self.board[0][0] == self.board[1][0] == self.board[2][0] == player:
            return True
        elif self.board[0][1] == self.board[1][1] == self.board[2][1] == player:
            return True
        elif self.board[0][2] == self.board[1][2] == self.board[2][2] == player:
            return True
        # check diagonals
        elif self.board[0][0] == self.board[1][1] == self.board[2][2] == player:
            return True
        elif self.board[0][2] == self.board[1][1] == self.board[2][0] == player:
            return True
        else:
            return False
            
    def redrawAll(self, canvas):
        canvas.create_line(0,0, 75,0)
        canvas.create_line(0,75, 75,75)
        canvas.create_line(0,0, 0,75)
        canvas.create_line(25,0, 25,75)
        canvas.create_line(50,0, 50,75)
        canvas.create_line(75,0, 75,75)
        canvas.create_line(0,25, 75,25)
        canvas.create_line(0,50, 75,50)

        for r in range(len(self.board)):
            row = self.board[r]
            for c in range(len(row)):
                col = row[c]
                x = c*25+12.5
                y = r*25+12.5
                canvas.create_text(x,y, text=col)

        canvas.create_text(62.5,100, text=self.win)


from tkinter import *
def run(width=300, height=300):
    app = App(width, height)
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        app.redrawAll(canvas)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        app.mousePressed(event)
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
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(600, 400)


