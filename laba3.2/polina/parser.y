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
%token PLUS MINUS AND_ST OR_ST NONEQ_ST EQUAL_ST FUNC_ST INT_ST
%token BOOL_ST TRUE_ST FALSE_ST STRING_ST BYTE_ST FLOAT_ST FOR_ST IF_ST ESLE_ST
%token LBRACE RBRACE UN_PLUS_ST UN_MINUS_ST SPECIFIER WHILE_ST

%token <ident> IDENT
%token <number> NUMBER

%type <ident> start func_decl func_item for_decl if_decl func_params expr expr_log expr_decl ident_val type
%type <ident> expr_una while_decl

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
    SPECIFIER type ident_val LPAREN func_params RPAREN LBRACE {
        char* indent = get_indent(env[0]);
		if (strlen($5) > 0){
			$$ = MEM(2 * strlen(indent) + strlen("public") + strlen($3) + strlen($5) + strlen("(){") + strlen($2) + 2 + strlen("\n"));
			sprintf($$, "%spublic %s %s(%s%s) {", indent, $2, $3, $5, indent);
			free($3);
			free($5);
            free($2);
			free(indent);
		} else {
			$$ = MEM(strlen(indent) + strlen("public") + strlen($3) + strlen($2) + 3 + 2 + 1);
			sprintf($$, "%spublic %s %s() {", indent, $2, $3);
			free($3);
			free(indent);
		}
    }
    ;

func_item:
    for_decl add_indent func_item remove_indent func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(2*strlen(indent) + strlen($1) + 2 * strlen("\n") + strlen($3) + strlen($5) + 1);
		sprintf($$, "%s%s%s\n%s\n%s", indent, $1, indent, $3, $5);
		free($1);
		free($3);
        free($5);
		free(indent);
    };
    |if_decl add_indent func_item remove_indent func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(2*strlen(indent) + strlen($1) + 2 * strlen("\n") +strlen($3) + strlen($5));
		sprintf($$, "%s%s%s\n%s\n%s", indent, $1, indent, $3, $5);
		free($1);
		free($3);
        free($5);
		free(indent);
    };
    |if_decl add_indent func_item remove_indent ESLE_ST LBRACE add_indent func_item remove_indent func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(4*strlen(indent) + 4 * strlen("\n") + strlen($1) + strlen($3) + strlen($8) + strlen($10) + 1);
		sprintf($$, "%s%s%s\n%s\n%selse {%s\n%s\n%s", indent, $1, indent, $3, indent, indent, $8, $10);
		free($1);
		free($3);
        free($8);
        free($10);
		free(indent);
    };
    |while_decl add_indent func_item remove_indent func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(2*strlen(indent) + strlen($1) + 2 * strlen("\n") +strlen($3) + strlen($5));
		sprintf($$, "%s%s%s\n%s\n%s", indent, $1, indent, $3, $5);
		free($1);
		free($3);
        free($5);
		free(indent);
    };
    |expr_decl SEMICOLON func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(strlen(indent) +strlen($1) + 1 + strlen("\n") + strlen($3));
		sprintf($$, "%s%s;\n%s", indent, $1, $3);
		free($1);
		free($3);
		free(indent);
    };
    |expr SEMICOLON func_item {
        char* indent = get_indent(env[0]);
		$$ = MEM(strlen(indent) +strlen($1) + 1 + strlen("\n") + strlen($3));
		sprintf($$, "%s%s;\n%s", indent, $1, $3);
		free($1);
		free($3);
		free(indent);
    };
    |
    RBRACE {
        char* indent = get_indent(env[0] - INDENT);
		$$ = MEM(strlen(indent) + strlen("}"));
		sprintf($$, "%s}", indent);
		free(indent);
    };

for_decl:
    FOR_ST LPAREN expr_decl SEMICOLON expr_log SEMICOLON expr_una RPAREN LBRACE {
        $$ = MEM(strlen("for") + strlen($3) + 1 + strlen($5) + 3 + strlen($7) + 1 + strlen("\n"));
        if (env[0] + 3 + strlen($5) > env[1]) {
            if (strlen($3) + strlen($5) + 2 + env[0] > env[1]) {
                char* indent = get_indent(env[0] + strlen("for "));
                sprintf($$, "for (%s;\n%s%s;;;\n%s%s) {", $3, indent, $5, indent, $7);
            } else {
                char* indent = get_indent(env[0] + strlen("for "));
                sprintf($$, "for (%s;\n%s%s; %s) {", $3, indent, $5, $7);
            }
        } else if (env[0] + 3 + strlen($5) + strlen($7) > env[1]) {
            char* indent = get_indent(env[0] + strlen("for "));
            sprintf($$, "for (%s; %s;\n%s%s) {", $3, $5, indent, $7);
        }
        else {
            sprintf($$, "for (%s; %s; %s) {", $3, $5, $7);
        }
        free($3);
        free($5);
        free($7);
    };

