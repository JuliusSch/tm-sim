import numpy as np
import pygame as pg
import time
import sys

pg.init()
winWidth = pg.display.Info().current_w
winHeight = pg.display.Info().current_h
window = pg.display.set_mode()
pg.display.set_caption("Turing Machine Simulator")
speed = 3.0
font = pg.font.SysFont('Courier New', 64)
font_s = pg.font.SysFont('Courier New', 16)
buttonFont = pg.font.SysFont('Courier New', 24)
textsurface = font.render('a', False, (0, 0, 0))

cellSprite = pg.image.load("cell.png")
cellSprSize = 64
headSprite = pg.image.load("head.png")
tapeCentreX = int(winWidth / 2 - cellSprSize / 2)
tapeY = 300
tapeVel = 4

class Game():
    def __init__(self):
        #print(pg.font.get_fonts())
        self.tms = []
        self.time = 0
        self.tms.append(TuringMachine("binaryincrement", "Increment"))
        self.tms.append(TuringMachine("binarydecrement", "Decrement"))
        self.tms.append(TuringMachine("binaryaddition", "Addition"))
        self.tms.append(TuringMachine("binarycopy", "Copy"))
        self.tms.append(TuringMachine("shiftright", "Shift Right"))
        self.active = False
        self.instructionFeed = []
        self.selectTM = self.tms[0]
        self.tape = Tape(self.selectTM.startTape)
        self.tapeEditor = TapeEditor((winWidth / 2) - 300, (winHeight / 2) + 100, 600, (winHeight / 2) - 100)
        self.buttons = []
        self.buttons.append(PauseButton(240, 70, 200, 30, "Start (Space)"))
        self.buttons.append(ResetButton(240, 105, 200, 30, "Reset Tape (R)"))
        self.buttons.append(ExitButton(240, 140, 200, 30, "Exit (Esc)"))
        self.buttons.append(SelectMachineButton(50, 70, 160, 30, "Increment", self.tms[0]))
        self.buttons.append(SelectMachineButton(50, 140, 160, 30, "Decrement", self.tms[1]))
        self.buttons.append(SelectMachineButton(50, 105, 160, 30, "Addition", self.tms[2]))
        self.buttons.append(SelectMachineButton(50, 175, 160, 30, "Copy", self.tms[3]))
        self.buttons.append(SelectMachineButton(50, 210, 160, 30, "Shift Right", self.tms[4]))
        return

    def update(self):
        self.updateButtons()
        x, y = pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]
        self.tapeEditor.update(x, y)
        self.time += 1
        if self.active:
            self.selectTM.update()
            self.tape.update()
        return
    

    def render(self):
        self.selectTM.render()
        lab = buttonFont.render("Currently running: " + self.selectTM.label, True, (0, 0, 0))
        window.blit(lab, (int(winWidth / 2) - 193, 150))
        self.tape.render()
        self.tapeEditor.render()
        for b in self.buttons:
            b.render()
        if len(self.instructionFeed) >= 10: self.instructionFeed.pop(0)
        lie = font_s.render("Last instruction executed: ", True, (0,0,0))
        window.blit(lie, (winWidth - 500, 270))
        for i in range (len(self.instructionFeed)):
            instr = font_s.render(space(str(self.instructionFeed[i])), True, (0,0,0))
            window.blit(instr, (winWidth - 230, 300 + (i - len(self.instructionFeed)) * 30))
        pt = buttonFont.render("Programs", True, (0,0,0))
        window.blit(pt, (50, 30))
        ot = buttonFont.render("Options", True, (0,0,0))
        window.blit(ot, (240, 30))
        return

    def checkButtons(self, x, y, button):
        for b in self.buttons: b.check(x, y, button)

    def updateButtons(self):
        x, y = pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]
        for b in self.buttons: b.update(x, y)

def space(s):
    return "    ".join(s)

class TuringMachine():
    def __init__(self, folderName, label):#includes: instructions, alphabet, startTape, states
        instructions, alphabet, startTape, states = readFolder(folderName)
        self.scanChar = startTape[0]
        self.currentState = states[0]
        self.alphabet = list(alphabet)
        self.startTape = startTape
        self.states = states
        self.folderName = folderName
        self.label = label
        self.instructions = instructions.split()
        parse(self.instructions,alphabet,states)
        
    def update(self):
        if game.time % (60/speed) == 0:
            if not self.checkInstructions():
                print("failure")
            
    def checkInstructions(self):
        for i in range (len(self.instructions)):
            li = self.instructions[i]
            instr = Instruction(li[0], li[1], li[2], li[3], li[4])
            self.scanChar = game.tape.cells[game.tape.tapePos]
            if (instr.state == game.selectTM.currentState) & (instr.scanChar == self.scanChar):
                instr.execute()
                game.instructionFeed.append(li)
                return True
        return False
        
    def render(self):
        window.blit(headSprite, (tapeCentreX, tapeY - 64))
        speedDisp = buttonFont.render("speed: "+str(speed), False, (0,0,0))
        window.blit(speedDisp, (int(winWidth / 2) - 50, 400))

