from src.grammar_utils import Grammar, Rule, Production
from src.util import is_nonterminal


def simplify_grammar(language: Grammar) -> Grammar:
    new_language = Grammar({})

    for nonterminal, rule_obj in language.rules.items():
        grouped_productions = group_by_common_prefix(rule_obj.productions)

        if len(grouped_productions) == len(rule_obj.productions):
            new_language.rules[nonterminal] = rule_obj
            continue

        updated_rule = Rule(nonterminal, [])

        for prefix_val, prod_list in grouped_productions.items():
            if len(prod_list) == 1:
                updated_rule.productions.append(prod_list[0])
                continue

            new_nt = f"<{nonterminal.strip('<>')}'>"

            prefix_symbols = list(prefix_val)
            updated_rule.productions.append(Production(prefix_symbols + [new_nt], []))

            remaining_productions = []
            for prod_item in prod_list:
                suffix_part = prod_item.symbols[len(prefix_symbols):]
                remaining_productions.append(Production(suffix_part or ["ε"], []))

            new_language.rules[new_nt] = Rule(new_nt, remaining_productions)

        new_language.rules[nonterminal] = updated_rule

    if any(len(group_by_common_prefix(rule_obj.productions)) < len(rule_obj.productions) for rule_obj in
           new_language.rules.values()):
        return simplify_grammar(new_language)

    return new_language


def group_by_common_prefix(prod_list: list[Production]) -> dict[tuple, list[Production]]:
    if not prod_list:
        return {}

    result_map = {}
    processed_indices = set()

    for i, prod1 in enumerate(prod_list):
        if i in processed_indices:
            continue

        common_part = []
        matching_productions = [prod1]
        processed_indices.add(i)

        for j, prod2 in enumerate(prod_list[i + 1:], i + 1):
            if j in processed_indices:
                continue

            match_length = 0
            min_len = min(len(prod1.symbols), len(prod2.symbols))

            for k in range(min_len):
                if prod1.symbols[k] == prod2.symbols[k]:
                    match_length = k + 1
                else:
                    break

            if match_length > 0:
                if not common_part or match_length >= len(common_part):
                    if match_length > len(common_part):
                        common_part = prod1.symbols[:match_length]
                        matching_productions = [prod1, prod2]
                    else:
                        matching_productions.append(prod2)
                    processed_indices.add(j)

        if len(matching_productions) > 1:
            prefix_key = tuple(common_part)
            result_map[prefix_key] = matching_productions
        else:
            first_elem = prod1.symbols[0] if prod1.symbols else "ε"
            prefix_key = (f"{first_elem}_unique_{i}",)
            result_map[prefix_key] = [prod1]

    return result_map


def eliminate_direct_recursion(language: Grammar) -> Grammar:
    updated_language = Grammar({})

    for nonterminal, rule_obj in language.rules.items():
        recursive_prods = []
        non_recursive_prods = []

        for prod_item in rule_obj.productions:
            if prod_item.symbols and prod_item.symbols[0] == nonterminal:
                recursive_prods.append(prod_item.symbols[1:])
            else:
                non_recursive_prods.append(prod_item.symbols)

        if recursive_prods:
            new_nt = f"<{nonterminal.strip('<>')}r>"
            updated_language.rules[new_nt] = Rule(new_nt, [])

            updated_language.rules[nonterminal] = Rule(nonterminal, [])
            for prod_body in non_recursive_prods:
                clean_body = [] if prod_body == ["ε"] else prod_body
                new_body = clean_body + [new_nt]
                updated_language.rules[nonterminal].productions.append(Production(new_body, []))

            updated_language.rules[new_nt].productions = [Production(body + [new_nt], []) for body in
                                                          recursive_prods] + [Production(["ε"], [])]
        else:
            updated_language.rules[nonterminal] = rule_obj

    return updated_language


def create_dependency_map(language: Grammar) -> dict[str, set[str]]:
    dependencies = dict()
    for nonterminal, rule_obj in language.rules.items():
        for prod_item in rule_obj.productions:
            dependencies.setdefault(nonterminal, set())
            if prod_item.symbols and prod_item.symbols[0] in language.rules:
                dependencies[nonterminal].add(prod_item.symbols[0])
    return dependencies


def sort_topologically(dep_graph: dict[str, set[str]], start_nt: str) -> tuple[list[str], bool]:
    visited_nodes = []
    sorted_order = []

    def traverse(node: str) -> None:
        if node in visited_nodes:
            visited_nodes.append(node)
            return
        visited_nodes.append(node)
        for neighbor in dep_graph[node]:
            if neighbor != node:
                traverse(neighbor)
        sorted_order.append(node)

    traverse(start_nt)

    return sorted_order, len(visited_nodes) != len(sorted_order)


def eliminate_indirect_recursion(language: Grammar) -> Grammar:
    dep_graph = create_dependency_map(language)

    for node in dep_graph:
        order, has_indirect = sort_topologically(dep_graph, node)
        order = order[:-1]
        if not has_indirect:
            continue

        for i, a_i in enumerate(order):
            for j in range(i):
                a_j = order[j]
                new_prod_list = []

                for prod_item in language.rules[a_i].productions:
                    if prod_item.symbols and prod_item.symbols[0] == a_j:
                        for a_j_prod in language.rules[a_j].productions:
                            new_prod_list.append(Production(a_j_prod.symbols + prod_item.symbols[1:], []))
                    else:
                        new_prod_list.append(prod_item)

                language.rules[a_i].productions = new_prod_list

    return language


