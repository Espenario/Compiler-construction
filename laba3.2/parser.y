%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "lexer.h"

#define MEM(size) ((char *)malloc( (size + 1) * sizeof(char)));
#define INDENT 4


char * get_indent(unsigned indent) {
    char *res = (char *)malloc(indent + 1);
    for (long i = 0; i < indent; i++) {
        res[i] = ' ';
    }
    res[indent] = '\0';
    return res;
}

%}

%define api.pure
%locations
%lex-param {yyscan_t scanner}  /* параметр для yylex() */
/* параметры для yyparse() */
%parse-param {yyscan_t scanner}
%parse-param {long env[26]}

%union {
    char* ident;
    long number;
}

%token ASSIGN MUL DIV MOD GREATER LESS NOT LEFT_PAREN RIGHT_PAREN COMMA SEMICOLON
%token PLUS MINUS AND_ST OR_ST NONEQ_ST EQUAL_ST DECL_ST FUNC_ST VAR_ST INT_ST
%token BOOL_ST TRUE_ST FALSE_ST STRING_ST BYTE_ST FLOAT_ST FOR_ST IF_ST ESLE_ST
%token LBRACE RBRACE UN_PLUS_ST UN_MINUS_ST

%token <ident> IDENT
%token <number> NUMBER

%type <ident> start func_decl func_item var_decl for_decl, if_decl func_params expr expr_log expr_decl

%{
int yylex(YYSTYPE *yylval_param, YYLTYPE *yylloc_param, yyscan_t scanner);
void yyerror(YYLTYPE *loc, yyscan_t scanner, long env[26], const char *message);
%}

%%

start:
    func_decl add_indent func_item remove_indent {
        printf("%s\n%s", $1, $3);
    };

func_decl:
    FUNC_ST ident_val LPAREN func_params RPAREN LBRACE {
        char* indent = get_indent(env[0]);
		if (strlen($4) > 0){
			$$ = MEM(2 * strlen(indent) + strlen("func") + strlen($2) + strlen($4) + strlen("(){") + 2 + strlen("\n"));
			sprintf($$, "%sfunc %s(%s%s) {", indent, $2, $4, indent);
			//free($1);
			free($2);
			free($4);
			free(indent);
		} else {
			$$ = MEM(strlen(indent) + strlen("func") + strlen($2) + 3 + 2 + 1);
			sprintf($$, "%sclass %s() {", indent, $2);
			//free($1);
			free($2);
			free(indent);
		}
    };

func_item:
    var_decl func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(strlen(indent) +strlen($1) + 1 + strlen($2));
		sprintf($$, "%s%s\n%s", indent, $1, $2);
		free($1);
		free($2);
		free(indent);
    }
    |
    var_decl SEMICOLON func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(strlen(indent) +strlen($1) + 1 + 1 + strlen($2));
		sprintf($$, "%s%s\n%s", indent, $1, $2);
		free($1);
		free($2);
		free(indent);
    }
    |
    for_decl func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(strlen(indent) +strlen($1) + 1 + strlen($2));
		sprintf($$, "%s%s\n%s", indent, $1, $2);
		free($1);
		free($2);
		free(indent);
    }
    |
    for_decl SEMICOLON func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(strlen(indent) +strlen($1) + 1 + 1 + strlen($2));
		sprintf($$, "%s%s\n%s", indent, $1, $2);
		free($1);
		free($2);
		free(indent);
    }
    |
    if_decl func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(strlen(indent) +strlen($1) + 1 + strlen($2));
		sprintf($$, "%s%s\n%s", indent, $1, $2);
		free($1);
		free($2);
		free(indent);
    }
    |
    if_decl SEMICOLON func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(strlen(indent) +strlen($1) + 1 + 1 + strlen($2));
		sprintf($$, "%s%s\n%s", indent, $1, $2);
		free($1);
		free($2);
		free(indent);
    }
    |
    expr_decl func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(strlen(indent) +strlen($1) + 1 + strlen($2));
		sprintf($$, "%s%s\n%s", indent, $1, $2);
		free($1);
		free($2);
		free(indent);
    }
    |
    expr_decl SEMICOLON func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(strlen(indent) +strlen($1) + 1 + 1 + strlen($2));
		sprintf($$, "%s%s\n%s", indent, $1, $2);
		free($1);
		free($2);
		free(indent);
    }
    |
    RBRACE {
        char* indent = get_indent(env[0] - INDENT);
		$$ = MEM(strlen(indent) + strlen("}"));
		sprintf($$, "%s}", indent);
		free(indent);
    };

var_decl:
    VAR_ST ident_val type {
		$$ = MEM(strlen('var') + strlen($2) + strlen($3) + 1);
		sprintf($$, "var %s %s", $2, $3);
		free($2);
		free($3);
	};

for_decl:
    FOR_ST expr_decl SEMICOLON expr_log SEMICOLON expr LBRACE func_item {
        $$ = MEM(strlen('for') + strlen($2) + 1 + strlen($4) + 1 + strlen($6) + 1 + strlen($8) + strlen("\n"));
        sprintf($$, "for%s;%s;%s {\n%s", $2, $4, $6, $8);
        free($2);
        free($4);
        free($6);
        free($8);
    };

