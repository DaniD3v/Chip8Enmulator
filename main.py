import pygame as py

from time import sleep, time
from random import randint
from glob import glob

import Additional as A
from Font import Font

A.CC()


# Config
ProzessorSpeed = 1 / 500  # update the second number it will represent Ips
ScreenMultiplier = 23
COn = (255, 100, 50)  # Color for activated pixel
COff = (0, 0, 0)  # Color for deactivated pixel

ProgramViewer = False

OriginalShifting = True
NormalJumpWithOffset = True  # other behavior was glitched tho might be used by some games
AmigaAddToIndex = True
ModernMemoryLoad = True


# Emulated Hardware
Ram = A.Memory(4095)
Stack = A.Stack(32)

Display = A.Display(64, 32)
Keyboard = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

DT = 0  # DelayTimer
ST = 0  # SoundTimer

IP = 512  # InstructionPointer
AP = 0  # AddressPointer

R = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Register


# time
LastTime = time()
Hz60 = 1 / 60


# font loader
for i in range(0, len(Font)):
    Ram[i] = Font[i]


# Program loader
Paths = glob("Programs/*.ch8")
if len(Paths) > 1:
    print("What program do you want to run?")
    for p in range(1, len(Paths) + 1): print(str(p) + ': ' + Paths[p - 1][9:-4])
    Path = Paths[int(input()) - 1]
else: Path = Paths[0]

f = open(Path, "rb")
Program = f.read()
f.close()
for i in range(0, len(Program)): Ram[512 + i] = Program[i]


# Pygame
Screen = py.display.set_mode((64 * ScreenMultiplier, 32 * ScreenMultiplier), py.NOFRAME)
On = py.Surface((ScreenMultiplier, ScreenMultiplier))
py.draw.rect(On, COn, py.Rect(0, 0, ScreenMultiplier, ScreenMultiplier))

def GetKeys():
    global Keyboard
    Keys = py.key.get_pressed()
    Keyboard[0] = Keys[py.K_x]
    Keyboard[1] = Keys[py.K_1]
    Keyboard[2] = Keys[py.K_2]
    Keyboard[3] = Keys[py.K_3]
    Keyboard[4] = Keys[py.K_q]
    Keyboard[5] = Keys[py.K_w]
    Keyboard[6] = Keys[py.K_e]
    Keyboard[7] = Keys[py.K_a]
    Keyboard[8] = Keys[py.K_s]
    Keyboard[9] = Keys[py.K_d]
    Keyboard[10] = Keys[py.K_y]
    Keyboard[11] = Keys[py.K_c]
    Keyboard[12] = Keys[py.K_4]
    Keyboard[13] = Keys[py.K_r]
    Keyboard[14] = Keys[py.K_f]
    Keyboard[15] = Keys[py.K_v]


def PygameShowScreen():
    global Display, ScreenMultiplier

    if py.event.get(eventtype=py.QUIT): exit(0)

    Screen.fill(COff)
    for l in range(0, 64):
        for r in range(0, 32):
            if Display.get(l, r): py.Surface.blit(Screen, On, (l * ScreenMultiplier, r * ScreenMultiplier))
    py.display.flip()


