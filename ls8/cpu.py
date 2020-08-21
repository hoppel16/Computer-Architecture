"""CPU functionality."""

import sys
from enum import Enum, auto


class Equal(Enum):
    EQUAL = auto()
    LESS = auto()
    GREATER = auto()
    NONE = auto()


class CPU:
    """Main CPU class."""

    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8

        self.pc = 0
        self.sp = 244

        self.equal = Equal.NONE

        self.branchtable = {}
        self.branchtable[1] = self.deal_with_HLT
        self.branchtable[17] = self.deal_with_RET
        self.branchtable[69] = self.deal_with_PUSH
        self.branchtable[70] = self.deal_with_POP
        self.branchtable[71] = self.deal_with_PRN
        self.branchtable[80] = self.deal_with_CALL
        self.branchtable[85] = self.deal_with_JEQ
        self.branchtable[130] = self.deal_with_LDI
        self.branchtable[160] = self.deal_with_ADD
        self.branchtable[162] = self.deal_with_MUL
        self.branchtable[167] = self.deal_with_CMP

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        try:
            file_location = sys.argv[1]
            program = open(file_location)
        except Exception:
            print("ERROR: Could not locate file")
            exit(1)

        print(f"LOADING INSTRUCTIONS FOR {file_location}")

        for instruction in program:
            instruction = instruction.strip().split("#")[0]
            try:
                instruction = int(instruction, 2)
            except Exception:
                continue

            self.ram[address] = instruction
            address += 1

        print("FINISHED LOADING INSTRUCTIONS")
        print("---------------------------------------------")

    def ram_read(self, mar):
        return self.reg[mar]

    def ram_write(self, mdr, mar):
        self.reg[mar] = mdr

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "CMP":
            return self.reg[reg_a] - self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def deal_with_LDI(self, mar, mdr):
        self.ram_write(mdr, mar)
        self.pc += 3

    def deal_with_PRN(self, mar, foo):
        print(f"Printing: {self.ram_read(mar)}")
        self.pc += 2

    def deal_with_ADD(self, op_a, op_b):
        self.alu("ADD", op_a, op_b)
        self.pc += 3

    def deal_with_MUL(self, op_a, op_b):
        self.alu("MUL", op_a, op_b)
        self.pc += 3

    def deal_with_PUSH(self, mar, foo):
        self.sp -= 1
        self.ram[self.sp] = self.ram_read(mar)
        self.pc += 2

    def deal_with_POP(self, mar, foo):
        if self.sp == 244:
            print("Stack is empty")
            return
        self.ram_write(self.ram[self.sp], mar)
        self.sp += 1
        self.pc += 2

    def deal_with_CALL(self, op_a, op_b):
        ret_addr = self.pc + 2
        self.sp -= 1
        self.ram[self.sp] = ret_addr

        self.pc = self.reg[op_a]

    def deal_with_RET(self, op_a, op_b):
        ret_addr = self.ram[self.sp]
        self.sp += 1

        self.pc = ret_addr

    def deal_with_CMP(self, op_a, op_b):
        self.equal = Equal.NONE

        result = self.alu("CMP", op_a, op_b)
        if result == 0:
            self.equal = Equal.EQUAL
        elif result > 0:
            self.equal = Equal.GREATER
        else:
            self.equal = Equal.LESS

        self.pc += 3

    def deal_with_JEQ(self, op_a, op_b):
        if self.equal is Equal.EQUAL:
            self.pc = self.reg[op_a]
        else:
            self.pc += 2

    def deal_with_HLT(self, foo, bar):
        exit(0)

    def run(self):
        ir = self.ram[self.pc]
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]

        try:
            self.branchtable[ir](operand_a, operand_b)
        except KeyError:
            print(f"UNKNOWN BYTE: {bin(ir)} ----- {ir}")
            exit(1)

        self.run()
