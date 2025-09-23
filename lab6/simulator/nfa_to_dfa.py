from .regex_to_nfa import MachineState


def fill_epsilon(machine: dict[str, MachineState]) -> dict[str, list[str]]:
    epsilon: dict[str, list[str]] = {}

    for state in machine:
        visited = set()
        stack = [state]

        while stack:
            vertex = stack.pop()

            if vertex not in visited:
                visited.add(vertex)

                if 'ε' not in machine[vertex].transitions:
                    continue
                for neighbor in machine[vertex].transitions['ε']:
                    if neighbor:
                        stack.append(neighbor)

        epsilon[state] = list(visited)

    return epsilon


def get_dependencies(states: list[str], epsilon: dict[str, list[str]]) -> list[str]:
    dependencies: set[str] = set()

    for state in states:
        dependencies.add(state)
        for transition in epsilon[state]:
            dependencies.add(transition)

    return list(dependencies)


def find_key_with_value(dictionary: dict[str, list[str]], new_value: list[str]) -> str | None:
    for key, value in dictionary.items():
        if tuple(sorted(value)) == tuple(sorted(new_value)):
            return key

    return None


def create_dfa(initial_state: str, finite_state: str, epsilon: dict[str, list[str]],
               machine: dict[str, MachineState]) -> dict[str, MachineState]:
    s_count = 0
    state_dependencies = {'s0': [initial_state]}
    states = ['s0']
    new_machine: dict[str, MachineState] = {}

    for state in states:
        new_machine[state] = MachineState(finite_state in get_dependencies(state_dependencies[state], epsilon), {})

        for symbol in filter(lambda x: x != 'ε', machine[initial_state].transitions):
            transitions = []
            for dependency in get_dependencies(state_dependencies[state], epsilon):
                transitions.extend(machine[dependency].transitions[symbol])
            transitions = list(set(transitions))
            key = ''
            if len(transitions) != 0:
                key = find_key_with_value(state_dependencies, transitions)
            if key is None:
                s_count += 1
                key = f's{s_count}'
                states.append(key)
                state_dependencies[key] = transitions
            new_machine[state].transitions[symbol] = {key}

    return new_machine


def adapt_dfa(initial_state: str, machine: dict[str, MachineState]) -> tuple[
    list[str], list[str], dict[str, dict[str, str]], dict[str, str], str]:
    states = list(machine.keys())
    input_symbols = list(machine[initial_state].transitions.keys())
    outputs = {}
    transitions: dict[str, dict[str, str]] = {}
    for state in states:
        outputs[state] = 'F' if machine[state].is_finite else ''
        transitions[state] = {}
        for symbol in input_symbols:
            transitions[state][symbol] = machine[state].transitions[symbol].pop()

    return states, input_symbols, transitions, outputs, initial_state


def process_nfa(initial_state: str, finite_state: str, machine: dict[str, MachineState]) -> tuple[
    list[str], list[str], dict[str, dict[str, str]], dict[str, str], str]:
    epsilon = fill_epsilon(machine)
    dfa = create_dfa(initial_state, finite_state, epsilon, machine)
    return adapt_dfa('s0', dfa)
