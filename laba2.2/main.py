import abc
import enum
import re
import sys
import typing
from dataclasses import dataclass
from pprint import pprint

import parser_edsl as pe

# <Program> = <Entity> <Program> | <Eps>
# <Entity> = enum <EntityBodyEnum> <EntityVar> | <RestType> <EntityBody> <EntityVar>
# <EntityBodyEnum> = <EntityName> <Option1>
# <Option1> = { <EnumList> } | <EnumListItem>
# <EnumList> = <EnumListElem> <RestEnumList>
# <RestEnumList> = , <EnumListElem> <RestEnumList> | <Eps>
# <EnumListItem> = <Ident> <Option3>
# <Option3> = = <Arith> | = <Expr> | <Eps>
# <Expr> = sizeof(<Option2>)
# <Types> = enum | <RestType>
# <Option2> = <Types> <EntityName> | <TypeName>
# <Arith> = <Arith> + <Term> | <Arith> - <Term> | <Term>
# <Term> = <Term> * <Factor> | <Term> / <Factor> | <Factor>
# <Factor> = <Number> | <Ident> | ( <Arith> )
# <RestType> = struct | union
# <TypeName> = char | int | double
# <EntityName> = Varname_const
# <Number> = Integer_const | Real_const
# <Ident> = Varname_const
# <EntityVar> = <EntityName> <RestNames>
# <RestNames> = , <EntityName> <RestNames> | <Eps>l
# <EntityBody> = <EntityName> <Option4>
# <Option4> = { <List> } | <EnumListItem>
# <List> = <ListItem> <RestList>
# <RestList> = ; <ListItem> <RestList> | <Eps>
# <ListItem> = <Entity> | <TypeName> <Ident>


class Type_of_Entity(enum.Enum):
    Struct = "struct"
    Enum = "enum"
    Union = "union"


class Type(enum.Enum):
    Integer = "INTEGER"
    Double = "DOUBLE"
    Char = "CHAR"
    Float = "FLOAT"


class Entity(abc.ABC):
    pass


class Expr(abc.ABC):
    pass


@dataclass
class Empty_Expr(Expr):
    pass


class Expr_Other(abc.ABC):
    pass


@dataclass
class Empty_Expr_Other(Expr_Other):
    pass


@dataclass
class Var_Expr_Other(Expr_Other):
    types: Type
    value: list[str]


@dataclass
class Other_Body:
    name: str
    statements: list[Expr_Other]


@dataclass
class Other_Entity(Entity):
    types: Type_of_Entity
    body: Other_Body
    var: list[str]


@dataclass
class Block_Expr_Other(Expr_Other):
    body: list[Other_Entity]


@dataclass
class Var_Expr(Expr):
    varname: str


@dataclass
class SizeofExpr(Expr):
    name: str
    value: Type_of_Entity


