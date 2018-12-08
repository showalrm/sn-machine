from display import display
from processor import Cell

cells = []
registers = []

icounter = None

complete = False


def execute_instruction(a, b):
    global icounter
    instruction = create_instruction(a.tostr(), b.tostr())
    opcode = instruction[0]
    icounter = icounter + 2

    if opcode == '1':
        load_from_cell(instruction)
    elif opcode == '2':
        load_with(instruction)
    elif opcode == '3':
        store(instruction)
    elif opcode == '4':
        move(instruction)
    elif opcode == '5':
        add_complement(instruction)
    elif opcode == '6':
        add_float(instruction)
    elif opcode == '7':
        orinstr(instruction)
    elif opcode == '8':
        andinstr(instruction)
    elif opcode == '9':
        xor(instruction)
    elif opcode == 'a':
        rotate(instruction)
    elif opcode == 'b':
        jump(instruction)
    elif opcode == 'c':
        halt()
    else:
        print("instruction could not be completed.")


def create_instruction(a, b):
    completeinstruction = (a + b)

    return completeinstruction


# If instruction looks like 1RXY, load register R
# with the bits found in memory cell XY
def load_from_cell(instruction):
    r = registers[int(instruction[1], 16)]
    xy = instruction[2:]
    xy = cells[int(xy, 16)]

    r.setvalue(hex(xy.getvalue()))


# If instruction looks like 2RXY, load register R
# with the bit pattern XY
def load_with(instruction):

    r = registers[int(instruction[1], 16)]

    value = instruction[2:]
    r.setvalue(hex(int(value, 16)))


# If instruction looks like 3RXY, store the contents
# of register R in memory cell XY
def store(instruction):
    r = registers[int(instruction[1], 16)]
    xy = instruction[2:]
    xy = cells[int(xy, 16)]

    xy.setvalue(hex(r.getvalue()))


# If instruction looks like 4*RS, move/copy the bit
# pattern in register R to register S
def move(instruction):
    r = registers[int(instruction[2], 16)]
    s = registers[int(instruction[3], 16)]

    s.setvalue(hex(r.getvalue()))


# If instruction looks like 5RST, add the bit patterns
# in registers S and T and store the result in R as
# a two's complement representation
def add_complement(instruction):
    r = registers[int(instruction[1], 16)]
    s = registers[int(instruction[2], 16)]
    t = registers[int(instruction[3], 16)]

    sval = s.getvalue()
    tval = t.getvalue()

    if sval > 127:
        sval = - sval
    if tval > 127:
        tval = - tval

    value = sval + tval

    if value > 127:
        value = - value

    r.setvalue(hex(value))


# If instruction looks like 6RST, add the bit patterns
# in registers S and T and store the result in R as
# two's complement. This may be updated later to add
# numbers as floats, but precision with 8 bits is not
# great, and it's hard to see situations where this
# little precision is useful.
def add_float(instruction):
    add_complement(instruction)


# If instruction looks like 7RST, or the bit patterns
# in registers S and T and store the result in R
def orinstr(instruction):
    r = registers[int(instruction[1], 16)]
    s = registers[int(instruction[2], 16)]
    t = registers[int(instruction[3], 16)]

    r.setvalue(hex(s.getvalue() | t.getvalue()))


# If instruction looks like 8RST, and the bit patterns
# in registers S and T and store the result in R
def andinstr(instruction):
    r = registers[int(instruction[1], 16)]
    s = registers[int(instruction[2], 16)]
    t = registers[int(instruction[3], 16)]

    r.setvalue(hex(s.getvalue() & t.getvalue()))


# If instruction looks like 9RST, xor the bit patterns
# in registers S and T and store the result in R
def xor(instruction):
    r = registers[int(instruction[1], 16)]
    s = registers[int(instruction[2], 16)]
    t = registers[int(instruction[3], 16)]

    r.setvalue(hex(s.getvalue() ^ t.getvalue()))


# If instruction looks like AR*X, rotate the bit pattern
# in register R one bit to the right X amount of times.
# Each time place the bit that started on the low end on
# the high end.
def rotate(instruction):
    bits = 8

    r = registers[int(instruction[1], 16)]
    x = registers[int(instruction[3], 16)].getvalue()

    n = x % bits
    a = r.getvalue() >> n
    b = r.getvalue() << ((bits - n) % 256)
    value = a | b
    r.setvalue(hex(value))


# If instruction looks like BRXY, jump to the instruction
# in the memory cell at address XY if the bit pattern in
# register R is equal to the bit pattern in register 0
def jump(instruction):
    global icounter
    if registers[int(instruction[1], 16)].getvalue() == registers[0].getvalue():
        icounter = int(instruction[2:], 16)


# Halt execution.
def halt():
    global complete
    complete = True


def execute(step):
    global icounter
    if len(cells) >= icounter + 1:
        execute_instruction(cells[icounter], cells[icounter + 1])
    if not complete and not step and len(cells) >= icounter + 3:
        execute(False)


def main():
    global icounter, complete
    numcells = -1
    numregisters = -1

    while numcells < 1 or numcells > 256:
        numcells = int(input("How many memory cells would you like to have? "))

    while numregisters < 1 or numregisters > 16:
        numregisters = int(input("How many registers would you like to have? "))

    icounter = int(input("What hex value would you like to set the instruction "
                         "counter at? "), 16)

    done = False

    i = 0
    while i < numcells:
        cells.append(Cell(hex(i)))
        i = i + 1

    i = 0
    while i < numregisters:
        registers.append(Cell(hex(i)))
        i = i + 1

    while not done:
        display(cells, registers, icounter)

        nextstep = input("Type r to edit a register, m to edit a memory cell, \n"
                         "e to execute, i to edit the instruction counter, \n"
                         "enter to step, or anything else to quit. ")

        if nextstep == 'r':
            which = None
            while which is None or which < 0 or which > len(registers):
                which = input("Which register would you like to edit? ")
                which = int(which, 16)

            what = input("What value would you like to put into register " +
                         str(hex(which))[2:] + "? ")

            i = 0
            j = 0
            n = len(what)
            while i < n:
                registers[which + j].setvalue(what[0 + i:2 + i])
                i += 2
                j += 1

        elif nextstep == 'm':
            which = None
            while which is None or which < 0 or which > len(cells):
                which = input("Which memory cell would you like to edit? ")
                which = int(which, 16)

            what = input("What value would you like to put into memory cell " +
                         str(hex(which))[2:] + "? ")

            i = 0
            j = 0
            n = len(what)
            while i < n:
                cells[which + j].setvalue(what[0 + i:2 + i])
                i += 2
                j += 1

        elif nextstep == 'i':
            icounter = int(input("What hex value would you like to set the instruction "
                                 "counter at? "), 16)
            
        elif nextstep == 'e':
            print("-----EXECUTION-----")
            execute(False)
            if complete:
                print("---PROGRAM HALTED--")
                complete = False
            print("---END EXECUTION---")

        elif nextstep == '':
            execute(True)
        else:
            done = True


if __name__ == "__main__":
    main()
