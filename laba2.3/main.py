#from enum import Enum, auto
from copy import deepcopy, copy
#from dataclasses import dataclass

class DomainTag():

    MULT = 1
    PLUS = 2
    LPAREN = 3
    RPAREN = 4
    NUMBERS = 5 
    ENDOFPROGRAMM = 6
    ERROR = 7

    # def __init__(self):
    #     self.IDENT = 1
    #     self.NUMBERS = 2
    #     self.KEYWORDS = 3
    #     self.ENDOFPROGRAMM = 4
    #     self.ERROR = 5

class Position:

    def __init__(self, text):
        self.text = text
        self.line = 1
        self.pos = 1
        self.index = 0
    
    def get_line(self):
        return self.line
    
    def get_pos(self):
        return self.pos
    
    def get_index(self):
        return self.index
    
    def cur_position(self):
        return (-1 if self.index == len(self.text) else self.text[self.index])
    
    def compare_to(self, other_pos):
        return (self.get_index() == other_pos.get_index())
    
    def is_white_space(self):
        return ((self.get_index() != len(self.text)) and \
                self.text[self.get_index()].isspace())
    
    def is_letter(self):
        return ((self.get_index() != len(self.text)) and \
                self.text[self.get_index()].isalpha())
    
    def is_decimal_digit(self):
        return ((self.get_index() != len(self.text)) and \
                self.text[self.get_index()] <= '9' and \
                self.text[self.get_index()] >= '0' )
    
    def is_letter_or_digit(self):
        pass

    def is_new_line(self):
        return self.text[self.get_index()] == '\n'

    def next(self):
        if self.index < len(self.text):
            if self.is_new_line():
                if self.text[self.get_index()] == '\r':
                    self.index += 1
                self.line += 1
                self.pos = 1
            else:
                self.pos += 1
            self.index += 1

    def __repr__(self):
        return "{},{}".format(self.line, self.pos)


class Fragment:

    def __init__(self, starting, following):
        self.starting = starting
        self.following = following

class Message:

    def __init__(self, isError, text):
        self.isError = isError
        self.text = text

class Compiler:
    
    def __init__(self):
        self.messages = []
        self.name_codes = {}
        self.names = []

    def add_name(self, name):
        if name in self.name_codes.keys():
            return self.name_codes[name]
        code = len(self.names)
        self.names.append(name)
        self.name_codes[name] = code
        return code
    
    def get_name(self, code):
        return self.names[code]

    def add_message(self, isErr, pos, text):
        self.messages.append((pos, Message(isErr, text)))

    def output_messages(self):
        pass

class Token:

    def __init__(self, tag, coords, value = None):
        self.tag = tag
        self.coords = coords
        self.value = value

    def __repr__(self):
        return "{} ({} - {}) : {}".format(self.tag, self.coords.starting, self.coords.following, self.value)

class Scanner:

    def __init__(self, programm, compiler):
        self.compiler = compiler
        self.cur = Position(programm)
        self.comments = []

    def get_token(self):
        key_list = ['ON', 'OFF', '**']
        check_list = ['+', '(', '*', ')']
        while self.cur.cur_position() != -1:
            #print(self.cur.cur_position())
            while self.cur.is_white_space():
                self.cur.next()
            start = deepcopy(self.cur)
            if self.cur.cur_position() == '*':
                self.cur.next()
                return Token(DomainTag.MULT, Fragment(start, copy(self.cur)), '*')
            elif self.cur.cur_position() == '+':
                self.cur.next()
                return Token(DomainTag.PLUS, Fragment(start, copy(self.cur)), '+')
            elif self.cur.cur_position() == '(':
                self.cur.next()
                return Token(DomainTag.LPAREN, Fragment(start, copy(self.cur)), '(')
            elif self.cur.cur_position() == ')':
                self.cur.next()
                return Token(DomainTag.RPAREN, Fragment(start, copy(self.cur)), ')')
            elif self.cur.is_decimal_digit():
                buf = ""
                #buf += str(self.cur.cur_position())
                while self.cur.is_decimal_digit():
                    buf += str(self.cur.cur_position())
                    self.cur.next()
                    #buf += str(self.cur.cur_position())
                return Token(DomainTag.NUMBERS, Fragment(start, copy(self.cur)), buf)
            else:
                self.cur.next()
                return Token(DomainTag.ERROR, Fragment(start, copy(self.cur)))
        return Token(DomainTag.ENDOFPROGRAMM, Fragment(self.cur, self.cur))       

    def create_tokens_list(self):
        token_list = []
        token = self.get_token()
        while token.tag != DomainTag.ENDOFPROGRAMM:
            token_list.append(token)
            token = self.get_token()
        token_list.append(token)
        return token_list

def main():
    f =  open('laba2.3/file.txt')
    an_str = f.read()
    scanner = Scanner(an_str, Compiler())
    token_list = scanner.create_tokens_list()
    for token in token_list:
        print(token)

if __name__ == '__main__':
    main()