@dataclass
class BinOpExpr(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass
class Const_Expr(Expr):
    value: typing.Any
    types: Type


@dataclass
class Statement:
    var_name: str
    expr: Expr


@dataclass
class Enum_Body:
    name: str
    statements: list[Statement]


@dataclass
class Enum_Entity(Entity):
    body: Enum_Body
    var: list[str]


@dataclass
class Program:
    entities: list[Entity]


INTEGER = pe.Terminal("INTEGER", "[0-9]+", int, priority=7)
REAL = pe.Terminal("REAL", "[0-9]+(\\.[0-9]*)?(e[-+]?[0-9]+)?", float)
VARNAME = pe.Terminal(
    "VARNAME",
    "\\**[A-Za-z][_A-Za-z0-9]*(\\[[A-Za-z][_A-Za-z0-9]*\\])*",
    str.upper,
)


def make_keyword(image):
    return pe.Terminal(
        image, image, lambda name: None, re_flags=re.IGNORECASE, priority=10
    )


KW_ENUM, KW_SIZEOF, KW_STRUCT, KW_CHAR, KW_INTEGER, KW_DOUBLE = map(
    make_keyword, "enum sizeof struct char int double".split()
)

KW_UNION, KW_FLOAT = map(make_keyword, "union float".split())

NProgram, NEntity, NEntityBodyEnum, NEnumList, NRestEnumList = map(
    pe.NonTerminal, "Program Entity EntityBodyEnum EnumList RestEnumList".split()
)

NEnumListItem, NExpr, NArith, NTerm, NFactor, NRestType, NTypes = map(
    pe.NonTerminal, "EnumListItem Expr Arith Term Factor RestType Types".split()
)

NTypeName, NEntityName, NNumber, NIdent, NEntityVar, NOption1 = map(
    pe.NonTerminal, "TypeName EntityName Number Ident EntityVar Option1".split()
)

NRestNames, NEntityBody, NList, NRestList, NListItem, NOption2 = map(
    pe.NonTerminal, "RestNames EntityBody List RestList ListItem Option2".split()
)

NOption3, NOption4, NIdents, NRestIdents, NRestEntities = map(
    pe.NonTerminal, "Option3 Option4 Idents RestIdents RestEntities".split()
)


NProgram |= NEntity, ";", NRestEntities, lambda ent, pr: Program(pr + [ent])
NRestEntities |= NEntity, ";", NRestEntities, lambda ent, rent: rent + [ent]
NProgram |= lambda: []
NRestEntities |= lambda: []

NEntity |= KW_ENUM, NEntityBodyEnum, NEntityVar, Enum_Entity
NEntity |= NRestType, NEntityBody, NEntityVar, Other_Entity

# NEntityBodyEnum |= NEntityName, NOption1, Enum_Body
# NEntityBodyEnum |= NOption1, lambda t: Enum_Body("", t)

NEntityBodyEnum |= NEntityName, "{", NEnumList, "}", Enum_Body
NEntityBodyEnum |= NEntityName, NEnumListItem, Enum_Body
NEntityBodyEnum |= "{", NEnumList, "}", lambda t: Enum_Body('', t)

NOption1 |= "{", NEnumList, "}"
NOption1 |= NEnumListItem, lambda eli: [eli]

NEnumList |= NEnumListItem, ",", NEnumList, lambda eli, reli: reli + [eli]
NEnumList |= NEnumListItem, lambda eli: [eli]
NEnumList |= lambda: []
NRestEnumList |= ",", NEnumListItem, NRestEnumList, lambda eli, reli: reli + [eli]
NRestEnumList |= lambda: []

NEnumListItem |= NIdent, "=", NArith, lambda t, r: Statement(t, r)
NEnumListItem |= NIdent, "=", NExpr, lambda t, r: Statement(t, r)
NEnumListItem |= NIdent, lambda t: Statement(t, Empty_Expr())


NExpr |= KW_SIZEOF, "(", NOption2, ")", lambda t: SizeofExpr(*t[::-1])

NTypes |= KW_ENUM, lambda: "enum"
NTypes |= NRestType, lambda t: t

NOption2 |= NTypes, VARNAME, lambda t, n: [t, n]
NOption2 |= NTypeName, lambda t: [t, ""]

NArith |= NArith, "+", NTerm, lambda l, r: BinOpExpr(l, "+", r)
NArith |= NArith, "-", NTerm, lambda l, r: BinOpExpr(l, "-", r)
NArith |= NTerm, lambda t: t

NTerm |= NTerm, "*", NFactor, lambda l, r: BinOpExpr(l, "*", r)
NTerm |= NTerm, "/", NFactor, lambda l, r: BinOpExpr(l, "/", r)
NTerm |= NFactor, lambda t: t

NFactor |= NNumber
NFactor |= NIdent, Var_Expr
NFactor |= "(", NArith, ")", lambda t: t

NRestType |= KW_STRUCT, lambda: "struct"
NRestType |= KW_UNION, lambda: "union"

NTypeName |= KW_CHAR, lambda: "CHAR"
NTypeName |= KW_INTEGER, lambda: "INTEGER"
NTypeName |= KW_DOUBLE, lambda: "DOUBLE"

NEntityName |= VARNAME
# NEntityName |= lambda: ''
NNumber |= INTEGER, lambda v: Const_Expr(v, Type.Integer)
NNumber |= REAL, lambda v: Const_Expr(v, Type.Float)

NIdent |= VARNAME

NEntityVar |= NEntityName, NRestNames, lambda en, ren: ren + [en]
NEntityVar |= lambda: []
NRestNames |= ",", NEntityName, NRestNames, lambda en, ren: ren + [en]
NRestNames |= lambda: []

# NEntityBody |= NEntityName, NOption4, Other_Body
NEntityBody |= NEntityName, "{", NList, "}", Other_Body
NEntityBody |= NEntityName, NEnumListItem, Other_Body
NEntityBody |= "{", NList, "}", lambda t: Other_Body('', t)

# NOption4 |= "{", NList, "}", lambda t: t
# NOption4 |= NEnumListItem, lambda t: [t]

NList |= NListItem, ";", NList, lambda li, rli: rli + [li]
NList |= lambda: []

NRestList |= NListItem, NRestList, lambda li, rli: rli + [li]
NRestList |= lambda: []

NListItem |= NEntity, Block_Expr_Other
NListItem |= NTypeName, NIdents, Var_Expr_Other
NIdents |= NIdent, NRestIdents, lambda ni, ri: ri + [ni]
NRestIdents |= ",", NIdent, NRestIdents, lambda ni, nis: nis + [ni]
NRestIdents |= lambda: []


p = pe.Parser(NProgram)
#p.print_table()

assert p.is_lalr_one()

p.add_skipped_domain("\\s")
p.add_skipped_domain("(//.*)|((/\\*)(.|\n)*?(\\*\\/))")
# p.add_skipped_domain('(/\\*)(.|\n)*?(\\*\\/)')


for filename in sys.argv[1:]:
    try:
        with open(filename) as f:
            tree = p.parse(f.read())
            pprint(tree)
    except pe.Error as e:
        print(f"Ошибка {e.pos}: {e.message}")
    except Exception as e:
        print(e)
