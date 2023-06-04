import abc
import enum
import re
import sys
from functools import reduce
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

memory_dict = {"H": 10, "V": 10}

class SemanticError(pe.Error):
    pass


class RepeatedVariable(SemanticError):
    def __init__(self, pos, varname):
        self.pos = pos
        self.varname = varname

    @property
    def message(self):
        return f'Повторная переменная {self.varname}'


class UnknownVar(SemanticError):
    def __init__(self, pos, varname):
        self.pos = pos
        self.varname = varname

    @property
    def message(self):
        return f'Необъявленная переменная {self.varname}'



class Type_of_Entity(enum.Enum):
    Struct = "struct"
    Enum = "enum"
    Union = "union"

class TypeWeight(enum.Enum):
    INTEGER = 4
    DOUBLE = 8
    CHAR = 4
    FLOAT = 8

class Type(enum.Enum):
    Integer = "INTEGER"
    Double = "DOUBLE"
    Char = "CHAR"
    Float = "FLOAT"


class Entity(abc.ABC):
    # @abc.abstractmethod
    # def check(self, vars):
        pass


class Expr(abc.ABC):
    @abc.abstractmethod
    def check(self, vars):
        pass
    @abc.abstractmethod
    def count_memory(self):
        pass


@dataclass
class Empty_Expr(Expr):
    def check(self, vars):
        pass
    def count_memory(self):
        pass
    pass


class Expr_Other(abc.ABC):
    # @abc.abstractmethod
    # def check(self, vars):
    @abc.abstractmethod
    def count_memory(self):
        pass


@dataclass
class Empty_Expr_Other(Expr_Other):
    pass


@dataclass
class Var_Expr_Other(Expr_Other):
    types: Type
    value: list[str]
    # value_coords: pe.Fragment
    # @pe.ExAction
    # def create(attrs, coords, res_coord):
    #     types, value = attrs
    #     ctypes, cvalue = coords
    #     return Var_Expr_Other(types, value, cvalue)
    def count_memory(self):
        # print(self.types)
        # return 10
        if self.types == 'INTEGER' or self.types == 'CHAR':
            return 4 * len(self.value)
        return 8 * len(self.value)


@dataclass
class Other_Body:
    name: str  
    name_coords: pe.Position
    statements: list[Expr_Other]
    # @staticmethod
    # def create(n, st):
    @pe.ExAction
    def create(attrs, coords, res_coord):
        # print('-------------')
        if len(coords) == 2:
            name, statements = attrs
            cname, cstatements = coords
            return Other_Body(name, cstatements.start, statements)
        if len(coords) == 4:
            name, statements = attrs
            cname, clbrace, cstatements, crbrace = coords
            return Other_Body(name, cstatements.start, statements)
        if len(coords) == 3:
            st, = attrs
            name = ""
            clbrace, cstatements, crbrace = coords
            return Other_Body(name, cstatements.start, st)
        # print("++++++++++++++++++")
        # return action
    def check(self, vars):
        # print("====================")
        if not(isinstance(self.statements, list)):
            # print(self.statements)
            return
        for statement in self.statements:
            fields = set()
            # print("====================")
            if isinstance(statement, Var_Expr_Other):
                for value in statement.value:
                    if value in fields:
                        raise RepeatedVariable(statement.value_coords, value)
                    fields.add(value)
            if isinstance(statement, Block_Expr_Other):
                # print(statement.body)
                statement.check(vars)            
                # for elem in statement.body:
                # print("====================")        
                elem = statement.body
                # print(vars, elem.body.name)
                for var in elem.var:
                    # print("====================")
                    if var in fields:
                        # print("====================")
                        raise RepeatedVariable(elem.var_coord, var)
                    # print("====================")
                    fields.add(var)
                if elem.body.name not in vars and elem.body.name != '':
                    raise UnknownVar(elem.body.name_coords, elem.body.name)
                
    def count_memory(self):
        if not(isinstance(self.statements, list)):
                
                return self.statements.count_memory()
        res_memo = 0
        for statement in self.statements:
            if isinstance(statement, Var_Expr_Other):
                # print("ffffffffffffffff")
                res_memo += statement.count_memory()
            if isinstance(statement, Block_Expr_Other): 
                # print("dsssssssss", statement)
                res_memo += statement.body.count_memory()
        return res_memo