class Instruction():
    def __init__(self, state, scanChar, printChar, move, nextState):
        self.state = state
        self.scanChar = scanChar
        self.printChar = printChar
        self.move = move
        self.nextState = nextState

    def execute(self):
        game.tape.writeChar(self.printChar)
        game.tape.moveTapePos(self.move, game.selectTM)
        game.selectTM.scanCar = game.tape.cells[game.tape.tapePos]
        game.selectTM.currentState = self.nextState
        
class Tape():
    def __init__(self, cells):
        self.cells = cells
        self.offSprX = 14
        self.offSprY = -3
        self.tapePos = 0
        self.xOff = 0
        self.lastMove = 0
        self.smoothMove = 0.0
     
    def writeChar(self, char):
        self.cells[self.tapePos] = char

    def moveTapePos(self, move, tm):
        m = parseMove(move)
        self.tapePos += m
        self.lastMove = m
        self.smoothMove = 0
        if (self.tapePos >= len(self.cells)-10): self.cells.append(tm.alphabet[0])

    def update(self):
        smoothScroll= (cellSprSize/60)*self.lastMove*self.smoothMove
        if (self.smoothMove < 60): self.smoothMove = self.smoothMove + 2.0*(speed)
        self.xOff = (self.tapePos - self.lastMove) * cellSprSize + smoothScroll
        
    def render(self):
        for i in range(-15, len(self.cells) + 15):
            xx = int(tapeCentreX + (i * cellSprSize) - self.xOff)
            window.blit(cellSprite, (xx, tapeY))
            if (i >= 0) and (i < len(self.cells)) and (self.cells[i] != '-'): symbol = font.render(self.cells[i], False, (0, 0, 0))
            else: symbol = font.render(' ', False, (0, 0, 0))
            window.blit(symbol, (xx + self.offSprX,tapeY + self.offSprY))

def parse(instr, alphabet, states):
    for i in range(len(instr)):
        chars = list(instr[i])
        if not (chars[1] in alphabet): raise ValueError('Characters not in alphabet.[1]: ',chars[1])
        if not (chars[2] in alphabet): raise ValueError('Characters not in alphabet.[2]: ',chars[2])
        if not (chars[0] in states): raise ValueError('State out of range: [0]')
        if not (chars[4] in states): raise ValueError('State out of range: [4]')
        if (chars[3] != 'L') & (chars[3] != 'N') & (chars[3] != 'R'): raise ValueError('[3] should be L,N or R: ',int(chars[3]))
    return True

def parseMove(char):
    if (char == 'L'): return -1
    if (char == 'N'): return 0
    if (char == 'R'): return 1
    raise ValueError("Use LNR.")
    
def read(name):
    f = open(name, "r")
    f1 = f.read()
    return f1

def readFolder(name):
    instructions = read(name + "/instructions.txt")
    alphabet = list(read(name + "/alphabet.txt"))
    tape = list(read(name + "/inputtape.txt"))
    states = list(read(name + "/states.txt"))
    return instructions, alphabet, tape, states

class Button():
    def __init__(self, x, y, width, height, label):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.x2 = self.x + self.width
        self.y2 = self.y + self.height
        self.label = label
        self.highlight = False

    def check(self, mx, my, mButton):
        if (mx >= self.x) & (mx <= self.x2) & (my >= self.y) & (my <= self.y2):
            if (mButton == 1): self.execute()
            if (mButton == 3): self.showInfo()
            return True
        return False

    def update(self, mx, my):
        if (mx >= self.x) & (mx <= self.x2) & (my >= self.y) & (my <= self.y2): self.highlight = True
        else: self.highlight = False
        return
    
    def execute(self):
        pass

    def showInfo(self):
        print("right click")

    def render(self):
        if self.highlight: pg.draw.rect(window, (100, 100, 100), (self.x, self.y, self.width, self.height))
        else: pg.draw.rect(window, (200, 200, 200), (self.x, self.y, self.width, self.height))
        labelT = buttonFont.render(self.label, True, (0, 0, 0))
        window.blit(labelT, (self.x + 2,self.y + 2))            


class PauseButton(Button):
    def execute(self):
        if (game.tapeEditor.active): return
        if game.active == True: game.active = False    
        elif game.active == False: game.active = True

    def render(self):
        if self.highlight: pg.draw.rect(window, (100, 100, 100), (self.x, self.y, self.width, self.height))
        else: pg.draw.rect(window, (200, 200, 200), (self.x, self.y, self.width, self.height))
        if game.active: lb = "Pause (Space)"
        else: lb = "Start (Space)"
        labelT = buttonFont.render(lb, True, (0, 0, 0))
        window.blit(labelT, (self.x + 2,self.y + 2))    

