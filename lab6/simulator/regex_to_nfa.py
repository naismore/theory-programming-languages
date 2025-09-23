from dataclasses import dataclass


class RegexNode:
    def __init__(self, value: str, left: 'RegexNode' = None, right: 'RegexNode' = None):
        self.value = value
        self.left = left
        self.right = right


class State:
    def __init__(self):
        self.transitions: dict[str, list['State']] = {}
        self.epsilon_transitions: list['State'] = []

    def add_transition(self, symbol: str, state: 'State') -> None:
        if symbol not in self.transitions:
            self.transitions[symbol] = []
        self.transitions[symbol].append(state)

    def add_epsilon_transition(self, state: 'State') -> None:
        self.epsilon_transitions.append(state)


class NFA:
    def __init__(self, start_state: State, accept_state: State):
        self.start_state = start_state
        self.accept_state = accept_state


def is_literal(value: str) -> bool:
    return value not in '+*()|.^'


def parse_regex(expression: str) -> RegexNode:
    def parse(tokens: list[str]):
        def get_next() -> str | None:
            return tokens.pop(0) if tokens else None

        def parse_primary() -> RegexNode:
            token = get_next()
            if token == '\\':
                escaped = get_next()
                if is_literal(escaped):
                    tokens.insert(0, escaped)
                else:
                    return RegexNode(escaped)
            if is_literal(token):
                return RegexNode(token)
            elif token == '.':
                return RegexNode('any')
            elif token == '^':
                negated_node = parse_primary()
                return RegexNode('not', left=negated_node)
            elif token == '(':
                node = parse_expression()
                if get_next() != ')':
                    raise ValueError('Mismatched parentheses')
                return node
            raise ValueError(f'Unexpected token: {token}')

        def parse_factor() -> RegexNode:
            node = parse_primary()
            while tokens and tokens[0] in ('*', '+'):
                op = 'multiply' if get_next() == '*' else 'add'
                node = RegexNode(op, left=node)
            return node

        def parse_term() -> RegexNode:
            node = parse_factor()
            while tokens and tokens[0] and (is_literal(tokens[0]) or tokens[0] in ('(', '.', '^')):
                right = parse_factor()
                node = RegexNode('concat', left=node, right=right)
            return node

        def parse_expression() -> RegexNode:
            node = parse_term()
            while tokens and tokens[0] == '|':
                get_next()
                right = parse_term()
                node = RegexNode('or', left=node, right=right)
            return node

        return parse_expression()

    return parse(list(expression))


def build_nfa(node: RegexNode) -> NFA | None:
    if node is None:
        return None

    if node.value not in ('concat', 'or', 'add', 'multiply', 'any', 'not'):
        start = State()
        accept = State()
        start.add_transition(node.value, accept)
        return NFA(start, accept)
    elif node.value == 'any':
        start = State()
        accept = State()
        start.add_transition('ANY', accept)
        return NFA(start, accept)
    elif node.value == 'not':
        sub_nfa = build_nfa(node.left)
        start = State()
        accept = State()
        start.add_epsilon_transition(sub_nfa.start_state)
        sub_nfa.accept_state.add_transition('NOT', accept)
        start.add_transition('ANY', accept)
        return NFA(start, accept)
    elif node.value == 'concat':
        left_nfa = build_nfa(node.left)
        right_nfa = build_nfa(node.right)
        left_nfa.accept_state.add_epsilon_transition(right_nfa.start_state)
        return NFA(left_nfa.start_state, right_nfa.accept_state)
    elif node.value == 'or':
        start = State()
        accept = State()
        left_nfa = build_nfa(node.left)
        right_nfa = build_nfa(node.right)
        start.add_epsilon_transition(left_nfa.start_state)
        start.add_epsilon_transition(right_nfa.start_state)
        left_nfa.accept_state.add_epsilon_transition(accept)
        right_nfa.accept_state.add_epsilon_transition(accept)
        return NFA(start, accept)
    elif node.value == 'multiply':
        start = State()
        accept = State()
        sub_nfa = build_nfa(node.left)
        start.add_epsilon_transition(sub_nfa.start_state)
        start.add_epsilon_transition(accept)
        sub_nfa.accept_state.add_epsilon_transition(sub_nfa.start_state)
        sub_nfa.accept_state.add_epsilon_transition(accept)
        return NFA(start, accept)
    elif node.value == 'add':
        start = State()
        accept = State()
        sub_nfa = build_nfa(node.left)
        start.add_epsilon_transition(sub_nfa.start_state)
        sub_nfa.accept_state.add_epsilon_transition(sub_nfa.start_state)
        sub_nfa.accept_state.add_epsilon_transition(accept)
        return NFA(start, accept)

    raise ValueError(f'Unexpected node value: {node.value}')


@dataclass
class MachineState:
    is_finite: bool
    transitions: dict[str, set[str]]


def adapt_nfa(nfa: NFA) -> tuple[str, str, dict[str, MachineState]]:
    state_index: dict[State, str] = {}
    index = 0

    def assign_indices(state: State) -> None:
        nonlocal index
        if state not in state_index:
            state_index[state] = f'S{index}'
            index += 1
            for symbol, states in state.transitions.items():
                for s in states:
                    assign_indices(s)
            for s in state.epsilon_transitions:
                assign_indices(s)

    assign_indices(nfa.start_state)

    initial_state = state_index[nfa.start_state]
    finite_state = state_index[nfa.accept_state]

    machine: dict[str, MachineState] = {state_index[s]: MachineState(name == finite_state, {}) for s, name in
                                        state_index.items()}

    for state_iter, name in state_index.items():
        for symbol_iter, states_iter in state_iter.transitions.items():
            machine[name].transitions.setdefault(symbol_iter, set()).update(state_index[s] for s in states_iter)
        for s in state_iter.epsilon_transitions:
            machine[name].transitions.setdefault('ε', set()).add(state_index[s])

    symbols: set[str] = set()
    for state_iter in machine:
        trans = machine[state_iter].transitions
        for symbol_iter in trans:
            symbols.add(symbol_iter)

    for state_iter in machine:
        for symbol_iter in symbols:
            machine[state_iter].transitions.setdefault(symbol_iter, set())

    return initial_state, finite_state, machine


def process_regex(regex_pattern: str) -> tuple[str, str, dict[str, MachineState]]:
    tree = parse_regex(regex_pattern)
    nfa = build_nfa(tree)
    return adapt_nfa(nfa)
