from symbol_table import SymbolTable
from instruction_table import InstructionTable

class SyntaxAnalyzer:
    """
    Enhanced syntax analyzer for simplified Rat25F with:
    - Symbol table integration
    - Assembly code generation
    - Semantic actions following partial solutions structure
    
    Simplified Rat25F: No functions, no real type, only integer and boolean
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
        self.current_token = self.tokens[0] if self.tokens else None
        self.output = []
        
        # Symbol table and instruction table
        self.symbol_table = SymbolTable()
        self.instruction_table = InstructionTable()
        self.jump_stack = []  # For back-patching

    def lexer(self):
        """Move to next token (matches partial solutions naming)"""
        if self.current_index < len(self.tokens) - 1:
            self.current_index += 1
            self.current_token = self.tokens[self.current_index]

    def match(self, expected):
        """Match current token with expected token/lexeme"""
        token_type, lexeme = self.current_token

        if token_type == expected or lexeme == expected:
            self.output.append(f"Token: {token_type:<15} Lexeme: {lexeme}")
            matched_lexeme = lexeme
            self.lexer()
            return matched_lexeme
        return None

    def error(self, expected):
        """Report syntax error"""
        token_type, lexeme = self.current_token
        raise SyntaxError(
            f"Expected {expected}, but found {token_type}: '{lexeme}' at token position {self.current_index}")

    def print_production(self, rule):
        """Print production rule"""
        self.output.append(f"    <{rule}")
    
    def push_jumpstack(self, address):
        """Push address onto jump stack for back-patching"""
        self.jump_stack.append(address)
    
    def pop_jumpstack(self):
        """Pop address from jump stack"""
        if self.jump_stack:
            return self.jump_stack.pop()
        return None
    
    def back_patch(self, jump_addr):
        """
        Back patch function from partial solutions:
        addr = pop_jumpstack();
        Instr_table[addr].oprn = jump_addr;
        """
        addr = self.pop_jumpstack()
        if addr:
            self.instruction_table.update_instruction(addr, jump_addr)

    # R1. <Rat25F> ::= # <Opt Declaration List> <Statement List> #
    def rat25f(self):
        self.print_production(
            "Rat25F> ::= # <Opt Declaration List> <Statement List> #")

        if not self.match("#"):
            self.error("#")

        self.opt_declaration_list()
        self.statement_list()

        if not self.match("#"):
            self.error("#")

    # R10. <Opt Declaration List> ::= <Declaration List> | <Empty>
    def opt_declaration_list(self):
        token_type, lexeme = self.current_token

        if lexeme in ["integer", "boolean"]:
            self.print_production(
                "Opt Declaration List> ::= <Declaration List>")
            self.declaration_list()
        else:
            self.print_production("Opt Declaration List> ::= <Empty>")
            self.empty()

    # R11. <Declaration List> ::= <Declaration> ; | <Declaration> ; <Declaration List>
    def declaration_list(self):
        self.print_production("Declaration List> ::= <Declaration> ;")
        self.declaration()

        if not self.match(";"):
            self.error(";")

        token_type, lexeme = self.current_token
        if lexeme in ["integer", "boolean"]:
            self.print_production(
                "Declaration List> ::= <Declaration> ; <Declaration List>")
            self.declaration_list()

    # R12. <Declaration> ::= <Qualifier> <IDs>
    def declaration(self):
        self.print_production("Declaration> ::= <Qualifier> <IDs>")
        var_type = self.qualifier()
        self.ids(var_type, is_declaration=True)

    # R8. <Qualifier> ::= integer | boolean
    def qualifier(self):
        self.print_production("Qualifier> ::= integer | boolean")
        token_type, lexeme = self.current_token

        if lexeme in ["integer", "boolean"]:
            self.match(lexeme)
            return lexeme
        else:
            self.error("integer or boolean")

    # R13. <IDs> ::= <Identifier> | <Identifier>, <IDs>
    def ids(self, var_type=None, is_declaration=False):
        self.print_production("IDs> ::= <Identifier>")
        token_type, lexeme = self.current_token

        if not self.match("Identifier"):
            self.error("Identifier")
        
        if is_declaration:
            # Semantic action: Insert into symbol table during declaration
            self.symbol_table.insert(lexeme, var_type)
        else:
            # For get statements, verify identifier exists
            if not self.symbol_table.lookup(lexeme):
                raise Exception(f"Error: Identifier '{lexeme}' not declared")
            # Semantic action: STDIN and POPM for get
            self.instruction_table.gen_instr("STDIN", None)
            addr = self.symbol_table.get_address(lexeme)
            self.instruction_table.gen_instr("POPM", addr)

        token_type, lexeme = self.current_token
        if lexeme == ",":
            self.print_production("IDs> ::= <Identifier> , <IDs>")
            self.match(",")
            self.ids(var_type, is_declaration)

    # R14. <Statement List> ::= <Statement> | <Statement> <Statement List>
    def statement_list(self):
        self.print_production("Statement List> ::= <Statement>")
        self.statement()

        token_type, lexeme = self.current_token
        if token_type == "Identifier" or lexeme in ["{", "if", "return", "put", "get", "while"]:
            self.print_production(
                "Statement List> ::= <Statement> <Statement List>")
            self.statement_list()

    # R15. <Statement> ::= <Compound> | <Assign> | <If> | <Return> | <Print> | <Scan> | <While>
    def statement(self):
        token_type, lexeme = self.current_token

        if lexeme == "{":
            self.print_production("Statement> ::= <Compound>")
            self.compound()
        elif lexeme == "if":
            self.print_production("Statement> ::= <If>")
            self.if_statement()
        elif lexeme == "return":
            self.print_production("Statement> ::= <Return>")
            self.return_statement()
        elif lexeme == "put":
            self.print_production("Statement> ::= <Print>")
            self.print_statement()
        elif lexeme == "get":
            self.print_production("Statement> ::= <Scan>")
            self.scan()
        elif lexeme == "while":
            self.print_production("Statement> ::= <While>")
            self.while_statement()
        elif token_type == "Identifier":
            self.print_production("Statement> ::= <Assign>")
            self.assign()
        else:
            self.error("Statement")

    # R16. <Compound> ::= { <Statement List> }
    def compound(self):
        self.print_production("Compound> ::= { <Statement List> }")

        if not self.match("{"):
            self.error("{")

        self.statement_list()

        if not self.match("}"):
            self.error("}")

    # R17. <Assign> ::= <Identifier> = <Expression> ;
    # Following partial solutions A1: A -> id = E { gen_instr(POPM, get_address(id)) }
    def assign(self):
        self.print_production("Assign> ::= <Identifier> = <Expression> ;")
        token_type, save = self.current_token

        if not self.match("Identifier"):
            self.error("Identifier")
        
        # Check if identifier is declared
        if not self.symbol_table.lookup(save):
            raise Exception(f"Error: Identifier '{save}' not declared")

        if not self.match("="):
            self.error("=")

        self.expression()

        if not self.match(";"):
            self.error(";")
        
        # Semantic action: gen_instr(POPM, get_address(save))
        addr = self.symbol_table.get_address(save)
        self.instruction_table.gen_instr("POPM", addr)

    # R18. <If> ::= if ( <Condition> ) <Statement> fi | if ( <Condition> ) <Statement> else <Statement> fi
    # Following partial solutions structure
    def if_statement(self):
        self.print_production("If> ::= if ( <Condition> ) <Statement> fi")

        if not self.match("if"):
            self.error("if")

        if not self.match("("):
            self.error("(")

        self.condition()

        if not self.match(")"):
            self.error(")")

        self.statement()

        token_type, lexeme = self.current_token
        if lexeme == "else":
            self.print_production(
                "If> ::= if ( <Condition> ) <Statement> else <Statement> fi")
            
            # Before else: generate JUMP and back-patch JUMPZ
            jump_addr = self.instruction_table.instr_address
            self.instruction_table.gen_instr("JUMP", None)
            
            # Back-patch JUMPZ to point to else
            self.back_patch(self.instruction_table.instr_address)
            
            self.match("else")
            self.statement()
            
            # Back-patch JUMP to point after else
            self.instruction_table.update_instruction(jump_addr, self.instruction_table.instr_address)
        else:
            # No else: back-patch JUMPZ to point to end
            self.back_patch(self.instruction_table.instr_address)

        if not self.match("fi"):
            self.error("fi")

    # R19. <Return> ::= return ; | return <Expression> ;
    def return_statement(self):
        self.print_production("Return> ::= return ;")

        if not self.match("return"):
            self.error("return")

        token_type, lexeme = self.current_token
        if lexeme != ";":
            self.print_production("Return> ::= return <Expression> ;")
            self.expression()

        if not self.match(";"):
            self.error(";")

    # R20. <Print> ::= put ( <Expression> );
    # Semantic action: generate STDOUT after expression
    def print_statement(self):
        self.print_production("Print> ::= put ( <Expression> );")

        if not self.match("put"):
            self.error("put")

        if not self.match("("):
            self.error("(")

        self.expression()

        if not self.match(")"):
            self.error(")")

        if not self.match(";"):
            self.error(";")
        
        # Semantic action: gen_instr(STDOUT, nil)
        self.instruction_table.gen_instr("STDOUT", None)

    # R21. <Scan> ::= get ( <IDs> );
    # Semantic action: STDIN and POPM for each identifier
    def scan(self):
        self.print_production("Scan> ::= get ( <IDs> );")

        if not self.match("get"):
            self.error("get")

        if not self.match("("):
            self.error("(")

        self.ids(is_declaration=False)

        if not self.match(")"):
            self.error(")")

        if not self.match(";"):
            self.error(";")

    # R22. <While> ::= while ( <Condition> ) <Statement>
    # Following partial solutions W1: W -> while ( C ) S
    def while_statement(self):
        self.print_production("While> ::= while ( <Condition> ) <Statement>")

        if not self.match("while"):
            self.error("while")

        # Semantic action: addr = instr_address
        addr = self.instruction_table.instr_address
        
        # Semantic action: gen_instr("LABEL", nil)
        self.instruction_table.gen_instr("LABEL", None)

        if not self.match("("):
            self.error("(")

        self.condition()

        if not self.match(")"):
            self.error(")")

        self.statement()

        # Semantic action: gen_instr(JUMP, addr)
        self.instruction_table.gen_instr("JUMP", addr)
        
        # Semantic action: back_patch(instr_address)
        self.back_patch(self.instruction_table.instr_address)

    # R23. <Condition> ::= <Expression> <Relop> <Expression>
    # Following partial solutions C -> E R E
    def condition(self):
        self.print_production(
            "Condition> ::= <Expression> <Relop> <Expression>")
        self.expression()
        op = self.relop()
        self.expression()
        
        # Semantic actions: generate comparison instruction
        if op == "<":
            self.instruction_table.gen_instr("LES", None)
        elif op == ">":
            self.instruction_table.gen_instr("GRT", None)
        elif op == "==":
            self.instruction_table.gen_instr("EQU", None)
        elif op == "!=":
            self.instruction_table.gen_instr("NEQ", None)
        elif op == "<=":
            self.instruction_table.gen_instr("LEQ", None)
        elif op == ">=" or op == "=>":
            self.instruction_table.gen_instr("GEQ", None)
        
        # Semantic action: push_jumpstack and gen_instr(JUMPZ, nil)
        self.push_jumpstack(self.instruction_table.instr_address)
        self.instruction_table.gen_instr("JUMPZ", None)

    # R24. <Relop> ::= == | != | > | < | <= | =>
    def relop(self):
        self.print_production("Relop> ::= == | != | > | < | <= | =>")
        token_type, lexeme = self.current_token

        if lexeme in ["==", "!=", ">", "<", "<=", ">=", "=>"]:
            self.match(lexeme)
            return lexeme
        else:
            self.error("relational operator")

    # R25. <Expression> ::= <Term> <Expression Prime>
    # Following partial solutions A2: E -> T E'
    def expression(self):
        self.print_production("Expression> ::= <Term> <Expression Prime>")
        self.term()
        self.expression_prime()

    # R25'. <Expression Prime> ::= + <Term> <Expression Prime> | - <Term> <Expression Prime> | ε
    # Following partial solutions A3: E' -> + T { gen_instr(ADD, nil) } E'
    def expression_prime(self):
        token_type, lexeme = self.current_token

        if lexeme in ["+", "-"]:
            self.print_production(
                "Expression Prime> ::= + <Term> <Expression Prime>" if lexeme == "+"
                else "Expression Prime> ::= - <Term> <Expression Prime>")
            op = lexeme
            self.match(lexeme)
            self.term()
            
            # Semantic action: gen_instr(ADD/SUB, nil)
            if op == "+":
                self.instruction_table.gen_instr("ADD", None)
            else:
                self.instruction_table.gen_instr("SUB", None)
            
            self.expression_prime()
        else:
            self.print_production("Expression Prime> ::= ε")

    # R26. <Term> ::= <Factor> <Term Prime>
    # Following partial solutions A5: T -> F T'
    def term(self):
        self.print_production("Term> ::= <Factor> <Term Prime>")
        self.factor()
        self.term_prime()

    # R26'. <Term Prime> ::= * <Factor> <Term Prime> | / <Factor> <Term Prime> | ε
    # Following partial solutions A6: T' -> *F { gen_instr(MUL, nil) } T'
    def term_prime(self):
        token_type, lexeme = self.current_token

        if lexeme in ["*", "/"]:
            self.print_production(
                "Term Prime> ::= * <Factor> <Term Prime>" if lexeme == "*"
                else "Term Prime> ::= / <Factor> <Term Prime>")
            op = lexeme
            self.match(lexeme)
            self.factor()
            
            # Semantic action: gen_instr(MUL/DIV, nil)
            if op == "*":
                self.instruction_table.gen_instr("MUL", None)
            else:
                self.instruction_table.gen_instr("DIV", None)
            
            self.term_prime()
        else:
            self.print_production("Term Prime> ::= ε")

    # R27. <Factor> ::= - <Primary> | <Primary>
    def factor(self):
        token_type, lexeme = self.current_token

        if lexeme == "-":
            self.print_production("Factor> ::= - <Primary>")
            self.match("-")
            self.primary()
            # Semantic action: For negation multiply by -1
            self.instruction_table.gen_instr("PUSHI", -1)
            self.instruction_table.gen_instr("MUL", None)
        else:
            self.print_production("Factor> ::= <Primary>")
            self.primary()

    # R28. <Primary> ::= <Identifier> | <Integer> | ( <Expression> ) | true | false
    # Following partial solutions A8: F -> id { gen_instr(PUSHM, get_address(id)) }
    def primary(self):
        token_type, lexeme = self.current_token

        if token_type == "Identifier":
            self.print_production("Primary> ::= <Identifier>")
            identifier = lexeme
            self.match("Identifier")
            
            # Check if identifier is declared
            if not self.symbol_table.lookup(identifier):
                raise Exception(f"Error: Identifier '{identifier}' not declared")
            
            # Semantic action: gen_instr(PUSHM, get_address(token))
            addr = self.symbol_table.get_address(identifier)
            self.instruction_table.gen_instr("PUSHM", addr)

        elif token_type == "Integer":
            self.print_production("Primary> ::= <Integer>")
            value = lexeme
            self.match("Integer")
            # Semantic action: gen_instr(PUSHI, integer_value)
            self.instruction_table.gen_instr("PUSHI", int(value))
            
        elif lexeme == "true":
            self.print_production("Primary> ::= true")
            self.match("true")
            # Semantic action: true = 1
            self.instruction_table.gen_instr("PUSHI", 1)
            
        elif lexeme == "false":
            self.print_production("Primary> ::= false")
            self.match("false")
            # Semantic action: false = 0
            self.instruction_table.gen_instr("PUSHI", 0)
            
        elif lexeme == "(":
            self.print_production("Primary> ::= ( <Expression> )")
            self.match("(")
            self.expression()
            if not self.match(")"):
                self.error(")")
        else:
            self.error(
                "Primary (Identifier, Integer, true, false, or '(')")

    # R29. <Empty> ::= ε
    def empty(self):
        self.print_production("Empty> ::= ε")

    def parse(self):
        """Start parsing from the root"""
        try:
            self.rat25f()

            if self.current_token[0] != "EOF":
                raise SyntaxError(
                    f"Unexpected token after program end: {self.current_token}")

            return True, self.output
        except (SyntaxError, Exception) as e:
            return False, [str(e)]


if __name__ == "__main__":
    pass