class SelectMachineButton(Button):
    def __init__(self, x, y, width, height, label, machine):
        super().__init__(x,y,width,height,label)
        self.TM = machine
    
    def execute(self):
        game.tape = Tape(game.tape.cells)
        game.selectTM = TuringMachine(self.TM.folderName, self.TM.label)

class ExitButton(Button):
    def execute(self):
        pg.quit()
        sys.exit()

class ResetButton(Button):
    def execute(self):
        game.selectTM.scanChar = game.selectTM.startTape[0]
        game.selectTM.currentState = game.selectTM.states[0]
        game.tape = Tape(game.selectTM.startTape)
        game.instructionFeed = []
       
class TapeEditor():
    def __init__(self, x, y, width, height):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.x2 = self.x + self.width
        self.y2 = self.y + self.height
        self.active = False
        self.tempTape = []
        self.label = []
        self.label.append("Hover to edit tape input (Warning, editing will reset the")
        self.label.append("program currently running).")
        self.lines = []
        self.lines.append("Use the keys '0', '1', 'space' and 'backspace' to edit the")
        self.lines.append("input tape. Remember that different Turing programs")
        self.lines.append("require different tape configurations.")
        self.edits = 0
        
    def update(self, mx, my):
        if mx >= self.x and mx <= self.x2 and my >= self.y and my <= self.y2: self.activate()
        else: self.deactivate()
        if (self.active and game.active): game.active = False

    def activate(self):
        if self.active: return
        else: self.active = True
        self.tempTape = ("".join(game.tape.cells)).strip('-')
        self.edits = 0
        print(self.tempTape)
        return

    def deactivate(self):
        if not self.active: return
        else: self.active = False
        if self.edits > 0:
            game.buttons[4].execute()
            game.tape = Tape(list(self.tempTape))
        #else: game.active = True
        return

    def interpret(self, char):
        if not self.active: return
        elif not game.active:
            if char == '0': self.tempTape = self.tempTape + char
            if char == '1': self.tempTape = self.tempTape + char
            if char == ' ': self.tempTape = self.tempTape + '-'
            if char == 'B': self.tempTape = self.tempTape[:-1]
        self.edits += 1
        print(self.tempTape)

    def render(self):
        if self.active: pg.draw.rect(window, (240, 240, 240), (self.x, self.y, self.width, self.height))
        else: pg.draw.rect(window, (200, 200, 200), (self.x, self.y, self.width, self.height))
        toPrint = []
        if self.active:
            toPrint = self.lines
            window.blit(font_s.render("tape: " + self.tempTape + "_", True, (0,0,0)), (self.x + 10, self.y + 100))
            window.blit(font_s.render("Move cursor out of area to confirm.", True, (0,0,0)), (self.x + 10, self.y + 140))
        else: toPrint = self.label
        for i in range(len(toPrint)): window.blit(font_s.render(toPrint[i], True, (0,0,0)), (self.x + 10,self.y + 5 + i * 20))


current_milli_time = lambda: int(round(time.time() * 1000))
last_milli_time = current_milli_time()
last_t = time.time()
ns = 1 / 60
delta = 0
frames = 0
updates = 0

DISPLAYSURF = pg.display.set_mode((0, 0), pg.FULLSCREEN)

run = True
game = Game()

while run:
    now_t = time.time()
    delta += (now_t - last_t) / ns
    last_t = now_t

    while delta >= 1:
        game.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.MOUSEBUTTONDOWN:
                x, y = pg.mouse.get_pos()
                game.checkButtons(x,y, event.button)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE: game.buttons[0].execute()
                if event.key == pg.K_DOWN and speed >= 2: speed -= 1
                if event.key == pg.K_UP and speed <= 5: speed += 1
                if event.key == pg.K_ESCAPE: game.buttons[2].execute()
                if event.key == pg.K_r: game.buttons[1].execute()
                if event.key == pg.K_0: game.tapeEditor.interpret('0')
                if event.key == pg.K_1: game.tapeEditor.interpret('1')
                if event.key == pg.K_SPACE: game.tapeEditor.interpret(' ')
                if event.key == pg.K_BACKSPACE: game.tapeEditor.interpret('B')
        updates += 1
        delta -= 1
    window.fill((255, 255, 255))
    game.render()
    frames += 1
    if current_milli_time() - last_milli_time > 1000:
        last_milli_time += 1000
        print(str(updates) + " ups |" + str(frames) + " fps")
        frames = 0
        updates = 0
    pg.display.update()
    
pg.quit()
