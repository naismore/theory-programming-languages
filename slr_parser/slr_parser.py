#!/usr/bin/env python3

from slr_parser.grammar import Grammar
import argparse
import csv

def first_follow(G):
    def union(set_1, set_2):
        original_size = len(set_1)
        set_1.update(set_2)
        return original_size != len(set_1)

    first = {symbol: set() for symbol in G.symbols}
    first.update((terminal, {terminal}) for terminal in G.terminals)
    follow = {symbol: set() for symbol in G.nonterminals}
    follow[G.start].add('$')

    while True:
        updated = False

        for head, bodies in G.grammar.items():
            for body in bodies:
                for symbol in body:
                    if symbol != '^':
                        updated |= union(first[head], first[symbol] - {'^'})
                        if '^' not in first[symbol]:
                            break
                    else:
                        updated |= union(first[head], {'^'})
                else:
                    updated |= union(first[head], {'^'})

                aux = follow[head]
                for symbol in reversed(body):
                    if symbol == '^':
                        continue
                    if symbol in follow:
                        updated |= union(follow[symbol], aux - {'^'})
                    if '^' in first[symbol]:
                        aux = aux | first[symbol]
                    else:
                        aux = first[symbol]

        if not updated:
            return first, follow


class SLRParser:
    def __init__(self, G):
        self.G_prime = Grammar(f"{G.start}' -> {G.start}\n{G.grammar_str}")
        self.G_indexed = [
            {'head': head, 'body': body}
            for head, bodies in self.G_prime.grammar.items()
            for body in bodies
        ]
        self.first, self.follow = first_follow(self.G_prime)
        self.C = self.items(self.G_prime)
        self.parsing_table = self.construct_parsing_table()
        self.action_symbols = list(self.G_prime.terminals) + ['$']
        self.max_nonterminal_len = max(len(nonterminal) for nonterminal in self.G_prime.nonterminals)

    def CLOSURE(self, I):
        J = I.copy()

        while True:
            original_size = len(J)

            for i, dot_pos in J:
                body = self.G_indexed[i]['body']
                if dot_pos < len(body):
                    symbol_after_dot = body[dot_pos]
                    if symbol_after_dot in self.G_prime.nonterminals:
                        for body in self.G_prime.grammar[symbol_after_dot]:
                            new_item = (self.G_indexed.index({'head': symbol_after_dot, 'body': body}), 0)
                            if new_item not in J:
                                J.append(new_item)

            if len(J) == original_size:
                return J

    def GOTO(self, I, X):
        goto = []

        for i, dot_pos in I:
            body = self.G_indexed[i]['body']
            if dot_pos < len(body) and body[dot_pos] == X:
                for new_item in self.CLOSURE([(i, dot_pos + 1)]):
                    if new_item not in goto:
                        goto.append(new_item)

        return goto

    def items(self, G_prime):
        C = [self.CLOSURE([(0, 0)])]

        while True:
            original_size = len(C)

            for I in C:
                for X in G_prime.symbols:
                    goto = self.GOTO(I, X)
                    if goto and goto not in C:
                        C.append(goto)

            if len(C) == original_size:
                return C

   def print_info(self):   
       goto_symbols = self.G_prime.nonterminals - {self.G_prime.start}
       parsing_table_symbols = self.action_symbols + list(goto_symbols)
   
       # Сохранение таблицы в CSV
       with open('slr_table.csv', 'w', newline='', encoding='utf-8') as csvfile:
           writer = csv.writer(csvfile)
           
           # Заголовок таблицы
           header = ['STATE'] + list(parsing_table_symbols)
           writer.writerow(header)
           
           # Данные таблицы
           for s in self.parsing_table:
               row = [s]
               for symbol in parsing_table_symbols:
                   row.append(self.parsing_table[s].get(symbol, ''))
               writer.writerow(row)
       
       print('\nПарсинг таблица сохранена в файл slr_table.csv')

    def LR_parser(self, w):
        buffer = f'{w} $'.split()
        pointer = 0
        a = buffer[pointer]
        stack = ['0']
        symbols = ['']
        results = {
            'step': [''],
            'stack': ['STACK'] + stack,
            'symbols': ['SYMBOLS'] + symbols,
            'input': ['INPUT'],
            'action': ['ACTION']
        }

        step = 0
        while True:
            s = int(stack[-1])
            step += 1
            results['step'].append(f'({step})')
            results['input'].append(' '.join(buffer[pointer:]))

            if a not in self.action_symbols:
                results['action'].append(f'ERROR: unrecognized symbol {a}')
                break

            action = self.parsing_table[s].get(a, '')

            if not action:
                results['action'].append('ERROR: input cannot be parsed by given grammar')
                break

            elif '/' in action:
                conflict_type = 'reduce' if action.count('r') > 1 else 'shift'
                results['action'].append(f'ERROR: {conflict_type}-reduce conflict at state {s}, symbol {a}')
                break

            elif action.startswith('s'):
                stack.append(action[1:])
                symbols.append(a)
                results['stack'].append(' '.join(stack))
                results['symbols'].append(' '.join(symbols[1:]))
                results['action'].append('shift')
                pointer += 1
                a = buffer[pointer]

            elif action.startswith('r'):
                production = self.G_indexed[int(action[1:])]
                head = production['head']
                body = production['body']

                if body != ['^']:
                    stack = stack[:-len(body)]
                    symbols = symbols[:-len(body)]

                stack.append(str(self.parsing_table[int(stack[-1])][head]))
                symbols.append(head)
                results['stack'].append(' '.join(stack))
                results['symbols'].append(' '.join(symbols[1:]))
                results['action'].append(f'reduce by {head} -> {" ".join(body)}')

            elif action == 'acc':
                results['action'].append('accept')
                break

        return results

    def print_LR_parser(self, results):
        def print_line():
            line = '+' + '+'.join([('-' * (max_len + 2)) for max_len in max_lens.values()]) + '+'
            print(line)

        max_lens = {key: max(len(value) for value in results[key]) for key in results}
        justifications = {
            'step': '>',
            'stack': '',
            'symbols': '',
            'input': '>',
            'action': ''
        }

        print_line()
        header = ''.join(
            [f'| {history[0]:^{max_len}} ' for history, max_len in zip(results.values(), max_lens.values())]) + '|'
        print(header)
        print_line()
        for i in range(1, len(results['step'])):
            row = ''.join([f'| {history[i]:{justification}{max_len}} ' for history, justification, max_len in
                           zip(results.values(), justifications.values(), max_lens.values())]) + '|'
            print(row)

        print_line()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('grammar_file', type=argparse.FileType('r'), help='Path to the text file used as grammar')
    parser.add_argument('tokens', help='Tokens to be parsed, separated by spaces')
    args = parser.parse_args()

    G = Grammar(args.grammar_file.read())
    slr_parser = SLRParser(G)
    slr_parser.print_info()
    results = slr_parser.LR_parser(args.tokens)
    slr_parser.print_LR_parser(results)


if __name__ == '__main__':
    main()
