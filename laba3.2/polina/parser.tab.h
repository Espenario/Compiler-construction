/* A Bison parser, made by GNU Bison 3.0.4.  */

/* Bison interface for Yacc-like parsers in C

   Copyright (C) 1984, 1989-1990, 2000-2015 Free Software Foundation, Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

#ifndef YY_YY_PARSER_TAB_H_INCLUDED
# define YY_YY_PARSER_TAB_H_INCLUDED
/* Debug traces.  */
#ifndef YYDEBUG
# define YYDEBUG 0
#endif
#if YYDEBUG
extern int yydebug;
#endif

/* Token type.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
  enum yytokentype
  {
    ASSIGN = 258,
    MUL = 259,
    DIV = 260,
    MOD = 261,
    GREATER = 262,
    LESS = 263,
    NOT = 264,
    LPAREN = 265,
    RPAREN = 266,
    COMMA = 267,
    SEMICOLON = 268,
    PLUS = 269,
    MINUS = 270,
    AND_ST = 271,
    OR_ST = 272,
    NONEQ_ST = 273,
    EQUAL_ST = 274,
    FUNC_ST = 275,
    INT_ST = 276,
    BOOL_ST = 277,
    TRUE_ST = 278,
    FALSE_ST = 279,
    STRING_ST = 280,
    BYTE_ST = 281,
    FLOAT_ST = 282,
    FOR_ST = 283,
    IF_ST = 284,
    ESLE_ST = 285,
    LBRACE = 286,
    RBRACE = 287,
    UN_PLUS_ST = 288,
    UN_MINUS_ST = 289,
    SPECIFIER = 290,
    WHILE_ST = 291,
    IDENT = 292,
    NUMBER = 293
  };
#endif

/* Value type.  */
#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED

union YYSTYPE
{
#line 29 "parser.y" /* yacc.c:1909  */

    char* ident;
    long number;

#line 98 "parser.tab.h" /* yacc.c:1909  */
};

typedef union YYSTYPE YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define YYSTYPE_IS_DECLARED 1
#endif

/* Location type.  */
#if ! defined YYLTYPE && ! defined YYLTYPE_IS_DECLARED
typedef struct YYLTYPE YYLTYPE;
struct YYLTYPE
{
  int first_line;
  int first_column;
  int last_line;
  int last_column;
};
# define YYLTYPE_IS_DECLARED 1
# define YYLTYPE_IS_TRIVIAL 1
#endif



int yyparse (yyscan_t scanner, long env[26]);

#endif /* !YY_YY_PARSER_TAB_H_INCLUDED  */
