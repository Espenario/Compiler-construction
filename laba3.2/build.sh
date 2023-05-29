flex lexer.l
bison -d parser.y
gcc lex.yy.c lab9.tab.c -w
./a.out 