from src.build_parsing_table import is_terminal_symbol
from src.grammar_utils import Grammar


def check_grammar_reachability(language: Grammar, start_symbol: str) -> str | None:
    reachable_symbols = set()
    processing_queue = [start_symbol]

    while processing_queue:
        current = processing_queue.pop()
        if current in reachable_symbols:
            continue
        reachable_symbols.add(current)

        if current in language.rules:
            for prod in language.rules[current].productions:
                for sym in prod.symbols:
                    if sym in language.rules and sym not in reachable_symbols:
                        processing_queue.append(sym)

    all_nt = set(language.rules.keys())
    unreachable_nt = all_nt - reachable_symbols

    return None if len(unreachable_nt) == 0 else "Grammar is not reachable from start symbol. Symbols" + ",".join(
        unreachable_nt)


def check_grammar_productivity(language: Grammar) -> str | None:
    productive_nt = set()
    changed = True

    for nonterminal, rule_obj in language.rules.items():
        for prod in rule_obj.productions:
            if all(is_terminal_symbol(sym) or sym == "ε" for sym in prod.symbols):
                productive_nt.add(nonterminal)
                break

    while changed:
        changed = False
        for nonterminal, rule_obj in language.rules.items():
            if nonterminal in productive_nt:
                continue

            for prod in rule_obj.productions:
                if all(is_terminal_symbol(sym) or sym == "ε" or sym in productive_nt for sym in prod.symbols):
                    productive_nt.add(nonterminal)
                    changed = True
                    break

    all_nt = set(language.rules.keys())
    unproductive_nt = all_nt - productive_nt

    if unproductive_nt:
        dependency_graph = {nt: set() for nt in all_nt}

        for nonterminal, rule_obj in language.rules.items():
            for prod in rule_obj.productions:
                for sym in prod.symbols:
                    if sym in language.rules:
                        dependency_graph[nonterminal].add(sym)

        cyclic_unproductive = set()
        for nt in unproductive_nt:
            if all(dep in unproductive_nt for dep in dependency_graph[nt]):
                cyclic_unproductive.add(nt)

        if cyclic_unproductive:
            return "Grammar is not productive. This nonterminals create a cycle: " + ",".join(
                sorted(cyclic_unproductive))

    return None if len(unproductive_nt) == 0 else "Grammar is not productive."


def verify_ll1_compatibility(language: Grammar) -> str | None:
    conflict_list = []

    for nonterminal, rule_obj in language.rules.items():
        if len(rule_obj.productions) <= 1:
            continue

        directing_sets_list = []
        for i, prod in enumerate(rule_obj.productions):
            directing_set = set(prod.first_set)
            directing_sets_list.append((i, directing_set))

        for i in range(len(directing_sets_list)):
            for j in range(i + 1, len(directing_sets_list)):
                set1 = directing_sets_list[i][1]
                set2 = directing_sets_list[j][1]
                common_symbols = set1 & set2

                if common_symbols:
                    prod1_str = ' '.join(rule_obj.productions[directing_sets_list[i][0]].symbols)
                    prod2_str = ' '.join(rule_obj.productions[directing_sets_list[j][0]].symbols)
                    conflict_list.append(
                        f"{nonterminal}: '{prod1_str}' and '{prod2_str}' have common symbols {sorted(common_symbols)}")

    if conflict_list:
        return "Grammar is not LL(1). Directing set conflicts:\n" + "\n".join(conflict_list)

    return None


def validate_language(language: Grammar, start_symbol: str) -> str | None:
    reachability_issue = check_grammar_reachability(language, start_symbol)
    if reachability_issue:
        return reachability_issue

    productivity_issue = check_grammar_productivity(language)
    if productivity_issue:
        return productivity_issue

    return None