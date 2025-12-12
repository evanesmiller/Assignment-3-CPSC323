from syntax import SyntaxAnalyzer
from lexer import LexicalAnalyzer

def main():
    input_files = ["t1.txt", "t2.txt", "t3.txt"]
    output_files = ["o1.txt", 'o2.txt', 'o3.txt']
    
    for input_file, output_file in zip(input_files, output_files):
        try:
            with open(input_file, "r") as f:
                source_code = f.read()
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

            s_analyzer = SyntaxAnalyzer(tokens)
            success, output = s_analyzer.parse()

            with open(output_file, "w") as f:
                if success:
                    f.write("Syntax Analysis Successful!\n")
                    f.write("=" * 50 + "\n\n")
                    for line in output:
                        f.write(line + "\n")
                    print(f"Success! Output written to {output_file}")
                else:
                    f.write("Syntax Analysis Failed!\n")
                    f.write("=" * 50 + "\n\n")
                    for line in output:
                        f.write(line + "\n")
                    print(f"Syntax error found. Check {output_file} for details.")

        except FileNotFoundError:
            print(f"Error: Could not find {input_file}")
        except Exception as e:
            print(f"Error processing {input_file}: {str(e)}")

if __name__ == "__main__":
    main()
