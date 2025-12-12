
class LexicalAnalyzer:
    def __init__(self):
        self.keywords = {'integer', 'boolean', 'function', 'real',  'if', 'else', 'fi', 'return', 'put', 'get', 'while', 'true', 'false'}
        self.operators = {'==', '!=', '>=', '<=', '+', '-', '*', '/', '%', '=', '<', '>', '||', '&&'}
        self.separators = {'(', ')', '{', '}', '[', ']', ',', ';', ':', '.', '#'}



    def lex_identifier(self, text, i):
        state = "start"
        lexeme = ""
        text = text.lower()

        while i < len(text):
            ch  = text[i]

            if state == "start":
                if ch.isalpha():
                    state = "id"
                    lexeme += ch
                    i += 1
                else:
                    return None
            elif state == "id":
                if ch.isalnum() or ch == '$':
                    lexeme += ch
                    i += 1
                else:
                    break
        if state == "id":
            token_type = "Keyword" if lexeme in self.keywords else "Identifier"
            return token_type, lexeme, i
        
        return None


    def lex_integer(self, text, i):
        start = i
        lexeme = ""

        while i < len(text) and text[i].isdigit():
            lexeme += text[i]
            i += 1

        if not lexeme:
            return None

        if i < len(text) and (text[i].isalpha() or text[i] == '.'):
            while i < len(text) and not (text[i].isspace() or text[i] in self.separators or any(text.startswith(op, i) for op in self.operators)):
                i += 1
            return None, None, i

        return "Integer", lexeme, i



    def lex_real(self, text, i):
        lexeme = ""

        while i < len(text) and text[i].isdigit():
            lexeme += text[i]
            i += 1

        if i < len(text) and text[i] == '.':
            lexeme += '.'
            i += 1
        else:
            return None

        if i < len(text) and text[i].isdigit():
            while i < len(text) and text[i].isdigit():
                lexeme += text[i]
                i += 1
        else:
            while i < len(text) and not (text[i].isspace() or text[i] in self.separators or any(text.startswith(op, i) for op in self.operators)):
                i += 1
            return None, None, i

        if i < len(text) and text[i].isalpha():
            while i < len(text) and not (text[i].isspace() or text[i] in self.separators or any(text.startswith(op, i) for op in self.operators)):
                i += 1
            return None, None, i

        return "Real", lexeme, i
    
    

    def lex_comment(self, text):
        result = ""
        out_comment = True
        for ch in text:
            if ch == '"' or ch == '“':
                out_comment = not out_comment
            elif out_comment:
                result += ch
        return result


    def lexer(self, text, start_index):

        # Identifier FSM
        result = self.lex_identifier(text, start_index)
        if result:
            return result

        # Real FSM
        result = self.lex_real(text, start_index)
        if result:
            return result
        
        # Integer FSM
        result = self.lex_integer(text, start_index)
        if result:
            return result


    

        # Operators and Separators
        for op in sorted(self.operators, key=len, reverse=True):
            if text.startswith(op, start_index):
                return ("Operator", op, start_index + len(op))
        ch = text[start_index]
        if ch in self.separators:
            return ("Separator", ch, start_index + 1)
        
        return None, None, start_index+1

if __name__ == '__main__':
    pass
