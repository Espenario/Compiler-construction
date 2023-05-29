#!/bin/bash

flex lexer.l
bison -d parser.y
gcc lex.yy.c parser.tab.c -w
./a.out -d