@dataclass
class Other_Entity(Entity):
    types: Type_of_Entity
    body: Other_Body
    var: list[str]  ## n
    var_coord: pe.Fragment
    @pe.ExAction
    def create(attrs, coords, res_coord):
        types, body, var = attrs
        ctype, cbody, cvar = coords
        return Other_Entity(types, body, var, cvar)
    def check(self, vars):
        # print(self.body)
        # print(self.body.statements, '+++++++++++++')
        # if isinstance(self.body.statements, list):
            
        #     # print("dddddddddddd")
        #     st_name = self.body.name
        #     var_names = self.var 
        #     # print(vars, self.body.name, var_names)
        #     for var in var_names:
        #         if var in vars:
        #             raise RepeatedVariable(self.var_coord, var)
        #         vars.add(var)
        #     if st_name in vars and st_name not in var_names:
        #         raise RepeatedVariable(self.body.name_coords, st_name)
        #     vars.add(st_name)
        # print("============")
        self.body.check(vars)
        # print(self.var, '--------------')
        # print("============")
        if isinstance(self.body.statements, list):
            print("Memory used for", self.body.name, self.body.count_memory())
        if self.body.name not in memory_dict:
            memory_dict[self.body.name] = self.body.count_memory()
        # print(memory_dict, 'ddddddddddddddddd')

    def count_memory(self):
        if not(isinstance(self.body.statements, list)):
            name = self.body.statements.var_name
            m = re.findall('\[(.+?)\]', name)
            # print([memory_dict[i] for i in m], "=========")
            if m:
                return memory_dict[self.body.name] * reduce(lambda x, y: x*y, [memory_dict[i] for i in m])
        return memory_dict[self.body.name]

@dataclass
class Block_Expr_Other(Expr_Other):
    body: list[Other_Entity]
    def check(self, vars):
        if isinstance(self.body.body.statements, list):
            
            # print("dddddddddddd")
            st_name = self.body.body.name
            var_names = self.body.var 
            # print(vars, self.body.name, var_names)
            for var in var_names:
                if var in vars:
                    raise RepeatedVariable(self.body.var_coord, var)
                if var != '':
                    vars.add(var)
            if st_name in vars and st_name not in var_names:
                raise RepeatedVariable(self.body.body.name_coords, st_name)
            if st_name != '':
                vars.add(st_name)
        # print("============")
        # print(self.body)
        self.body.check(vars)
    def count_memory(self):
        pass


@dataclass
class Var_Expr(Expr):
    varname: str  
    varname_coord: pe.Position
    @pe.ExAction
    def create(attrs, coords, res_coord):
        name, = attrs
        cname, = coords
        return Var_Expr(name, cname)
    def check(self, var):
        if self.varname not in var:
            return UnknownVar(self.varname, self.varname_coord)
    def count_memory(self):
        return 4

@dataclass
class SizeofExpr(Expr):
    name: str   ##n
    name_coord: pe.Position
    value: Type_of_Entity
    @pe.ExAction
    def create(attrs, coords, res_coord):
        # print(attrs)
        value, name = attrs[0]
        csizeof, clparen, cname, crparen = coords
        return SizeofExpr(name, cname, value)
    def check(self, var):
        if self.name not in var:
            return UnknownVar(self.name, self.name_coord)
    def count_memory(self):
        return 4


@dataclass
class BinOpExpr(Expr):
    left: Expr
    op: str
    right: Expr
    def check(self, vars):
        pass
    def count_memory(self):
        if self.op == '/':
            return 8
        else: return 4


@dataclass
class Const_Expr(Expr):
    value: typing.Any
    types: Type
    def check(self, vars):
        pass
    def count_memory(self):
        if self.types == 'INTEGER' or self.types == 'CHAR':
            return 4 
        return 8


@dataclass
class Statement:
    var_name: str  ## n
    var_name_coords: pe.Position
    expr: Expr
    @pe.ExAction
    def create(attrs, coords, res_coord):
        pass
        if len(coords) == 1:
            name, = attrs
            cname, = coords
            value = Empty_Expr()
        if len(coords) == 3:
            name, value = attrs
            cname, ceq, cvalue = coords
        return Statement(name, cname, value)
    def check(self, vars):
        # print(self.var_name, '-------')
        self.expr.check(vars)
        if isinstance(self.expr, Const_Expr):
            memory_dict[self.var_name] = self.expr.value
            print(self.var_name, "value", self.expr.value)
    def count_memory(self):
        # print(self.var_name)
        if isinstance(self.expr, Empty_Expr):
            return 4
        return self.expr.count_memory()


@dataclass
class Enum_Body:
    name: str  ## n
    name_coords: pe.Position
    statements: list[Statement]
    @pe.ExAction
    def create(attrs, coords, res_coord):
        # print('-------------')
        if len(coords) == 2:
            name, statements = attrs
            cname, cstatements = coords
            return Enum_Body(name, cstatements.start, statements)
        if len(coords) == 4:
            name, statements = attrs
            cname, clbrace, cstatements, crbrace = coords
            return Enum_Body(name, cstatements.start, statements)
        if len(coords) == 3:
            # print("=--------------")
            st, = attrs
            name = ""
            clbrace, cstatements, crbrace = coords
            return Enum_Body(name, cstatements.start, st)
    def check(self, vars):
        # print("fffffffffffffff")
        if not(isinstance(self.statements, list)):
            # print("dddddddddddddd")
            self.statements.check(vars)
            return
        for statement in self.statements:
            statement.check(vars)

    def count_memory(self):
        res_memo = 0
        if not(isinstance(self.statements, list)):
            # print("dddddddddddddd")
            return self.statements.count_memory()
        for statement in self.statements:
            res_memo += statement.count_memory()
        return res_memo


