import re

# Language tokens
keywords = {
    'program': 'PROGRAM',
    'var': 'VAR', 
    'int': 'INT_KW',
    'float': 'FLOAT_KW',
    'bool': 'BOOL_KW',
    'string': 'STRING_KW',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE', 
    'print': 'PRINT',
    'input': 'INPUT',
    'end': 'END',
    'true': 'TRUE',
    'false': 'FALSE'
}

operators = {
    '=': 'ASSIGN',
    '+': 'PLUS',
    '-': 'MINUS', 
    '*': 'MUL',
    '/': 'DIV',
    '<': 'LT',
    '>': 'GT',
    '<=': 'LE',
    '>=': 'GE',
    '==': 'EQ',
    '!=': 'NEQ'
}

delimiters = {
    '(': 'LPAREN',
    ')': 'RPAREN',
    '{': 'LBRACE', 
    '}': 'RBRACE',
    ';': 'SEMI',
    ':': 'COLON'
}

def obtener_tokens(codigo_fuente):
    
    tokens_encontrados = []
    lineas = codigo_fuente.split('\n')
    linea_num = 0

    for linea in lineas:
        linea_num += 1
        pos = 0
        linea = linea.rstrip()
        
        while pos < len(linea):
            # Saltar espacios en blanco
            if linea[pos].isspace():
                pos += 1
                continue
            
            
            patterns = [
                (r'\"[^\"]*\"', 'STRING'),      
                (r"\'[^\']*\'", 'STRING'),      
                (r'==|!=|<=|>=', 'OPERATOR'),   
                (r'[=+\-*/<>(){};:]', 'SYMBOL'), 
                (r'\d+\.\d+', 'NUM'),           
                (r'\d+', 'NUM'),                
                (r'[A-Za-z_][A-Za-z0-9_]*', 'ID') 
            ]
            
            match = None
            token_type = None
            
            for pattern, t_type in patterns:
                regex_match = re.match(pattern, linea[pos:])
                if regex_match:
                    match = regex_match.group(0)
                    token_type = t_type
                    break
            
            if not match:
                
                tokens_encontrados.append(('ERROR', linea[pos], linea_num, pos + 1))
                pos += 1
                continue
            
            token = match
            col = pos + 1
            
            # Token clasification
            if token in keywords:
                tipo = keywords[token]
            elif token in operators:
                tipo = operators[token]
            elif token in delimiters:
                tipo = delimiters[token]
            elif token_type == 'NUM':
                if '.' in token:
                    tipo = 'NUM'
                else:
                    tipo = 'NUM'
            elif token_type == 'STRING':
                tipo = 'STRING'
            elif token_type == 'ID':
                tipo = 'ID'
            else:
                tipo = 'ERROR'

            tokens_encontrados.append((tipo, token, linea_num, col))
            pos += len(token)

    return tokens_encontrados
