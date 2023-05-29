%option reentrant noyywrap bison-bridge bison-locations
%option extra-type="struct Extra *"

/* Подавление предупреждений для -Wall */
%option noinput nounput

%{

#include <stdio.h>
#include <stdlib.h>
#include "lexer.h"
#include "parser.tab.h"  /* файл генерируется Bison’ом */

#define YY_USER_ACTION \
  { \
    int i; \
    struct Extra *extra = yyextra; \
    if (! extra->continued ) { \
      yylloc->first_line = extra->cur_line; \
      yylloc->first_column = extra->cur_column; \
    } \
    extra->continued = false; \
    for (i = 0; i < yyleng; ++i) { \
      if (yytext[i] == '\n') { \
        extra->cur_line += 1; \
        extra->cur_column = 1; \
      } else { \
        extra->cur_column += 1; \
      } \
    } \
    yylloc->last_line = extra->cur_line; \
    yylloc->last_column = extra->cur_column; \
  }

void yyerror(YYLTYPE *loc, yyscan_t scanner, long env[26], const char *message) {
    printf("Error (%d,%d): %s\n", loc->first_line, loc->first_column, message);
}

%}

%%

[\r\t\n ]+

=   return ASSIGN;
\+  return PLUS;
-   return MINUS;
\*  return MUL;
\{  return LBRACE;
\}  return RBRACE; 
\/  return DIV;
%   return MOD;
>   return GREATER;
\<   return LESS;
!   return NOT;
\(  return LPAREN;
\)  return RPAREN;
,   return COMMA;
;   return SEMICOLON;


[0-9]+  {
    yylval->number = strdup(yytext);
    return NUMBER;
}

[a-z]   {
    yylval->ident = strdup(yytext);
    return IDENT;
}


\+\+    return UN_PLUS_ST;
--      return UN_MINUS_ST;
&&      return AND_ST;
\|\|      return OR_ST;
!=      return NONEQ_ST;
==      return EQUAL_ST;
:=      return DECL_ST;
func    return FUNC_ST;
var     return VAR_ST;
int     return INT_ST;
bool    return BOOL_ST;
true    return TRUE_ST;
false   return FALSE_ST;
string  return STRING_ST;
byte    return BYTE_ST;
float32 return FLOAT_ST;
for     return FOR_ST;
if      return IF_ST;
else    return ESLE_ST;




%%

void init_scanner(FILE *input, yyscan_t *scanner, struct Extra *extra) {
    extra->continued = false;
    extra->cur_line = 1;
    extra->cur_column = 1;

    yylex_init(scanner);
    yylex_init_extra(extra, scanner);
    yyset_in(input, *scanner);
}

void destroy_scanner(yyscan_t scanner) {
    yylex_destroy(scanner);
}