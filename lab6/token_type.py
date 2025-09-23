from lab6.constants import *


class TokenType:
    def __init__(self, name: str, regex: str):
        self.name = name
        self.regex = regex

    def __str__(self):
        return self.name


TOKEN_TYPES = [
    TokenType('BLOCK_COMMENT', f'{{.*}}'),
    TokenType('LINE_COMMENT', f'//.*\n'),
    TokenType('ARRAY', f'(A|a)(R|r)(R|r)(A|a)(Y|y)'),
    TokenType('BEGIN', f'(B|b)(E|e)(G|g)(I|i)(N|n)'),
    TokenType('ELSE', f'(E|e)(L|l)(S|s)(E|e)'),
    TokenType('END', f'(E|e)(N|n)(D|d)'),
    TokenType('IF', f'(I|i)(F|f)'),
    TokenType('OF', f'(O|o)(F|f)'),
    TokenType('OR', f'(O|o)(R|r)'),
    TokenType('PROGRAM', f'(P|p)(R|r)(O|o)(G|g)(R|r)(A|a)(M|m)'),
    TokenType('PROCEDURE', f'(P|p)(R|r)(O|o)(C|c)(E|e)(D|d)(U|u)(R|r)(E|e)'),
    TokenType('THEN', f'(T|t)(H|h)(E|e)(N|n)'),
    TokenType('TYPE', f'(T|t)(Y|y)(P|p)(E|e)'),
    TokenType('INT', f'(I|i)(N|n)(T|t)'),
    TokenType('REAL', f'(R|r)(E|e)(A|a)(L|l)'),
    TokenType('CHAR', f'(C|c)(H|h)(A|a)(R|r)'),
    TokenType('LOOP', f'(L|l)(O|o)(O|o)(P|p)'),
    TokenType('WHILE', f'(W|w)(H|h)(I|i)(L|l)(E|e)'),
    TokenType('PRINT', f'(P|p)(R|r)(I|i)(N|n)(T|t)'),
    TokenType('READ', f'(R|r)(E|e)(A|a)(D|d)'),
    TokenType('VAR', f'(V|v)(A|a)(R|r)'),
    TokenType('AND', f'(A|a)(N|n)(D|d)'),
    TokenType('DIV', f'(D|d)(I|i)(V|v)'),
    TokenType('MOD', f'(M|m)(O|o)(D|d)'),
    TokenType('MULTIPLICATION', '\\*'),
    TokenType('PLUS', '\\+'),
    TokenType('MINUS', '-'),
    TokenType('NOT', f'(N|n)(O|o)(T|t)'),
    TokenType('TRUE', f'(T|t)(R|r)(U|u)(E|e)'),
    TokenType('FALSE', f'(F|f)(A|a)(L|l)(S|s)(E|e)'),
    TokenType('IDENTIFIER', f'({LETTER}|_)({LETTER_OR_DIGIT}|_)*'),
    TokenType('DIVIDE', '/'),
    TokenType('SEMICOLON', ';'),
    TokenType('COMMA', ','),
    TokenType('LEFT_PAREN', '\\('),
    TokenType('RIGHT_PAREN', '\\)'),
    TokenType('LEFT_BRACKET', '['),
    TokenType('RIGHT_BRACKET', ']'),
    TokenType('EQ', '=='),
    TokenType('LESS_EQ', '<='),
    TokenType('GREATER_EQ', '>='),
    TokenType('NOT_EQ', '!='),
    TokenType('GREATER', '>'),
    TokenType('LESS', '<'),
    TokenType('ASSIGN', ':='),
    TokenType('COLON', ':'),
    TokenType('DOT', '\\.'),
    TokenType('STRING', f'\'.*\''),
    TokenType('FLOAT', f'{DIGIT}*({EXPONENT}|(\\.{DIGIT}+({EXPONENT}|ε)))'),
    TokenType('INTEGER', f'{NUMBER}'),
    TokenType('SPACE', SPACE),
    TokenType('BAD_STRING', f'\'.*'),
    TokenType('BAD_BLOCK_COMMENT', f'{{.*'),
    TokenType('#', '#'),
    TokenType('BAD', '.*')
]
