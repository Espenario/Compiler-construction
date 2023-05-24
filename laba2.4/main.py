import re
from dataclasses import dataclass
from enum import Enum, auto
from queue import Queue
from typing import List, Optional, Union
from collections import defaultdict


class Tag(Enum):
    ERROR = auto()
    TERM = auto()
    NTERM = auto()
    AXIOM = auto()
    COMMENT = auto()
    OPEN = auto()
    CLOSE = auto()
    ITERSTART = auto()
    ITEREND = auto()
    CONCAT = auto()
    SEPARATOR = auto()
    UNMATCHED = auto()
    END = auto()


@dataclass
class Token:
    """Represents tokens for lexical analysis."""

    tag: Tag
    value: str = ""


@dataclass
class CoordsToken(Token):
    start_idx: int = 0
    end_idx: int = 0

    def __repr__(self):
        return f"{self.tag} ({self.start_idx}, {self.end_idx}): {self.value}"

class Lexer:
    """Performs lexical analysis of input data."""

    def __init__(self, config: dict):
        self.config = config
        self._re_mapping = {
            r"'.*\n": Tag.COMMENT,
            r"<axiom <({})>>\n".format(config["nonterminal"]): Tag.AXIOM,
            config["open"]: Tag.OPEN,
            config["close"]: Tag.CLOSE,
            config["iter_start"]: Tag.ITERSTART,
            config["iter_end"]: Tag.ITEREND,
            config["terminal"]: Tag.TERM,
            config["nonterminal"]: Tag.NTERM,   
            config["separator"]: Tag.SEPARATOR,
        }
        if config["concatenation"]:
            self._re_mapping[config["concatenation"]] = Tag.CONCAT

    def _match_token(self, input_str: str) -> Token:
        for pattern, tag in self._re_mapping.items():
            matched = re.match(pattern, input_str)
            if matched:
                return Token(tag=tag, value=matched.group())

        return Token(tag=Tag.UNMATCHED, value=input_str[0])

    def tokenize(self, input_str: str) -> Queue:
        tokens = Queue()
        idx = 0

        while idx < len(input_str):
            token = self._match_token(input_str[idx:])
            if token.tag == Tag.UNMATCHED and token.value.isspace() or token.tag == Tag.COMMENT:
                idx += len(token.value)
            else:
                if token.tag == Tag.AXIOM:
                    axiom_value = re.search(self.config["nonterminal"], token.value).group(0) # type: ignore
                    tokens.put(CoordsToken(Tag.AXIOM, axiom_value, idx, idx + len(token.value)))
                else:
                    tokens.put(CoordsToken(token.tag, token.value, idx, idx + len(token.value)))
                idx += len(token.value)

        tokens.put(CoordsToken(Tag.END, "", idx+1, idx+1))
        return tokens
config = {
    "open": "<",
    "close": ">",
    "iter_start": "{",
    "iter_end": "}",
    "terminal": r"[a-z\(\)\+\-\*\/]",
    "nonterminal": r"[A-Z]'?",
    "separator": "\n",
    "concatenation": "",
}
class Nonterminal:
    def __init__(self, symbol, rule_id=0):
        self.symbol = symbol
        self.rule_id = rule_id
        self.children = []

    def __eq__(self, other):
        return (isinstance(other, Nonterminal) and
                self.symbol == other.symbol)

    def __hash__(self):
        return hash(self.symbol)

    def __str__(self):
        return self.symbol
    
    def print(self, indent):
        print(indent + str(self) + ":")
        for child in self.children:
            child.print(indent + "\t")


class Terminal:
    def __init__(self, symbol):
        self.symbol = symbol

    def __eq__(self, other):
        return (isinstance(other, Terminal) and
                self.symbol == other.symbol)

    def __hash__(self):
        return hash(self.symbol)

    def __str__(self):
        return self.symbol
    
    def print(self, indent):
        print(indent + str(self))
# ```
# <Grammar> ::= <Rules>.

# <Rules> ::= <Rule> <RestRules>.
# <RestRules> ::= <Sep> <Rule> <RestRules> | .

# <Rule> ::= <Open> <Nterm> <RHS> <Close>.

# <RHS> ::= <RHSTerm> <RestRHS>.
# <RestRHS> ::= <Alt> <RHSTerm> <RestRHS> | .

# <RHSTerm> ::= <RHSFactor> <RestRHSTerm>.
# <RestRHSTerm> ::= <Concat> <RHSFactor> <RestRHSTerm> | .

# <RHSFactor> ::= <Term> | <Nterm> | <Group> | <Iter> | <Empty>.

# <Group> ::= <GroupStart> <RHS> <GroupEnd>.
# <Iter> ::= <IterStart> <RHS> <IterEnd>.

# ```

# T = `{Term, Nterm, Open, Close, $}`,

# N = `{Grammar, Rules, RestRules, Rule, RHS, RestRHS, RHSTerm, RestRHSTerm, RHSFactor, Group, Iter}`,

# S = `Grammar`
test_str = """<E    <T {<
            <+>
            <->
          > T}>>
<T    <F {< 
            <*> 
            </>
          > F}>>
<F    <n>
      <- F>
      <( E )>>"""
@dataclass
class Empty:
    symbol: str = ''


