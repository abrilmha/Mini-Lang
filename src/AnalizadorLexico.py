# AnalizadorLexico.py (VERSIÓN CORREGIDA)
import re

# Diccionarios de tokens del lenguaje
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
    """
    Recibe el código fuente como cadena y devuelve una lista de tokens
    """
    tokens_encontrados = []
    lineas = codigo_fuente.strip().split('\n')
    linea_num = 0

    # Regex mejorada para capturar strings correctamente
    token_regex = r'\"[^\"]*\"|\'[^\']*\'|==|!=|<=|>=|[=+\-*/<>;:(){}\[\]]|\d+\.\d+|\d+|\w+'

    for linea in lineas:
        linea_num += 1
        pos = 0
        linea = linea.strip()
        
        while pos < len(linea):
            # Saltar espacios en blanco
            if linea[pos].isspace():
                pos += 1
                continue
            
            # Buscar coincidencia con el patrón
            match = None
            for pattern in [r'\"[^\"]*\"', r'\'[^\']*\'', r'==|!=|<=|>=', r'[=+\-*/<>;:(){}\[\]]', r'\d+\.\d+', r'\d+', r'\w+']:
                regex_match = re.match(pattern, linea[pos:])
                if regex_match:
                    match = regex_match.group(0)
                    break
            
            if not match:
                # Carácter no reconocido
                tokens_encontrados.append(('ERROR', linea[pos], linea_num, pos + 1))
                pos += 1
                continue
            
            token = match
            col = pos + 1
            
            # Clasificación del token
            if token in keywords:
                tipo = keywords[token]
            elif token in operators:
                tipo = operators[token]
            elif token in delimiters:
                tipo = delimiters[token]
            elif re.match(r'^\d+\.\d+$', token):
                tipo = 'NUM'
            elif re.match(r'^\d+$', token):
                tipo = 'NUM'  
            elif re.match(r'^\"[^\"]*\"$', token) or re.match(r"^\'[^\']*\'$", token):
                tipo = 'STRING'
            elif re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', token):
                tipo = 'ID'
            else:
                tipo = 'ERROR'

            tokens_encontrados.append((tipo, token, linea_num, col))
            pos += len(token)

    return tokens_encontrados
