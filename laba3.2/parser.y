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

%token ASSIGN MUL DIV MOD GREATER LESS NOT LPAREN RPAREN COMMA SEMICOLON
%token PLUS MINUS AND_ST OR_ST NONEQ_ST EQUAL_ST DECL_ST FUNC_ST VAR_ST INT_ST
%token BOOL_ST TRUE_ST FALSE_ST STRING_ST BYTE_ST FLOAT_ST FOR_ST IF_ST ESLE_ST
%token LBRACE RBRACE UN_PLUS_ST UN_MINUS_ST

%token <ident> IDENT
%token <number> NUMBER

%type <ident> start func_decl func_item var_decl for_decl if_decl func_params expr expr_log expr_decl ident_val type
%type <ident> expr_una

%{
int yylex(YYSTYPE *yylval_param, YYLTYPE *yylloc_param, yyscan_t scanner);
void yyerror(YYLTYPE *loc, yyscan_t scanner, long env[26], const char *message);
%}

%%

start:
    func_decl add_indent func_item remove_indent {
        printf("%s\n%s", $1, $3);
    }
    ;

func_decl:
    FUNC_ST ident_val LPAREN func_params RPAREN type LBRACE {
        char* indent = get_indent(env[0]);
		if (strlen($4) > 0){
            // sprintf("======================");
			$$ = MEM(2 * strlen(indent) + strlen("func") + strlen($2) + strlen($4) + strlen("(){") + strlen($6) + 2 + strlen("\n"));
			sprintf($$, "%sfunc %s(%s%s)%s {", indent, $2, $4, indent, $6);
			//free($1);
			free($2);
			free($4);
            free($6);
			free(indent);
		} else {
			$$ = MEM(strlen(indent) + strlen("func") + strlen($2) + strlen($6) + 3 + 2 + 1);
			sprintf($$, "%sfunc %s()%s {", indent, $2, $6);
			//free($1);
			free($2);
			free(indent);
		}
    }
    ;

func_item:
    var_decl func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(strlen(indent) + strlen($1) + strlen("\n") + strlen($2));
		sprintf($$, "%s%s\n%s", indent, $1, $2);
		free($1);
		free($2);
		free(indent);
    }
    |
    var_decl SEMICOLON func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(strlen(indent) + strlen($1) + 1 + 1 + strlen($3));
		sprintf($$, "%s%s\n%s", indent, $1, $3);
		free($1);
		free($3);
		free(indent);
    }
    |
    for_decl add_indent func_item remove_indent func_item {
        char* indent = get_indent(env[0]);
       // env[0] += INDENT;
		$$ = MEM(strlen(indent) + strlen($1) + 2 * strlen("\n") + strlen($5) + strlen($3));
		sprintf($$, "%s%s\n%s\n%s", indent, $1, $3, $5);
		free($1);
		free($3);
        free($5);
		free(indent);
    }
    |
    if_decl add_indent func_item remove_indent func_item {
        char* indent = get_indent(env[0]);
       // env[0] += INDENT;
		$$ = MEM(strlen(indent) + strlen($1) + 2 * strlen("\n") + strlen($5) + strlen($3));
		sprintf($$, "%s%s\n%s\n%s", indent, $1, $3, $5);
		free($1);
		free($3);
        free($5);
		free(indent);
    }
    |
    if_decl add_indent func_item remove_indent ESLE_ST LBRACE add_indent func_item remove_indent func_item{
        char* indent = get_indent(env[0]);
       // env[0] += INDENT;
		$$ = MEM(strlen(indent) + strlen($1) + 2 * strlen("\n") + strlen($8) + strlen($3) + strlen($10));
		sprintf($$, "%s%s\n%s else {\n%s\n%s", indent, $1, $3, $8, $10);
		free($1);
		free($3);
        free($8);
        free($10);
		free(indent);
    }
    |
    expr_decl func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(strlen(indent) + strlen($1) + strlen("\n") + strlen($2));
		sprintf($$, "%s%s\n%s", indent, $1, $2);
		free($1);
		free($2);
		free(indent);
    }
    |
    expr_decl SEMICOLON func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(strlen(indent) +strlen($1) + 1 + strlen("\n") + strlen($3));
		sprintf($$, "%s%s;\n%s", indent, $1, $3);
		free($1);
		free($3);
		free(indent);
    }
    |
    RBRACE {
        char* indent = get_indent(env[0] - INDENT);
		$$ = MEM(strlen(indent) + strlen("}"));
		sprintf($$, "%s}", indent);
		free(indent);
    };
    // |
    // %empty {
    //     $$ = "";
    // };

var_decl:
    VAR_ST ident_val type {
		$$ = MEM(strlen("var") + strlen($2) + strlen($3) + 1);
		sprintf($$, "var %s%s", $2, $3);
		free($2);
		free($3);
	};

for_decl:
    FOR_ST expr_decl SEMICOLON expr_log SEMICOLON expr_una LBRACE {
        // char* indent = get_indent(env[0]);
        $$ = MEM(strlen("for") + strlen($2) + 1 + strlen($4) + 1 + strlen($6) + 1 + strlen("\n"));
        // printf("CHECK %d", env[0] + strlen($2));
         
        if (env[0] + 3 + strlen($2) > env[1]) {
            if (strlen($4) + strlen($6) + 3 + 1 + env[0] > env[1]) {
                char* indent = get_indent(env[0] + strlen("for "));
                sprintf($$, "for %s;\n%s%s;\n%s%s {", $2, indent, $4, indent, $6);
            } else {
                char* indent = get_indent(env[0] + strlen("for "));
                sprintf($$, "for %s;\n%s%s; %s {", $2, indent, $4, $6);
            }
        } else if (env[0] + 3 + strlen($2) + strlen($4) > env[1]) {
            char* indent = get_indent(env[0] + strlen("for "));
            sprintf($$, "for %s; %s;\n%s%s {", $2, $4, indent, $6);
        }
        else {
            sprintf($$, "for %s; %s; %s {", $2, $4, $6);
        }
        // sprintf($$, "for %s; %s; %s {", $2, $4, $6);
        free($2);
        free($4);
        free($6);
    };

