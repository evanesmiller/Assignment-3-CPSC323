class SymbolTable:
    """
    Symbol table handler with procedures for:
    - Checking if identifier exists
    - Inserting new identifiers
    - Printing all identifiers
    - Error checking for undeclared/duplicate identifiers
    """
    def __init__(self):
        self.table = {}
        self.memory_address = 10000
    
    def insert(self, identifier, var_type):
        """
        Insert a new identifier into the symbol table.
        Raises exception if identifier already declared.
        """
        if identifier in self.table:
            raise Exception(f"Error: Identifier '{identifier}' already declared")
        
        self.table[identifier] = {
            'memory_address': self.memory_address,
            'type': var_type
        }
        current_address = self.memory_address
        self.memory_address += 1
        return current_address
    
    def lookup(self, identifier):
        """
        Check if identifier exists in the table.
        Returns entry if found, None otherwise.
        """
        return self.table.get(identifier)
    
    def get_address(self, identifier):
        """
        Get memory address of an identifier.
        Raises exception if identifier not declared.
        """
        entry = self.lookup(identifier)
        if entry is None:
            raise Exception(f"Error: Identifier '{identifier}' not declared")
        return entry['memory_address']
    
    def get_type(self, identifier):
        """
        Get type of an identifier.
        Raises exception if identifier not declared.
        """
        entry = self.lookup(identifier)
        if entry is None:
            raise Exception(f"Error: Identifier '{identifier}' not declared")
        return entry['type']
    
    def check_type_match(self, identifier1, identifier2):
        """
        Check if two identifiers have matching types.
        Returns True if types match, False otherwise.
        """
        type1 = self.get_type(identifier1)
        type2 = self.get_type(identifier2)
        return type1 == type2
    
    def print_table(self):
        """Print all identifiers in the table"""
        output = []
        output.append("\nSymbol Table")
        output.append("=" * 50)
        output.append(f"{'Identifier':<20} {'MemoryLocation':<20} {'Type':<10}")
        output.append("-" * 50)
        for identifier, info in self.table.items():
            output.append(f"{identifier:<20} {info['memory_address']:<20} {info['type']:<10}")
        return output