if_decl:
    IF_ST LPAREN expr_log RPAREN LBRACE {
        $$ = MEM( strlen("if") + strlen($3) + strlen("\n") + 3);
        sprintf($$, "if (%s) {", $3);
        free($3);
    };

while_decl:
    WHILE_ST LPAREN expr_log RPAREN LBRACE {
        $$ = MEM( strlen("while") + strlen($3) + strlen("\n") + 3);
        sprintf($$, "while (%s) {", $3);
        free($3);
    }

expr_decl:
    type ident_val ASSIGN expr {
        $$ = MEM(strlen($1) + strlen($2) + strlen(" = ") + strlen($4));
        sprintf($$, "%s %s = %s", $1, $2, $4);
        free($1);
        free($2);
        free($4);
    };
    |
    ident_val ASSIGN expr {
        $$ = MEM(strlen($1) + strlen(" = ") + strlen($3));
        sprintf($$, "%s = %s", $1, $3);
        free($1);
        free($3);
    };

expr_una:
    ident_val UN_PLUS_ST {
        $$ = MEM(strlen($1) + 2);
        sprintf($$, "%s++", $1);
        free($1);
    };
    |
    ident_val UN_MINUS_ST {
        $$ = MEM(strlen($1) + 2);
        sprintf($$, "%s--", $1);
        free($1);
    };

expr:
    NUMBER {
		$$ = MEM(strlen(yylval.number));
		sprintf($$, "%s", yylval.number);
	};
    |
    ident_val {
        $$ = MEM(strlen($1));
        sprintf($$, "%s", $1);
    };
    |
    ident_val PLUS ASSIGN expr {
        $$ = MEM(strlen($1) + strlen(" += ") + strlen($4));
        sprintf($$, "%s += %s", $1, $4);
        free($1);
        free($4);
    };
    |
    expr_log {
        $$ = MEM(strlen($1));
        sprintf($$, "%s", $1);
    };
    |
    expr MINUS ASSIGN expr {
        $$ = MEM(strlen($1) + strlen(" -= ") + strlen($4));
        sprintf($$, "%s -= %s", $1, $4);
        free($1);
        free($4);
    };
    |
    expr DIV ASSIGN expr {
        $$ = MEM(strlen($1) + strlen(" /= ") + strlen($4));
        sprintf($$, "%s /= %s", $1, $4);
        free($1);
        free($4);
    };
    |
    expr MUL ASSIGN expr {
        $$ = MEM(strlen($1) + strlen(" *= ") + strlen($4));
        sprintf($$, "%s *= %s", $1, $4);
        free($1);
        free($4);
    };
    |
    expr MOD ASSIGN expr {
        $$ = MEM(strlen($1) + strlen(" %= ") + strlen($4));
        sprintf($$, "%s %= %s", $1, $4);
        free($1);
        free($4);
    };
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
    };
    |
    expr NONEQ_ST expr {
        $$ = MEM(strlen($1) + strlen(" != ") + strlen($3));
        sprintf($$, "%s != %s", $1, $3);
        free($1);
        free($3);
    };
    |
    expr EQUAL_ST expr {
        $$ = MEM(strlen($1) + strlen(" == ") + strlen($3));
        sprintf($$, "%s == %s", $1, $3);
        free($1);
        free($3);
    };
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
		$$ = MEM(strlen("Int"));
		sprintf($$, "int");
	};
	|
	BOOL_ST {
		$$ = MEM(strlen("Bool"));
		sprintf($$, "bool");
	};
	|
	FLOAT_ST {
		$$ = MEM(strlen("Float32"));
		sprintf($$, "float32");
	};
	|
	STRING_ST {
		$$ = MEM(strlen("String"));
		sprintf($$, "string");
	};
    |
	%empty {
		$$ = MEM(strlen(""));
		sprintf($$, "");
	};


func_params:
	type ident_val COMMA func_params {
		$$ = MEM(strlen($1) + strlen($2) + strlen($4) + 1);
		sprintf($$, "%s %s, %s", $1, $2, $4);
		free($1);
		free($4);
	};
	|
	type ident_val {
		$$ = MEM(strlen($1) + strlen($2));
		sprintf($$, "%s %s", $1, $2);
		free($1);
	};
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