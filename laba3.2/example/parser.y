%{
#include <stdio.h>
#include "lexer.h"
%}

%define api.pure
%locations
%lex-param {yyscan_t scanner}  /* параметр для yylex() */
/* параметры для yyparse() */
%parse-param {yyscan_t scanner}
%parse-param {long env[26]}

%union {
    char variable;
    long number;
}

%right ASSIGN
%right IF
%left '+' '-'
%left MUL DIV
%left UMINUS
%token INPUT PRINT LEFT_PAREN RIGHT_PAREN COMMA SEMICOLON DOT

%token <variable> VARIABLE
%token <number> NUMBER

%type <number> expr

%{
int yylex(YYSTYPE *yylval_param, YYLTYPE *yylloc_param, yyscan_t scanner);
void yyerror(YYLTYPE *loc, yyscan_t scanner, long env[26], const char *message);
%}

%%

program:
      statement SEMICOLON program
    | statement DOT
    ;

statement:
      PRINT print_list  { printf("\n"); }
    | INPUT input_list
    | expr
    ;

print_list:
      print_expr
    | print_list COMMA print_expr
    ;

print_expr:
      expr
      {
          printf("%ld ", $expr);
      }
    ;

input_list:
      input_var
    | input_list COMMA input_var
    ;

input_var:
      VARIABLE
      {
          printf("%c = ", $VARIABLE);
          fflush(stdout);
          scanf("%ld", &env[$VARIABLE - 'a']);
      }
    ;

expr:
      VARIABLE ASSIGN expr[value]
      {
          $$ = env[$VARIABLE - 'a'] = $value;
      }
    | expr '+' expr { $$ = $1 + $3; }
    | expr[L] '-' expr[R] { $$ = $L - $R; }
    | expr[L] MUL expr[R] { $$ = $L * $R; }
    | expr[L] DIV expr[R] { $$ = $L / $R; }
    | LEFT_PAREN expr RIGHT_PAREN { $$ = $2; }
    | expr[COND] IF LEFT_PAREN expr[NEG] COMMA expr[ZERO] COMMA expr[POS] RIGHT_PAREN
      {
          /* e ? (neg, zero, pos) */
          $$ = $COND < 0 ? $NEG : $COND > 0 ? $POS : $ZERO;
      }
    | '-' expr[value] %prec UMINUS
      {
          $$ = -$value;
      }
    | NUMBER
    | VARIABLE { $$ = env[$VARIABLE - 'a']; }
    ;

%%

int main(int argc, char *argv[]) {
    FILE *input = 0;
    long env[26] = { 0 };
    yyscan_t scanner;
    struct Extra extra;

    if (argc > 1) {
        printf("Read file %s\n", argv[1]);
        input = fopen(argv[1], "r");
    } else {
        printf("No file in command line, use stdin\n");
        input = stdin;
    }

    init_scanner(input, &scanner, &extra);
    yyparse(scanner, env);
    destroy_scanner(scanner);

    if (input != stdin) {
        fclose(input);
    }

    return 0;
}