import sys

class CPU:

    def __init__(self):
        self.ram = [0] * 256 
        self.reg = [0] * 8 
        self.pc = 0 
        self.sp = 7 
        self.reg[self.sp] = 244 
        self.e = 7 
        self.fl = [0] * 8 

    def load(self):

        address = 0

        if len(sys.argv) != 2:
            print("need to pass a filename as an argument!")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    num = line.split("#", 1)[0]
                    if num.strip() != "":
                        self.ram_write(address, int(num, 2))
                        address += 1

        except FileNotFoundError:
            print("Could not find that file")
            sys.exit(2)


    def halt(self):
        print('Program Halted')
        sys.exit(1)

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr


    def alu(self, operation_code, register_a, register_b):
        """ALU operations."""

        if operation_code == "ADD":
            self.reg[register_a] += self.reg[register_b]
        elif operation_code == "MUL":
            self.reg[register_a] = self.reg[register_a] * self.reg[register_b]
        elif operation_code == "AND":
            self.reg[register_a] = self.reg[register_a] & self.reg[register_b]
        elif operation_code == "DEC":
            self.reg[register_a] -= 1
        elif operation_code == "INC":
            self.reg[register_a] += 1
        elif operation_code == "CMP":
            if self.reg[register_a] == self.reg[register_b]:
                self.fl[self.e] = 1
            else:
                self.fl[self.e] = 0
        elif operation_code == "MOD":
            self.reg[register_a] = self.reg[register_a] % self.reg[register_b]
        elif operation_code == "DIV":
            if self.reg[register_b] != 0:
                self.reg[register_a] = self.reg[register_a] / self.reg[register_b]
            else:
                self.halt()
        else:
            raise Exception("Cannot process that ALU")

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

    def run(self):

        HLT = 0b00000001
        LDI = 0b10000010
        PRN = 0b01000111
        MUL = 0b10100010
        ADD = 0b10100000
        AND = 0b10101000
        POP = 0b01000110
        LD  = 0b10000011
        MOD = 0b10100100
        PUSH = 0b01000101
        CMP = 0b10100111
        CALL = 0b01010000
        RET = 0b00010001
        JMP = 0b01010100
        JNE = 0b01010110
        JEQ = 0b01010101


        while self.pc < len(self.ram):

            command = self.ram[self.pc]
            num_ops = (command & 0b11000000) >> 6

            if num_ops == 1:
                operand_a = self.ram_read(self.pc + 1)
            elif num_ops == 2:
                operand_a = self.ram_read(self.pc + 1)
                operand_b = self.ram_read(self.pc + 2)

            if command == HLT:
                self.halt()
            elif command == LDI:
                self.reg[operand_a] = operand_b
            elif command == PRN:
                print(self.reg[operand_a])
            elif command == MUL:
                self.alu("MUL", operand_a, operand_b)
                print(self.reg[operand_a])
            elif command == ADD:
                self.alu("ADD", operand_a, operand_b)
            elif command == AND:
                self.alu("AND", operand_a, operand_b)
            elif command == LD:
                self.reg[operand_a] = self.reg[operand_b]
            elif command == MOD:
                self.alu("MOD", operand_a, operand_b)
            elif command == POP:
                value = self.ram[self.reg[self.sp]]
                self.reg[operand_a] = value
                self.reg[self.sp] += 1
            elif command == PUSH:
                self.reg[self.sp] -= 1
                value = self.reg[operand_a]
                self.ram[self.reg[self.sp]] = value  
            elif command == CMP:
                self.alu("CMP", operand_a, operand_b)

            if command == CALL:
                return_addr = self.pc + 2
                self.reg[self.sp] -= 1
                self.ram[self.reg[self.sp]] = return_addr
                regnum = self.ram[self.pc + 1]
                subroutine_addr = self.reg[regnum]
                self.pc = subroutine_addr
                
            elif command == RET:
                return_addr = self.ram[self.reg[self.sp]]
                self.reg[self.sp] += 1
                self.pc = return_addr
            elif command == JMP:
                self.pc = self.reg[operand_a]
            elif command == JNE:
                if self.fl[self.e] == 0:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += num_ops + 1
            elif command == JEQ:
                if self.fl[self.e] == 1:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += num_ops + 1
            else:
                self.pc += num_ops + 1
