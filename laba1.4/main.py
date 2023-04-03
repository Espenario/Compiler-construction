class Token:
    def __init__(self, ident = None, start_coord = None, end_coord = None, val = None):
        self.ident = ident
        self.start_coord = start_coord
        self.end_coord = end_coord
        self.val = val
        
    def __repr__(self):
        return "{} ({} - {}) : {}".format(self.tag, self.coords.starting, self.coords.following, self.value)

def lex_identifier(str):

def main():
    f =  open('laba5/file.txt')
    raw_str = f.read()

if __name__ == '__main__':
    main()