def remove_unused_rules(language: Grammar, start_symbol: str) -> Grammar:
    accessible = set()
    queue = [start_symbol]

    while queue:
        current_nt = queue.pop()
        if current_nt in accessible:
            continue
        accessible.add(current_nt)
        if current_nt in language.rules:
            for prod_item in language.rules[current_nt].productions:
                for sym in prod_item.symbols:
                    if sym in language.rules and sym not in accessible:
                        queue.append(sym)

    filtered_rules = {nt: rule for nt, rule in language.rules.items() if nt in accessible}
    return Grammar(filtered_rules)


def compute_directing_sets(language: Grammar, start_symbol: str) -> Grammar:
    first_collections = {}

    for rule_obj in language.rules.values():
        for prod_item in rule_obj.productions:
            for sym in prod_item.symbols:
                if not (is_nonterminal(sym)):
                    first_collections[sym] = {sym}

    for nonterminal in language.rules:
        first_collections[nonterminal] = set()

    changed_flag = True
    while changed_flag:
        changed_flag = False
        for nonterminal, rule_obj in language.rules.items():
            for prod_item in rule_obj.productions:
                all_epsilon = True
                for sym in prod_item.symbols:
                    if sym == "ε":
                        continue

                    if not (is_nonterminal(sym)):
                        if sym not in first_collections[nonterminal]:
                            first_collections[nonterminal].add(sym)
                            changed_flag = True
                        all_epsilon = False
                        break

                    for s in first_collections.get(sym, set()):
                        if s != "ε" and s not in first_collections[nonterminal]:
                            first_collections[nonterminal].add(s)
                            changed_flag = True

                    if "ε" not in first_collections.get(sym, set()):
                        all_epsilon = False
                        break

                if all_epsilon and "ε" not in first_collections[nonterminal]:
                    first_collections[nonterminal].add("ε")
                    changed_flag = True

    follow_collections = {nonterminal: set() for nonterminal in language.rules}

    follow_collections[start_symbol].add(language.rules[start_symbol].productions[0].symbols[-1])

    changed_flag = True
    while changed_flag:
        changed_flag = False
        for nonterminal, rule_obj in language.rules.items():
            for prod_item in rule_obj.productions:
                for i, sym in enumerate(prod_item.symbols):
                    if not (is_nonterminal(sym)) or sym == "ε":
                        continue

                    trailing_symbols = set()
                    all_epsilon = True

                    for j in range(i + 1, len(prod_item.symbols)):
                        next_sym = prod_item.symbols[j]
                        if next_sym == "ε":
                            continue

                        sym_first = first_collections.get(next_sym, {next_sym})
                        for s in sym_first:
                            if s != "ε":
                                trailing_symbols.add(s)

                        if "ε" not in sym_first:
                            all_epsilon = False
                            break

                    if all_epsilon or i == len(prod_item.symbols) - 1:
                        for follow_sym in follow_collections[nonterminal]:
                            if follow_sym not in follow_collections[sym]:
                                follow_collections[sym].add(follow_sym)
                                changed_flag = True

                    for s in trailing_symbols:
                        if s not in follow_collections[sym]:
                            follow_collections[sym].add(s)
                            changed_flag = True

    result_grammar = Grammar({})
    for nonterminal, rule_obj in language.rules.items():
        new_rule = Rule(nonterminal, [])
        for prod_item in rule_obj.productions:
            prod_first = compute_production_first(prod_item.symbols, first_collections)

            derives_epsilon = True
            for sym in prod_item.symbols:
                if sym == "ε":
                    continue
                sym_first = first_collections.get(sym, {sym})
                if "ε" not in sym_first:
                    derives_epsilon = False
                    break

            directing_collection = set()
            for s in prod_first:
                if s != "ε":
                    directing_collection.add(s)

            if derives_epsilon or "ε" in prod_first:
                directing_collection.update(follow_collections[nonterminal])

            new_prod = Production(symbols=prod_item.symbols,
                                  first_set=[s for s in directing_collection if s != "ε"])
            new_rule.productions.append(new_prod)

        result_grammar.rules[nonterminal] = new_rule

    return result_grammar


def compute_production_first(symbol_list: list[str], first_collections: dict[str, set[str]]) -> set[str]:
    if not symbol_list or symbol_list[0] == "ε":
        return {"ε"}

    result_set = set()
    all_epsilon = True

    for sym in symbol_list:
        if sym == "ε":
            continue

        if not (is_nonterminal(sym)):
            result_set.add(sym)
            all_epsilon = False
            break

        sym_first = first_collections.get(sym, set())
        for s in sym_first:
            if s != "ε":
                result_set.add(s)

        if "ε" not in sym_first:
            all_epsilon = False
            break

    if all_epsilon:
        result_set.add("ε")

    return result_set