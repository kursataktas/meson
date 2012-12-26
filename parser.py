#!/usr/bin/python3 -tt

# Copyright 2012 Jussi Pakkanen

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ply.lex as lex
import ply.yacc as yacc
import nodes

tokens = ['LPAREN',
          'RPAREN',
          'LBRACKET',
          'RBRACKET',
          'LBRACE',
          'RBRACE',
          'ATOM',
          'COMMENT',
          'EQUALS',
          'COMMA',
          'DOT',
          'STRING',
          'EOL_CONTINUE',
          'EOL',
          ]

t_EQUALS = '='
t_LPAREN = '\('
t_RPAREN = '\)'
t_LBRACKET = '\['
t_RBRACKET = '\]'
t_LBRACE = '\{'
t_RBRACE = '\}'
t_ATOM = '[a-zA-Z][_0-9a-zA-Z]*'
t_COMMENT = '\#[^\n]*'
t_COMMA = ','
t_DOT = '\.'

t_ignore = ' \t'

def t_STRING(t):
    "'[^']*'"
    t.value = t.value[1:-1]
    return t

def t_EOL(t):
    r'\n'
    t.lexer.lineno += 1
    return t

def t_EOL_CONTINUE(t):
    r'\\[ \t]*\n'
    t.lexer.lineno += 1

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Yacc part

def p_codeblock(t):
    'codeblock : statement EOL codeblock'
    cb = t[3]
    cb.prepend(t[1])
    t[0] = cb
    
def p_codeblock_emptyline(t):
    'codeblock : EOL codeblock'
    t[0] = t[2]

def p_codeblock_last(t):
    'codeblock : statement EOL'
    cb = nodes.CodeBlock(t.lineno(1))
    cb.prepend(t[1])
    t[0] = cb

def p_expression_atom(t):
    'expression : ATOM'
    t[0] = nodes.AtomExpression(t[1], t.lineno(1))

def p_expression_string(t):
    'expression : STRING'
    t[0] = nodes.StringExpression(t[1], t.lineno(1))

def p_statement_assign(t):
    'statement : expression EQUALS statement'
    t[0] = nodes.Assignment(t[1], t[3], t.lineno(1))

def p_statement_func_call(t):
    'statement : expression LPAREN args RPAREN'
    t[0] = nodes.FunctionCall(t[1], t[3], t.lineno(1))

def p_statement_method_call(t):
    'statement : expression DOT expression LPAREN args RPAREN'
    t[0] = nodes.MethodCall(t[1], t[3], t[5], t.lineno(1))

def p_statement_expression(t):
    'statement : expression'
    t[0] = nodes.statement_from_expression(t[1])

def p_args_multiple(t):
    'args : statement COMMA args'
    args = t[3]
    args.prepend(t[1])
    t[0] = args

def p_args_single(t):
    'args : statement'
    args = nodes.Arguments(t.lineno(1))
    args.prepend(t[1])
    t[0] = args

def p_args_none(t):
    'args :'
    t[0] = nodes.Arguments(t.lineno(0))

def p_error(t):
    print('Parser errored out at: ' + t.value)

def test_lexer():
    s = """hello = (something) # this = (that)
    two = ['file1', 'file2']
    function(h) { stuff }
    obj.method(lll, \\ 
    'string')
    """
    lexer = lex.lex()
    lexer.input(s)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)

def test_parser():
    code = """func_call('something', 'or else')
    objectname.methodname(abc)
    
    emptycall()"""
    print(build_ast(code))

def build_ast(code):
    code = code.rstrip() + '\n'
    lex.lex()
    parser = yacc.yacc()
    result = parser.parse(code)
    return result

if __name__ == '__main__':
    #test_lexer()
    test_parser()
