import re
from dataclasses import dataclass


@dataclass
class Production:
    symbols: list[str]
    first_set: list[str]

    def add_first_set(self, first_collection: list[str]) -> None:
        self.first_set = first_collection


@dataclass
class Rule:
    nonterminal: str
    productions: list[Production]

    def add_production(self, symbol_list: list[str], first_collection: list[str]) -> None:
        self.productions.append(Production(symbol_list, first_collection))


@dataclass
class Grammar:
    rules: dict[str, Rule]

    def add_production(self, nonterminal: str, symbol_list: list[str], first_collection: list[str]) -> None:
        if nonterminal not in self.rules:
            self.rules[nonterminal] = Rule(nonterminal, [])
        self.rules[nonterminal].add_production(symbol_list, first_collection)


def parse_grammar_with_first_sets(content_lines: list[str]) -> Grammar:
    language = Grammar(dict())
    pattern = re.compile(r"^\s*(<.+>)\s*->(.*)\|\s*(.*)\s*$")

    for line in content_lines:
        match = pattern.match(line)
        if match:
            nonterminal, symbols, first_set = match.groups()
            language.add_production(nonterminal.strip(), symbols.strip().split(), first_set.strip().split())

    return language


def parse_grammar_from_text(content_lines: list[str]) -> tuple[Grammar, str]:
    language = Grammar(dict())
    pattern = re.compile(r"^\s*(<.+>)\s*->\s*(.*)$")
    start_symbol = None

    for line in content_lines:
        match = pattern.match(line)
        if match:
            nonterminal, symbols = match.groups()
            if start_symbol is None:
                start_symbol = nonterminal
            language.add_production(nonterminal.strip(), symbols.strip().split(), [])

    return language, start_symbol


def save_grammar(language: Grammar, axiom: str) -> None:
    with open("new-grammar.txt", "w", encoding="utf-8") as f:
        axiom_rule = language.rules[axiom]
        for prod in axiom_rule.productions:
            f.write(f"{axiom_rule.nonterminal} -> {' '.join(prod.symbols)} | {' '.join(sorted(prod.first_set))}\n")
        for rule_obj in language.rules.values():
            if rule_obj.nonterminal == axiom:
                continue
            for prod in rule_obj.productions:
                f.write(
                    f"{rule_obj.nonterminal} -> {' '.join(prod.symbols)} | {' '.join(sorted(prod.first_set))}\n")
