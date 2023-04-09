%option noyywrap bison-bridge bison-locations

%{

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TAG_EOF 0
#define TAG_LONG 1
#define TAG_FRAC 2
#define TAG_COMMENTS 3
#define TAG_ERROR 4

#include <float.h>
#include <limits.h>


const char *tag_names [] = {
    "EOF", "LONG", "FRAC", "COMMENTS", "ERROR"
};

struct Position {
    int line, pos, index;
};

void print_pos(struct Position *p) {
    printf("(%d,%d)", p->line, p->pos);
}

struct Fragment {
    struct Position starting, following;
};

typedef struct Fragment YYLTYPE;

void print_frag(struct Fragment *f) {
    print_pos(&(f->starting));
    printf("-");
    print_pos(&(f->following));
}

union Token {
    char *word;
    long long_value;
    long numerator_value;
    long denumerator_value;
};

typedef union Token YYSTYPE;

int continued;
struct Position cur;

#define YY_USER_ACTION                       \
{                                            \
    int i;                                   \
    if (!continued)                          \
        yylloc->starting = cur;              \
    continued = 0;                           \
                                             \
    for (i = 0; i < yyleng; i++) {           \
        if (yytext[i] == '\n') {             \
            cur.line++;                      \
            cur.pos = 1;                     \
        } else {                             \
            cur.pos++;                       \
        }                                    \
        cur.index++;                         \
    }                                        \
    yylloc->following = cur;                 \
}

long size;

void init_scanner(char *program) {
    continued = 0;
    cur.line = 1;
    cur.pos = 1;
    cur.index = 0;
    yy_scan_string(program);
}

void err(const char *msg) {
    printf("ERROR");
    print_pos(&cur);
    printf(": %s\n", msg);
}

%}

SPACE [ \t\r]+
DIGIT [0-9]
NUM_LIT {DIGIT}+
FRAC_LIT {DIGIT}+\\{DIGIT}+
COMMENTS [\{(.|\n)*\} | \(\*(.|\n)*\*\)]

%%
{NUM_LIT} {
    char *endptr;
    //printf("544444444444");
    long value = strtol(yytext, &endptr, 10);
    if (value > LONG_MAX) {
        return TAG_ERROR;
    }
	yylval->long_value = value;
	return TAG_LONG;
}
{FRAC_LIT} {
    char *endptr;
    char *istr = strtok(yytext, "/");
    long num = strtol(istr, &endptr, 10);
    long denum = strtol(yytext, &endptr, 10);
	if (num > LONG_MAX || denum > LONG_MAX) {
        return TAG_ERROR;
    }
	yylval->numerator_value = num;
    yylval->denumerator_value = denum;
	return TAG_FRAC;
}
{COMMENTS} {
    print_frag(yylloc);
    printf(" Comment\n");
    BEGIN(0);
}
. {
    err("");
    yylval->word = (char*)("");
	return TAG_ERROR;
}
%%

int main(int argc, const char **argv) {
    int tag;
    YYSTYPE token;
    YYLTYPE coords;
    long size_str;
    char *str;
    FILE *input;
    input = fopen(argv[1], "rb");
    if (input == NULL) {
        fputs("cannot open file", stderr);
        exit(1);
    }
    fseek(input, 0, SEEK_END);
    size_str = ftell(input);
    rewind(input);
    
    str = (char*)malloc(sizeof(char)*(size_str+1));
    if (str == NULL) {
        fputs("malloc error", stderr);
        exit(1);
    }
    fread(str, sizeof(char), size_str, input);
    str[size_str] = '\0';
    fclose(input);
    init_scanner(str);
    //printf("DDDDDDDDDDDDDDDDD");
    do {
        tag = yylex(&token, &coords);
        printf("%s ", tag_names[tag]);
        print_frag(&coords);
        
        if (tag == TAG_ERROR) {
            printf(": %s\n", token.word);
        }
        else if (tag == TAG_LONG) {
            printf(": %ld\n", token.long_value);
        }
        else if (tag == TAG_FRAC) {
            printf(": %ld/%ld\n", token.numerator_value, token.denumerator_value);
        }
        else {
            printf("\n");
        }
    } while (tag != TAG_EOF);
    printf("\n");
    free(str);
    return 0;
}