@dataclass
class Terminal:
    symbol: str

    def __hash__(self):
        return hash(self.symbol)


@dataclass
class Nonterminal:
    symbol: str

    def __eq__(self, other):
        return isinstance(other, Nonterminal) and self.symbol == other.symbol

    def __hash__(self):
        return hash(self.symbol)


@dataclass
class GroupNode:
    value: Optional[None]


@dataclass
class IterNode:
    value: Optional[None]


@dataclass
class AltNode:
    nodes: List[Union[Empty, Terminal, Nonterminal, GroupNode, IterNode]]


@dataclass
class RHS:
    nodes: List[AltNode]


@dataclass
class Rule:
    lhs: Nonterminal
    rhs: RHS
class Parser:
    """Performs syntax analysis of input data."""

    def parse(self, tokens: Queue) -> tuple[list[Rule], set[Nonterminal]]:
        nonterminals = set()

        def rules() -> list[Rule]:
            """<Rules> ::= <Rule> <RestRules>."""
            return rest_rules([rule()])

        def rest_rules(rules) -> list[Rule]:
            """<RestRules> ::= <Sep> <Rule> <RestRules> | ."""
            if tokens.queue[0].tag == Tag.SEPARATOR:
                tokens.get()
                rules.append(rule())
                return rest_rules(rules)
            return rules

        def rule():
            """<Rule> ::= <Open> <Nterm> <RHS> <Close>."""
            assert tokens.get().tag == Tag.OPEN
            lhs = tokens.get()
            assert lhs.tag == Tag.NTERM
            nonterminals.add(Nonterminal(lhs.value))
            rhs_ = rhs()
            assert tokens.get().tag == Tag.CLOSE
            return Rule(Nonterminal(lhs.value), rhs_)

        def rhs():
            """<RHS> ::= <RHSTerm> <RestRHS>."""
            return RHS(rest_rhs([rhs_term()]))

        def rest_rhs(terms):
            """<RestRHS> ::= <Alt> <RHSTerm> <RestRHS> | ."""
            if tokens.queue[0].tag == Tag.SEPARATOR:
                tokens.get()
                terms.append(rhs_term())
                return rest_rhs(terms)
            return terms

        def rhs_term():
            """<RHSTerm> ::= <RHSFactor> <RestRHSTerm>."""
            return AltNode(rest_rhs_term([rhs_factor()]))

        def rest_rhs_term(factors):
            """<RestRHSTerm> ::= <Concat> <RHSFactor> <RestRHSTerm> | ."""
            if tokens.queue[0].tag == Tag.CONCAT:
                tokens.get()
                factors.append(rhs_factor())
                return rest_rhs_term(factors)
            if tokens.queue[0].tag in [
                Tag.TERM,
                Tag.NTERM,
                Tag.OPEN,
                Tag.ITERSTART,
            ]:
                factors.append(rhs_factor())
                return rest_rhs_term(factors)
            return factors

        def rhs_factor():
            """<RHSFactor> ::= (<Term> | <Nterm>
                                | <Open> <RHS> <Close>
                                | <IterStart> <RHS> <IterEnd>)?."""
            if tokens.queue[0].tag == Tag.CLOSE:
                return Empty()
            token = tokens.get()
            
            if token.tag == Tag.SEPARATOR:
                token = tokens.get()
            if token.tag == Tag.TERM:
                return Terminal(token.value)
            if token.tag == Tag.NTERM:
                nonterminals.add(Nonterminal(token.value))
                return Nonterminal(token.value)
            if token.tag == Tag.OPEN:
                rhs_ = rhs()
                assert tokens.get().tag == Tag.CLOSE
                return GroupNode(rhs_)
            if token.tag == Tag.ITERSTART:
                rhs_ = rhs()
                assert tokens.get().tag == Tag.ITEREND
                return IterNode(rhs_)
            raise Exception(f"Wrong Factor <{token.tag}> with value <{token.value}>")

        rules_ = rules()
        return rules_, nonterminals
lexer = Lexer(config)
tokens = lexer.tokenize(test_str)
rules, nonterminals = Parser().parse(tokens)
print(nonterminals)

for rule in rules:
    print(rule)
def first(rules, nonterminals):
    rules_by_nts = defaultdict(list)

    for rule in rules:
        rules_by_nts[rule.lhs].append(rule)

    def first_rec(curr, first_set):
        if isinstance(curr, RHS):
            for node in curr.nodes:
                first_set |= first_rec(node, first_set)
            return first_set
        elif isinstance(curr, AltNode):
            return first_set | first_rec(curr.nodes[0], first_set)
        elif isinstance(curr, IterNode):
            return first_set | Empty() | first_rec(curr.value, first_set)
        elif isinstance(curr, GroupNode):
            return first_set | first_rec(curr.value, first_set)
        elif isinstance(curr, Terminal):
            first_set.add(curr)
            return first_set
        elif isinstance(curr, Nonterminal):
            for rule in rules_by_nts[curr]:
                first_set |= first_rec(rule.rhs, first_set)
            return first_set
        
    for nt in nonterminals:
        print(nt, "- FIRST:", first_rec(rules_by_nts[nt][0].rhs, set()))
first(rules, nonterminals)