if_decl:
    IF_ST expr_log LBRACE func_item RBRACE {
        $$ = MEM(strlen('if') + strlen($2) + 1 + 2* strlen("\n") + strlen($4) + 1);
        sprintf($$, "if%s {\n%s\n}", $2, $4);
        free($2);
        free($4);
    }
    |
    IF_ST expr_log LBRACE func_item RBRACE ESLE_ST LBRACE func_item RBRACE {
        $$ = MEM(strlen('if') + strlen($2) + 1 + 4* strlen("\n") + strlen($4) + 1 + strlen('else') + 2 + strlen($8));
        sprintf($$, "if%s {\n%s\n} else {\n%s\n}", $2, $4, $8);
        free($2);
        free($4);
        free($8);
    };

expr_decl:
    ident_val ASSIGN expr {
        $$ = MEM(strlen($1) + strlen(" = ") + strlen($3));
        sprintf($$, "%s = %s\n", $1, $3);
        free($1);
        free($3);
    }
    |
    ident_val DECL_ST expr {
        $$ = MEM(strlen($1) + strlen(" := ") + strlen($3));
        sprintf($$, "%s := %s\n", $1, $3);
        free($1);
        free($3);
    }


expr:
    NUMBER 
    |
    ident_val {
        $$ = MEM(strlen($1));
        sprintf($$, "%s", $1);
    }
    |
    expr PLUS expr {
        $$ = MEM(strlen($1) + strlen(" + ") + strlen($3));
        sprintf($$, "%s + %s\n", $1, $3);
        free($1);
        free($3);
    }
    |
    expr_log {
        $$ = MEM(strlen($1));
        sprintf($$, "%s", $1);
    }
    |
    expr MINUS expr {
        $$ = MEM(strlen($1) + strlen(" - ") + strlen($3));
        sprintf($$, "%s - %s\n", $1, $3);
        free($1);
        free($3);
    }
    |
    expr DIV expr {
        $$ = MEM(strlen($1) + strlen(" / ") + strlen($3));
        sprintf($$, "%s / %s\n", $1, $3);
        free($1);
        free($3);
    }
    |
    expr MUL expr {
        $$ = MEM(strlen($1) + strlen(" * ") + strlen($3));
        sprintf($$, "%s * %s\n", $1, $3);
        free($1);
        free($3);
    }
    |
    expr MOD expr {
        $$ = MEM(strlen($1) + strlen(" % ") + strlen($3));
        sprintf($$, "%s % %s\n", $1, $3);
        free($1);
        free($3);
    }
    |
    LPAREN expr RPAREN {
        $$ = MEM(strlen($2) + 1 + 1);
        sprintf($$, "(%s)\n", $2);
        free($2);
    };

expr_log:
    expr LESS expr {
        $$ = MEM(strlen($1) + strlen(" < ") + strlen($3));
        sprintf($$, "%s < %s\n", $1, $3);
        free($1);
        free($3);
    }
    |
    expr NONEQ_ST expr {
        $$ = MEM(strlen($1) + strlen(" != ") + strlen($3));
        sprintf($$, "%s != %s\n", $1, $3);
        free($1);
        free($3);
    }
    |
    expr EQUAL_ST expr {
        $$ = MEM(strlen($1) + strlen(" == ") + strlen($3));
        sprintf($$, "%s == %s\n", $1, $3);
        free($1);
        free($3);
    }
    |
    expr GREATER expr {
        $$ = MEM(strlen($1) + strlen(" > ") + strlen($3));
        sprintf($$, "%s > %s\n", $1, $3);
        free($1);
        free($3);
    };

ident_val:
	IDENT {
		$$ = MEM(strlen(yylval.ident));
		sprintf($$, "%s", yylval.ident);
	};

add_indent:
	%empty {
		env[0] += INDENT;
	};

remove_indent:
	%empty {
		env[0] -= INDENT;
	};

type:
	INT_ST{
		$$ = MEM(strlen("Int"));
		sprintf($$, "int");
	}
	|
	BOOL_ST {
		$$ = MEM(strlen("Bool"));
		sprintf($$, "bool");
	}
	|
	FLOAT_ST {
		$$ = MEM(strlen("Float32"));
		sprintf($$, "float32");
	}
	|
	STRING_SPEC {
		$$ = MEM(strlen("String"));
		sprintf($$, "string");
	};

fun_params:
	ident_val type COMMA fun_params {
		$$ = MEM(strlen($1) + strlen($3) + strlen($5) + 1 + 1 + 1);
		sprintf($$, "%s %s,%s\n", $1, $2, $4);
		free($1);
		free($4);
	}
	|
	ident_val type {
		$$ = MEM(strlen($1) + strlen($2) + 1);
		sprintf($$, "%s %s", $1, $2);
		free($1);
	}
	|
	%empty {
		$$ = "";
	};




%%

int main()
{
	yyscan_t scanner;
	struct Extra extra;
	long env[26];
    env[0] = 0;
    char * buffer = 0;
    long length;
    FILE * f = fopen ("input.txt", "rb");

    if (f) {
    	fseek (f, 0, SEEK_END);
    	length = ftell (f);
    	fseek (f, 0, SEEK_SET);
    	buffer = malloc (length+1);
    	if (buffer)
    		fread (buffer, 1, length, f);
        fclose (f);
        buffer[length] = '\0';
   	}
	init_scanner(buffer, &scanner, &extra);
	yyparse(scanner, env);
	destroy_scanner(scanner);
    free(buffer);
	return 0;
}