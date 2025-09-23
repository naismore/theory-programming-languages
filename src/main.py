import re
import sys

from lab6.main import task
from src.build_parsing_table import create_analysis_table
from src.check_line import validate_input_sequence
from src.grammar import simplify_grammar, eliminate_direct_recursion, eliminate_indirect_recursion, remove_unused_rules, \
    compute_directing_sets
from src.grammar_utils import parse_grammar_from_text, parse_grammar_with_first_sets, save_grammar
from src.grammar_validation import validate_language, verify_ll1_compatibility
from src.table import write_table, read_table


def process_task1() -> None:
    with open("new-grammar.txt", "r", encoding="utf-8") as f:
        language = parse_grammar_with_first_sets(f.readlines())

    table = create_analysis_table(language, list(language.rules.keys())[0])
    write_table(table)


def process_task2(input_string: str) -> str:
    table_data = read_table()
    return validate_input_sequence(input_string.split(), table_data)


def process_task3() -> str | None:
    with open("grammar.txt", "r", encoding="utf-8") as f:
        language, start_nt = parse_grammar_from_text(f.readlines())

    validation_result = validate_language(language, start_nt)

    if validation_result:
        return validation_result

    language = simplify_grammar(language)

    language = eliminate_indirect_recursion(language)

    language = eliminate_direct_recursion(language)

    language = remove_unused_rules(language, start_nt)

    start_rule = language.rules[start_nt]

    requires_new_axiom = False
    if len(start_rule.productions) > 1:
        requires_new_axiom = True
    elif start_rule.productions and (start_rule.nonterminal in start_rule.productions[0].symbols or (
            start_rule.productions[0].symbols and start_rule.productions[0].symbols[-1].startswith('<') and
            start_rule.productions[0].symbols[-1].endswith('>'))):
        requires_new_axiom = True

    if requires_new_axiom:
        language.add_production("<axiom>", [start_nt, "#"], [])
        start_nt = "<axiom>"

    language = compute_directing_sets(language, start_nt)

    save_grammar(language, start_nt)

    ll1_issue = verify_ll1_compatibility(language)
    if ll1_issue:
        return ll1_issue

    return None


def process_task4() -> None:
    if len(sys.argv) != 2:
        print(f'Usage: python {sys.argv[0]} <input-file>')
        return

    input_file = sys.argv[1]

    token_list = task(input_file)

    input_line = " ".join(token.type for token in token_list)

    error_msg = process_task3()

    if error_msg:
        print(error_msg)
        return

    process_task1()
    result = process_task2(input_line)
    if result != "Ok":
        pattern = r"Error at index (\d+): '([^']+)'.*"
        match = re.match(pattern, result)
        if match:
            index_val = int(match.group(1))
            symbol_name = match.group(2)
            print(f"Index: {token_list[index_val].pos} ({token_list[index_val].value})")
            print(f"Symbol: {symbol_name}")

    print(result)


if __name__ == "__main__":
    process_task4()




