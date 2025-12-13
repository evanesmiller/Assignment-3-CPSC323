from syntax import SyntaxAnalyzer
from lexer import LexicalAnalyzer

def main():
    """
    Main handler for running test cases.
    Processes input files through:
    1. Lexical analysis (removes comments, tokenizes)
    2. Syntax analysis with semantic actions (symbol table + code generation)
    3. Outputs results with syntax trace, assembly code, and symbol table
    """
    input_files = ["t1.txt", "t2.txt", "t3.txt"]
    output_files = ["o1.txt", "o2.txt", "o3.txt"]
    
    for input_file, output_file in zip(input_files, output_files):
        try:
            # Read source code
            with open(input_file, "r") as f:
                source_code = f.read()
            
            # Lexical Analysis
            l_analyzer = LexicalAnalyzer()
            source_code = l_analyzer.lex_comment(source_code)
            tokens = []
            index = 0
            
            while index < len(source_code):
                if source_code[index].isspace():
                    index += 1
                    continue
                
                token_type, lexeme, index = l_analyzer.lexer(source_code, index)
                if token_type:
                    tokens.append((token_type, lexeme))

            tokens.append(("EOF", ""))

            # Syntax Analysis with Semantic Actions
            s_analyzer = SyntaxAnalyzer(tokens)
            success, output = s_analyzer.parse()

            # Write output
            with open(output_file, "w") as f:
                if success:
                    f.write("Compilation Successful!\n")
                    f.write("=" * 50 + "\n\n")
                    
                    # Write syntax analysis trace
                    f.write("SYNTAX ANALYSIS\n")
                    f.write("-" * 50 + "\n")
                    for line in output:
                        f.write(line + "\n")
                    f.write("\n")
                    
                    # Write assembly code
                    f.write("\n")
                    for line in s_analyzer.instruction_table.print_instructions():
                        f.write(line + "\n")
                    f.write("\n")
                    
                    # Write symbol table
                    for line in s_analyzer.symbol_table.print_table():
                        f.write(line + "\n")
                    
                    print(f"✓ Success! Output written to {output_file}")
                else:
                    f.write("Compilation Failed!\n")
                    f.write("=" * 50 + "\n\n")
                    for line in output:
                        f.write(line + "\n")
                    print(f"✗ Error found in {input_file}. Check {output_file} for details.")

        except FileNotFoundError:
            print(f"✗ Error: Could not find {input_file}")
        except Exception as e:
            print(f"✗ Error processing {input_file}: {str(e)}")

if __name__ == "__main__":
    main()