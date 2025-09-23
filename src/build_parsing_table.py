from itertools import chain

from src.grammar_utils import Grammar, Production
from src.table import Line
from src.util import is_nonterminal


def create_analysis_table(language: Grammar, starting_symbol: str) -> list[Line]:
    rule_positions = calculate_rule_positions(language)
    analysis_table = []
    counter = 0
    end_marker_set = False

    sorted_rules = []
    if starting_symbol in language.rules:
        sorted_rules.append(language.rules[starting_symbol])

    for nt, rule_obj in language.rules.items():
        if nt != starting_symbol:
            sorted_rules.append(rule_obj)

    for rule_obj in sorted_rules:
        production_sequences = [prod.symbols for prod in rule_obj.productions]

        for prod_index, prod_item in enumerate(rule_obj.productions):
            is_error_case = (prod_index == len(rule_obj.productions) - 1)
            target_pointer = counter + len(rule_obj.productions) - prod_index + sum(
                len(p.symbols) for p in rule_obj.productions[:prod_index])

            analysis_table.append(
                Line(counter, rule_obj.nonterminal, prod_item.first_set, shift=False, error=is_error_case,
                     pointer=target_pointer,
                     stack=False, end=False))
            counter += 1

        for seq_index, symbol_list in enumerate(production_sequences):
            for elem_index, elem in enumerate(symbol_list):
                first_collection = get_symbol_first(elem, language, rule_obj.productions[seq_index])
                next_pointer = determine_pointer(elem, symbol_list, elem_index, counter, rule_positions)
                is_end, end_marker_set = check_end_condition(elem, symbol_list, elem_index, end_marker_set)
                requires_stack = (elem_index != len(symbol_list) - 1) if is_nonterminal(elem) else False

                analysis_table.append(
                    Line(counter, elem, first_collection, shift=is_terminal_symbol(elem), error=True,
                         pointer=next_pointer, stack=requires_stack,
                         end=is_end))
                counter += 1

    return analysis_table


def calculate_rule_positions(language: Grammar) -> dict[str, int]:
    rule_mapping = {}
    position = 0
    for rule_obj in language.rules.values():
        rule_mapping[rule_obj.nonterminal] = position
        position += sum(len(prod.symbols) + 1 for prod in rule_obj.productions)
    return rule_mapping


def get_symbol_first(symbol_name: str, language: Grammar, prod_item: Production) -> list[str]:
    if is_nonterminal(symbol_name):
        return list(set(chain.from_iterable(prod.first_set for prod in language.rules[symbol_name].productions)))
    return prod_item.first_set if symbol_name == "ε" else [symbol_name]


def determine_pointer(symbol_name: str, symbol_sequence: list[str], current_index: int, current_position: int,
                      rule_mapping: dict[str, int]) -> int | None:
    if is_nonterminal(symbol_name):
        return rule_mapping[symbol_name]
    return None if current_index == len(symbol_sequence) - 1 else current_position + 1


def check_end_condition(symbol_name: str, symbol_sequence: list[str], index_val: int, end_flag: bool) -> (bool, bool):
    end_condition = not end_flag and index_val == len(symbol_sequence) - 1 and is_terminal_symbol(symbol_name)
    return end_condition, end_flag or end_condition


def is_terminal_symbol(symbol_name: str) -> bool:
    return not is_nonterminal(symbol_name) and symbol_name != "ε"
