def is_nonterminal(symbol_name: str) -> bool:
    return symbol_name.startswith('<') and symbol_name.endswith('>') and len(symbol_name) > 2