@dataclass
class Enum_Entity(Entity):
    body: Enum_Body
    var: list[str]  ## n
    var_coord: pe.Fragment
    @pe.ExAction
    def create(attrs, coords, res_coord):
        body, var = attrs
        cenum, cbody, cvar = coords
        return Enum_Entity(body, var, cvar)
    def check(self, vars):
        # if isinstance(self.body.statements, list):
            
        #     # print("dddddddddddd")
        #     st_name = self.body.name
        #     var_names = self.var 
        #     print(vars, self.body.name, var_names)
        #     for var in var_names:
        #         if var in vars:
        #             raise RepeatedVariable(self.var_coord, var)
        #         vars.add(var)
        #     if st_name in vars and st_name not in var_names:
        #         raise RepeatedVariable(self.body.name_coords, st_name)
        #     vars.add(st_name)
        self.body.check(vars)
        if isinstance(self.body.statements, list):
            print("Memory used for", self.body.name, self.body.count_memory())
            memory_dict[self.body.name] = self.body.count_memory()

    def count_memory(self):
        if not(isinstance(self.body.statements, list)):
            name = self.body.statements.var_name
            # print(name)
            m = re.findall('\[(.+?)\]', name)
            if m:
                # print([memory_dict[i] for i in m], "=========")
                return memory_dict[self.body.name] * reduce(lambda x, y: x*y, [memory_dict[i] for i in m])
        return memory_dict[self.body.name]

@dataclass
class Program:
    entities: list[Entity]
    def check(self):
        vars = set()
        st = set()
        for entity in self.entities:
            # print(entity)
            if isinstance(entity, Enum_Entity):
                var_defs = entity.var
                st_def = entity.body.name
                # print('----', st_def)
            elif isinstance(entity, Other_Entity):
                var_defs = entity.var
                st_def = entity.body.name
                # print('----', st_def)
            else:
                var_defs = []
                st_def = []
            for var_def in var_defs:
                if var_def in vars:
                    raise RepeatedVariable(entity.var_coord, var_def)
                if var_def != '':
                    vars.add(var_def)
            if st_def in st:
                raise RepeatedVariable(entity.body.name_coords, st_def)
            if st_def != '':
                st.add(st_def)
            entity.check(vars | st)


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


NProgram |= NEntity, ";", NRestEntities, lambda ent, pr: Program([ent] + pr)
NRestEntities |= NEntity, ";", NRestEntities, lambda ent, rent: [ent] + rent
NProgram |= lambda: []
NRestEntities |= lambda: []

NEntity |= KW_ENUM, NEntityBodyEnum, NEntityVar, Enum_Entity.create
NEntity |= NRestType, NEntityBody, NEntityVar, Other_Entity.create

# NEntityBodyEnum |= NEntityName, NOption1, Enum_Body
# NEntityBodyEnum |= NOption1, lambda t: Enum_Body("", t)

NEntityBodyEnum |= NEntityName, "{", NEnumList, "}", Enum_Body.create
NEntityBodyEnum |= NEntityName, NEnumListItem, Enum_Body.create
NEntityBodyEnum |= "{", NEnumList, "}", Enum_Body.create

NOption1 |= "{", NEnumList, "}"
NOption1 |= NEnumListItem, lambda eli: [eli]

NEnumList |= NEnumListItem, ",", NEnumList, lambda eli, reli: [eli] + reli
NEnumList |= NEnumListItem, lambda eli: [eli]
NEnumList |= lambda: []
NRestEnumList |= ",", NEnumListItem, NRestEnumList, lambda eli, reli: [eli] + reli
NRestEnumList |= lambda: []

NEnumListItem |= NIdent, "=", NArith, Statement.create
NEnumListItem |= NIdent, "=", NExpr, Statement.create
NEnumListItem |= NIdent, Statement.create


NExpr |= KW_SIZEOF, "(", NOption2, ")", SizeofExpr.create

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
NFactor |= NIdent, Var_Expr.create
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

NEntityVar |= NEntityName, NRestNames, lambda en, ren: [en] + ren
NEntityVar |= lambda: []
NRestNames |= ",", NEntityName, NRestNames, lambda en, ren: [en] + ren
NRestNames |= lambda: []

# NEntityBody |= NEntityName, NOption4, Other_Body
NEntityBody |= NEntityName, "{", NList, "}", Other_Body.create
NEntityBody |= NEntityName, NEnumListItem, Other_Body.create
NEntityBody |= "{", NList, "}", Other_Body.create

# NOption4 |= "{", NList, "}", lambda t: t
# NOption4 |= NEnumListItem, lambda t: [t]

NList |= NListItem, ";", NList, lambda li, rli: [li] + rli
NList |= lambda: []

NRestList |= NListItem, NRestList, lambda li, rli: [li] + rli
NRestList |= lambda: []

NListItem |= NEntity, Block_Expr_Other
NListItem |= NTypeName, NIdents, Var_Expr_Other
NIdents |= NIdent, NRestIdents, lambda ni, ri: [ni] + ri
NRestIdents |= ",", NIdent, NRestIdents, lambda ni, nis: [ni] + nis
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
            tree.check()
            print("Errors net")
    except pe.Error as e:
        print(f"Ошибка {e.pos}: {e.message}")
    except Exception as e:
        print(e)
