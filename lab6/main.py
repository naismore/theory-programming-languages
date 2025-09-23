import sys

from lab6.lexer import Lexer
from lab6.lexer_token import LexerToken


def process_tokens(lexer: Lexer, debug: bool = False, output_file=None) -> list[LexerToken]:
    tokens = []
    bad_collector = LexerToken('BAD', '', (0, 0))
    while True:
        token = lexer.next_token()
        if token is None:
            break
        if token.type == 'BAD':
            bad_collector.value += token.value
            if not bad_collector.pos[0] and not bad_collector.pos[1]:
                bad_collector.pos = token.pos
            continue
        if bad_collector.value:
            print(bad_collector) if debug else None
            if output_file:
                output_file.write(str(bad_collector) + '\n')
            tokens.append(bad_collector)
            bad_collector = LexerToken('BAD', '', (0, 0))
        if token.type not in ('SPACE', 'LINE_COMMENT', 'BLOCK_COMMENT'):
            print(token) if debug else None
            if output_file:
                output_file.write(str(token) + '\n')
            tokens.append(token)
    if bad_collector.value:
        print(bad_collector) if debug else None
        if output_file:
            output_file.write(str(bad_collector) + '\n')
        tokens.append(bad_collector)

    return tokens


def main() -> None:
    if len(sys.argv) not in {3, 4}:
        print(f'Usage: python {sys.argv[0]} <input-file> <output-file> [debug]')
        return

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    debug = sys.argv[3] == 'debug' if len(sys.argv) == 4 else False

    lexer = Lexer(input_file)

    with open(output_file, 'w', encoding='utf-8') as output:
        process_tokens(lexer, debug, output)

    lexer.close()


def task(input_file: str, debug=False) -> list[LexerToken]:
    lexer = Lexer(input_file)
    with open("output.txt", 'w', encoding='utf-8') as output:
        tokens = process_tokens(lexer, debug, output)
    lexer.close()
    return tokens


if __name__ == '__main__':
    main()