if_decl:
    IF_ST expr_log LBRACE {
        $$ = MEM( strlen("if") + strlen($2) + 1 + strlen("\n") + 1);
        sprintf($$, "if %s {", $2);
        free($2);
    };

expr_decl:
    ident_val ASSIGN expr {
        $$ = MEM(strlen($1) + strlen(" = ") + strlen($3));
        sprintf($$, "%s = %s", $1, $3);
        free($1);
        free($3);
    }
    |
    ident_val DECL_ST expr {
        $$ = MEM(strlen($1) + strlen(" := ") + strlen($3));
        sprintf($$, "%s := %s", $1, $3);
        free($1);
        free($3);
    }

expr_una:
    ident_val UN_PLUS_ST {
        $$ = MEM(strlen($1) + 2);
        sprintf($$, "%s++", $1);
        free($1);
    }
    |
    ident_val UN_MINUS_ST {
        $$ = MEM(strlen($1) + 2);
        sprintf($$, "%s--", $1);
        free($1);
    }

expr:
    NUMBER {
		$$ = MEM(strlen(yylval.number));
		sprintf($$, "%s", yylval.number);
	}
    ;
    |
    ident_val {
        $$ = MEM(strlen($1));
        sprintf($$, "%s", $1);
    }
    |
    expr PLUS expr {
        $$ = MEM(strlen($1) + strlen(" + ") + strlen($3));
        sprintf($$, "%s + %s", $1, $3);
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
        sprintf($$, "%s - %s", $1, $3);
        free($1);
        free($3);
    }
    |
    expr DIV expr {
        $$ = MEM(strlen($1) + strlen(" / ") + strlen($3));
        sprintf($$, "%s / %s", $1, $3);
        free($1);
        free($3);
    }
    |
    expr MUL expr {
        $$ = MEM(strlen($1) + strlen(" * ") + strlen($3));
        sprintf($$, "%s * %s", $1, $3);
        free($1);
        free($3);
    }
    |
    expr MOD expr {
        $$ = MEM(strlen($1) + strlen(" % ") + strlen($3));
        sprintf($$, "%s % %s", $1, $3);
        free($1);
        free($3);
    }
    |
    LPAREN expr RPAREN {
        $$ = MEM(strlen($2) + 1 + 1);
        sprintf($$, "(%s)", $2);
        free($2);
    };

expr_log:
    expr LESS expr {
        $$ = MEM(strlen($1) + strlen(" < ") + strlen($3));
        sprintf($$, "%s < %s", $1, $3);
        free($1);
        free($3);
    }
    |
    expr NONEQ_ST expr {
        $$ = MEM(strlen($1) + strlen(" != ") + strlen($3));
        sprintf($$, "%s != %s", $1, $3);
        free($1);
        free($3);
    }
    |
    expr EQUAL_ST expr {
        $$ = MEM(strlen($1) + strlen(" == ") + strlen($3));
        sprintf($$, "%s == %s", $1, $3);
        free($1);
        free($3);
    }
    |
    expr GREATER expr {
        $$ = MEM(strlen($1) + strlen(" > ") + strlen($3));
        sprintf($$, "%s > %s", $1, $3);
        free($1);
        free($3);
    };

ident_val:
	IDENT {
		$$ = MEM(strlen(yylval.ident));
		sprintf($$, "%s", yylval.ident);
	}
    ;

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
		$$ = MEM(strlen(" Int"));
		sprintf($$, " int");
	}
	|
	BOOL_ST {
		$$ = MEM(strlen(" Bool"));
		sprintf($$, " bool");
	}
	|
	FLOAT_ST {
		$$ = MEM(strlen(" Float32"));
		sprintf($$, " float32");
	}
	|
	STRING_ST {
		$$ = MEM(strlen(" String"));
		sprintf($$, " string");
	}
    |
	%empty {
		$$ = MEM(strlen(""));
		sprintf($$, "");
	};


func_params:
	ident_val type COMMA func_params {
		$$ = MEM(strlen($1) + strlen($2) + strlen($4) + 1 + 1 + 1);
		sprintf($$, "%s%s, %s", $1, $2, $4);
		free($1);
		free($4);
	}
	|
	ident_val type {
		$$ = MEM(strlen($1) + strlen($2) + 1);
		sprintf($$, "%s%s", $1, $2);
		free($1);
        // free($2);
	}
	|
	%empty {
		$$ = "";
	};




%%

int main(int argc, char *argv[])
{
	yyscan_t scanner;
	struct Extra extra;
	long env[26];
    env[0] = 0;
    char * buffer = 0;
    long length;
    FILE * f = fopen ("input.txt", "rb");

    if (argc > 1) {
        printf("Read flag %s\n", argv[1]);
        if (argv[1] = "-d") {
            env[1] = 20;
        }
    }

	init_scanner(f, &scanner, &extra);
	yyparse(scanner, env);
	destroy_scanner(scanner);
    free(buffer);
	return 0;
}