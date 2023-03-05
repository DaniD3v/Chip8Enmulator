from os import system

OverflowFlag = False
UnderflowFlag = False

# Returns binary representation of int
def NIB(integer, startint, endint=0, bits=8, index=False):
    if index: return int(('{0:0' + str(bits) + 'b}').format(integer)[startint], 2)
    else: return int(('{0:0' + str(bits) + 'b}').format(integer)[startint:endint], 2)

# Simulates overflow in python
def SO(integer, maxi):
    global OverflowFlag
    Org = integer
    Return = integer % maxi
    OverflowFlag = int(Return < Org)
    return Return

# Simulates underflow in python
def SU(integer, maxi):
    global UnderflowFlag
    Org = integer
    Return = (integer + maxi) % maxi
    UnderflowFlag = int(Org == Return)
    return Return


# Clears the Console
def CC(): system("cls")

# Ram
class Memory:
    def __init__(self, size):
        self.Size = size
        self.Array = []
        for i in range(0, size): self.Array.append(0)

    def __setitem__(self, key, value):
        if key > self.Size:
            print("Tried to save to memory location that doesn't exist.")
            raise IndexError
        self.Array[key] = value

    def __getitem__(self, key):
        if key > self.Size:
            print("Tried to read from memory location that doesn't exist.")
            raise IndexError
        return self.Array[key]

# Screen
class Display:
    def __init__(self, x, y):
        self.X = x
        self.Size = x * y
        self.Array = []
        for i in range(0, x * y): self.Array.append(False)

    def set(self, x, y, value):
        if x * y > self.Size:
            print("Tried to set a pixel that doesn't exist.")
            raise IndexError
        self.Array[x + self.X * y] = value

    def get(self, x, y):
        if x * y > self.Size:
            print("Tried to get pixel that doesn't exist.")
            raise IndexError
        return self.Array[x + self.X * y]

# Stack
class Stack:
    def __init__(self, layers):
        self.Size = layers
        self.SP = -1
        self.Array = []
        for i in range(0, layers): self.Array.append(0)

    def push(self, address):
        if self.SP + 1 > self.Size:
            print("Stackoverflow.")
            raise IndexError
        self.SP += 1
        self.Array[self.SP] = address

    def pop(self):
        if self.SP < 0:
            print("Tried to read from empty stack.")
            raise IndexError
        self.SP -= 1
        return self.Array[self.SP + 1]
