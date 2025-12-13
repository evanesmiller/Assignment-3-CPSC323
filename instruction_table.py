class InstructionTable:
    """
    Instruction table for generating assembly code.
    Following the structure from partial solutions:
    - instr_address: current instruction address (global)
    - gen_instr: generates instruction with op and operand
    - Stores in array structure
    """
    def __init__(self):
        self.instructions = []
        self.instr_address = 1  # Start at 1 as shown in partial solutions
    
    def gen_instr(self, op, operand=None):
        """
        Generate instruction following partial solutions format:
        Instr_table[instr_address].address = instr_address;
        Instr_table[instr_address].op = op;
        Instr_table[instr_address].oprnd = operand;
        instr_address++;
        """
        self.instructions.append({
            'address': self.instr_address,
            'op': op,
            'operand': operand
        })
        
        current_address = self.instr_address
        self.instr_address += 1
        return current_address
    
    def update_instruction(self, address, operand):
        """
        Update the operand of an instruction at given address.
        Used for back-patching jumps.
        """
        if address > 0 and address <= len(self.instructions):
            self.instructions[address - 1]['operand'] = operand
    
    def print_instructions(self):
        """
        Print instructions ignoring 'nil' operands as specified in partial solutions.
        Format: address  op  operand (if not nil)
        """
        output = []
        output.append("\nAssembly Code")
        output.append("=" * 50)
        for instr in self.instructions:
            if instr['operand'] is None:
                # Print without operand (like "LABEL" or "ADD")
                output.append(f"{instr['address']:<5} {instr['op']}")
            else:
                # Print with operand
                output.append(f"{instr['address']:<5} {instr['op']} {instr['operand']}")
        return output