# main
while True:
    # 60 Hz
    if LastTime + Hz60 < time():
        LastTime = time()
        # Timers
        if DT > 0: DT -= 1
        if ST > 0: ST -= 1
        # Screen Refresh
        PygameShowScreen()

    # Instruction Parts
    Instruction = A.NIB(Ram[IP], 0, 4)
    Xa = A.NIB(Ram[IP], 4, 8)
    Ya = A.NIB(Ram[IP + 1], 0, 4)
    X = R[Xa]
    Y = R[Ya]
    N = A.NIB(Ram[IP + 1], 4, 8)
    NN = Ram[IP + 1]
    NNN = A.NIB((Ram[IP] << 8) + Ram[IP + 1], 4, 16, bits=16)
    Full = (Ram[IP] << 8) + Ram[IP + 1]
    IP += 2

    GetKeys()
    if ProgramViewer: print(hex(Instruction)[2:] + ' ' + hex(Xa)[2:] + ' ' + hex(Ya)[2:] + ' ' + hex(N)[2:] + '  ' + str(IP - 2))


    if Instruction == 0:
        if Full == 224:  # 00E0 Clear screen
            for p in range(0, len(Display.Array)): Display.Array[p] = False

        if Full == 238:  IP = Stack.pop()  # 00EE return from subroutine

    elif Instruction == 1:
        IP = NNN  # 1NNN Jump

    elif Instruction == 2:  # 2NNN Enter Subroutine
        Stack.push(IP)
        IP = NNN

    elif Instruction == 3:  # 3XNN Skip ==
        if X == NN: IP += 2

    elif Instruction == 4:  # 4XNN Skip !=
        if X != NN: IP += 2

    elif Instruction == 5:  # 5XY0 Skip ==
        if X == Y: IP += 2

    elif Instruction == 6:  # 6XNN Set
        R[Xa] = NN

    elif Instruction == 7:
        R[Xa] = A.SO(X + NN, 256)  # 7XNN Add

    elif Instruction == 8:
        if N == 0: R[Xa] = Y  # 8XY0 Set

        elif N == 1: R[Xa] = X | Y  # 8XY1 Or

        elif N == 2: R[Xa] = X & Y  # 8XY2 And

        elif N == 3: R[Xa] = X ^ Y  # 8XY3 Xor

        elif N == 4:  # 8XY4 Add
            R[Xa] = A.SO(X + Y, 256)
            R[15] = A.OverflowFlag

        elif N == 5:  # 8XY5 Subtract
            R[Xa] = A.SU(X - Y, 256)
            R[15] = A.UnderflowFlag

        elif N == 6:  # 8XY6 Shift to the right
            if OriginalShifting: X = R[Xa]
            R[15] = A.NIB(X, -1, index=True)
            R[Xa] = X >> 1

        elif N == 7:  # 8XY7 Subtract
            R[Xa] = A.SU(Y - X, 256)
            R[15] = A.UnderflowFlag

        elif N == 14:  # 8XYE Shift to the left
            if OriginalShifting: X = R[Xa]
            R[15] = A.NIB(X, 0, index=True)
            R[Xa] = X << 1

    elif Instruction == 9:  # 9XY0 Skip !=
        if X != Y: IP += 2

    elif Instruction == 10: AP = NNN  # ANNN Set Index

    elif Instruction == 11:  # BNNN Jump with offset
        if NormalJumpWithOffset: IP = NNN + R[0]
        else: IP = NNN + X

    elif Instruction == 12:  R[Xa] = randint(0, 255) & NN  # CXNN Random

    elif Instruction == 13:  # DXYN Display
        R[15] = 0
        X %= 64
        Y %= 32
        for r in range(0, N):
            if r + Y > 31: break
            Row = list(map(bool, list(map(int, "{0:08b}".format(Ram[AP + r])))))
            for Pixel in range(0, 8):
                if Pixel + X > 63: break
                if Pixel and Display.get(X + Pixel, Y + r): R[15] = 1
                Display.set(X + Pixel, Y + r, Display.get(X + Pixel, Y + r) ^ Row[Pixel])

    elif Instruction == 14:
        if NN == 158:  # EX9E Skip if key
            if Keyboard[X]: IP += 2

        if NN == 161:  # EXA1 Skip if not Key
            if not Keyboard[X]: IP += 2

    elif Instruction == 15:
        if NN == 7: R[Xa] = DT  # FX07 X = DT
        elif NN == 15: DT = X  # FX15 DT = X
        elif NN == 18: ST = X  # FX18 ST = X

        elif NN == 30:  # FX1E Add to AddressPointer
            A.SO(AP + X, 4096)
            if AmigaAddToIndex: R[15] = A.OverflowFlag

        elif NN == 10:  # FX0A Wait for key
            try: R[Xa] = Keyboard.index(True)
            except ValueError: IP -= 2

        elif NN == 41: AP = A.NIB(X, 4, 8) * 5  # FX29 Font character


        elif NN == 51:  # FX33 Decimal conversion
            Ram[AP] = X // 100
            Ram[AP + 1] = X // 10 % 10
            Ram[AP + 2] = X % 10

        elif NN == 85:  # FX55 Load Ram
            for r in range(0, Xa + 1): Ram[AP + r] = R[r]
            if not ModernMemoryLoad: AP += Xa + 1

        elif NN == 101:  # FX65 Store Ram
            for r in range(0, Xa + 1): R[r] = Ram[AP + r]
            if not ModernMemoryLoad: AP += Xa + 1

    else: print("Error")

    sleep(ProzessorSpeed)
