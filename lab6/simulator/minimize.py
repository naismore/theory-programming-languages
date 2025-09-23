Machine = tuple[list[str], list[str], dict[str, dict[str, str]], dict[str, str], str]


def remove_unreachable_states(machine: Machine) -> Machine:
    states, input_symbols, transitions, outputs, initial_state = machine
    reachable_states = set()
    to_visit = [initial_state]

    while to_visit:
        state = to_visit.pop()
        if state in reachable_states:
            continue
        reachable_states.add(state)

        for symbol in transitions[state]:
            transition = transitions[state][symbol]
            if transition:
                to_visit.append(transition)

    return list(filter(lambda x: x in reachable_states, states)), input_symbols, transitions, outputs, initial_state


def refine(partitions: list[set[str]], input_symbols: list[str], transitions: dict[str, dict[str, str]]) \
        -> list[set[str]]:
    new_partitions: list[set[str]] = []
    for group in partitions:
        subgroup = {}
        for state in group:
            key = ''
            for symbol in input_symbols:
                for i, s in enumerate(partitions):
                    if transitions[state][symbol] in s:
                        key += symbol + str(i)
            subgroup.setdefault(key, set()).add(state)
        new_partitions.extend(subgroup.values())
    return new_partitions


def minimize_moore_machine(machine: Machine) -> Machine:
    states, input_symbols, transitions, outputs, initial_state = machine

    output_groups: dict[str, set[str]] = {}
    for state in states:
        output = outputs[state]
        output_groups.setdefault(output, set()).add(state)

    partitions = list(output_groups.values())

    while True:
        new_partitions = refine(partitions, input_symbols, transitions)
        if new_partitions == partitions:
            break
        partitions = new_partitions

    state_map = {}
    minimized_states = []
    minimized_transitions = {}
    minimized_outputs = {}

    for i, group in enumerate(partitions):
        new_state = f'S{i}'
        for state in group:
            state_map[state] = new_state
        minimized_states.append(new_state)
        representative = next(iter(group))
        minimized_outputs[new_state] = outputs[representative]

    for group in partitions:
        representative = next(iter(group))
        new_state = state_map[representative]
        minimized_transitions[new_state] = {
            symbol: state_map[transitions[representative][symbol]] if transitions[representative][symbol] else ''
            for symbol in input_symbols
        }
    minimized_initial_state = state_map[initial_state]

    return minimized_states, input_symbols, minimized_transitions, minimized_outputs, minimized_initial_state


def process_dfa(machine: Machine) -> Machine:
    return minimize_moore_machine(remove_unreachable_states(machine))
