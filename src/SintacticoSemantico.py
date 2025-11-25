# =========================================================
# Analizador Sintáctico y Semántico Extendido (versión final)
# Lenguaje propio basado en el Analizador Léxico 
# =========================================================

from AnalizadorLexico import obtener_tokens
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict

# -----------------------
# Token
# -----------------------
class Token:
    def __init__(self, type_, value, line=0, col=0):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col
    def __repr__(self):
        return f"Token({self.type},{self.value})"

# -----------------------
# AST Nodes
# -----------------------
@dataclass
class ASTNode: pass

@dataclass
class Program(ASTNode):
    statements: List['ASTNode'] = field(default_factory=list)

@dataclass
class VarDecl(ASTNode):
    var_type: str
    name: str
    expr: Optional['ASTNode'] = None
    line: int = 0

@dataclass
class Assign(ASTNode):
    name: str
    expr: 'ASTNode'
    line: int = 0

@dataclass
class BinaryOp(ASTNode):
    op: str
    left: 'ASTNode'
    right: 'ASTNode'

@dataclass
class Literal(ASTNode):
    value: Any
    value_type: str

@dataclass
class VarRef(ASTNode):
    name: str
    line: int = 0

@dataclass
class IfStmt(ASTNode):
    cond: 'ASTNode'
    then_block: List['ASTNode']
    else_block: Optional[List['ASTNode']]
    line: int = 0

@dataclass
class WhileStmt(ASTNode):
    cond: 'ASTNode'
    body: List['ASTNode']
    line: int = 0

@dataclass
class PrintStmt(ASTNode):
    expr: 'ASTNode'
    line: int = 0

@dataclass
class InputStmt(ASTNode):
    name: str
    line: int = 0


# -----------------------
# Parser
# -----------------------
class ParserError(Exception): pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        t = self.peek()
        if t:
            self.pos += 1
        return t

    def expect(self, typ):
        t = self.peek()
        if not t:
            raise ParserError(f"Se esperaba '{typ}' pero se llegó al final del código.")
        if t.type != typ:
            raise ParserError(
                f"Error de sintaxis en línea {t.line}: "
                f"se esperaba '{typ.replace('_KW', '').lower()}' pero se encontró '{t.value}'."
            )
        return self.advance()

    def parse(self):
        prog = Program()
        if self.peek() and self.peek().type == 'PROGRAM':
            self.advance()
        while self.peek() and self.peek().type != 'END':
            prog.statements.append(self.parse_stmt())
        if self.peek() and self.peek().type == 'END':
            self.advance()
        return prog

    # ----- Statements -----
    def parse_stmt(self):
        t = self.peek()
        if not t:
            raise ParserError("EOF inesperado")

        if t.type in ('VAR', 'INT_KW', 'FLOAT_KW', 'BOOL_KW', 'STRING_KW'):
            return self.parse_vardecl()
        if t.type == 'ID':
            return self.parse_assign()
        if t.type == 'IF':
            return self.parse_if()
        if t.type == 'WHILE':
            return self.parse_while()
        if t.type == 'PRINT':
            return self.parse_print()
        if t.type == 'INPUT':
            return self.parse_input()

        raise ParserError(f"Error en línea {t.line}: token inesperado '{t.value}'")

    def parse_vardecl(self):
        t = self.peek()
        tipo = None
        if t.type in ('INT_KW', 'FLOAT_KW', 'BOOL_KW', 'STRING_KW'):
            tipo = self.advance().value
        elif t.type == 'VAR':
            self.advance()
            tipo = 'var'
        linea = t.line
        name = self.expect('ID').value
        expr = None
        if self.peek() and self.peek().type == 'ASSIGN':
            self.advance()
            expr = self.parse_expr()
        self.expect('SEMI')
        return VarDecl(tipo, name, expr, line=linea)

    def parse_assign(self):
        name_token = self.expect('ID')
        name = name_token.value
        linea = name_token.line
        self.expect('ASSIGN')
        expr = self.parse_expr()
        self.expect('SEMI')
        return Assign(name, expr, line=linea)

    def parse_if(self):
        if_token = self.expect('IF')
        self.expect('LPAREN')
        cond = self.parse_expr()
        self.expect('RPAREN')
        self.expect('LBRACE')
        then_block = []
        while self.peek() and self.peek().type != 'RBRACE':
            then_block.append(self.parse_stmt())
        self.expect('RBRACE')
        else_block = None
        if self.peek() and self.peek().type == 'ELSE':
            self.advance()
            self.expect('LBRACE')
            else_block = []
            while self.peek() and self.peek().type != 'RBRACE':
                else_block.append(self.parse_stmt())
            self.expect('RBRACE')
        return IfStmt(cond, then_block, else_block, line=if_token.line)

    def parse_while(self):
        while_token = self.expect('WHILE')
        self.expect('LPAREN')
        cond = self.parse_expr()
        self.expect('RPAREN')
        self.expect('LBRACE')
        body = []
        while self.peek() and self.peek().type != 'RBRACE':
            body.append(self.parse_stmt())
        self.expect('RBRACE')
        return WhileStmt(cond, body, line=while_token.line)

    def parse_print(self):
        print_token = self.expect('PRINT')
        self.expect('LPAREN')
        expr = self.parse_expr()
        self.expect('RPAREN')
        self.expect('SEMI')
        return PrintStmt(expr, line=print_token.line)

    def parse_input(self):
        input_token = self.expect('INPUT')
        self.expect('LPAREN')
        name = self.expect('ID').value
        self.expect('RPAREN')
        self.expect('SEMI')
        return InputStmt(name, line=input_token.line)

    # ----- Expresiones -----
    def parse_expr(self):
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_addition()
        while self.peek() and self.peek().type in ('LT','GT','LE','GE','EQ','NEQ'):
            op = self.advance().type
            right = self.parse_addition()
            left = BinaryOp(op, left, right)
        return left

    def parse_addition(self):
        left = self.parse_multiplication()
        while self.peek() and self.peek().type in ('PLUS','MINUS'):
            op = self.advance().type
            right = self.parse_multiplication()
            left = BinaryOp(op, left, right)
        return left

    def parse_multiplication(self):
        left = self.parse_term()
        while self.peek() and self.peek().type in ('MUL','DIV'):
            op = self.advance().type
            right = self.parse_term()
            left = BinaryOp(op, left, right)
        return left

    def parse_term(self):
        t = self.peek()
        if not t:
            raise ParserError("EOF en expresión")
        
        if t.type == 'NUM':
            self.advance()
            return Literal(float(t.value) if '.' in t.value else int(t.value),
                        'float' if '.' in t.value else 'int')
        
        if t.type == 'TRUE':
            self.advance()
            return Literal(True, 'bool')
        
        if t.type == 'FALSE':
            self.advance()
            return Literal(False, 'bool')
        
        if t.type == 'STRING':
            self.advance()
            return Literal(t.value, 'string')
        
        if t.type == 'ID':
            tok = self.advance()
            return VarRef(tok.value, line=tok.line)
        
        if t.type == 'LPAREN':
            self.advance()
            expr = self.parse_expr()
            self.expect('RPAREN')
            return expr
        
        raise ParserError(f"Error en línea {t.line}: token inesperado '{t.value}' en expresión")

# -----------------------
# Semantic Analyzer
# -----------------------

class SemanticAnalyzer:
    def __init__(self):
        self.global_symbols: Dict[str, str] = {}
        self.scopes: List[Dict[str, str]] = []  # pila de ámbitos
        self.errors: List[str] = []

    # --- Utilidades de manejo de ámbito ---
    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    def current_scope(self):
        return self.scopes[-1] if self.scopes else self.global_symbols

    def declare(self, name, tipo, node):
        current = self.current_scope()
        if name in current:
            self.errors.append(f"Error en línea {node.line}: redeclaración de '{name}' en este ámbito")
        current[name] = tipo
        node._tipo = tipo
        node._ambito = "local" if self.scopes else "global"

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return self.global_symbols.get(name)

    # --- Análisis principal ---
    def analyze(self, program: Program):
        for stmt in program.statements:
            self.visit(stmt)
        return self.errors

    def visit(self, node):
        method = f'visit_{type(node).__name__}'
        if hasattr(self, method):
            return getattr(self, method)(node)

    # --- Visitas ---
    def visit_VarDecl(self, node):
        tipo = node.var_type if node.var_type != 'var' else 'int'
        self.declare(node.name, tipo, node)
        if node.expr:
            tipo_expr = self.eval_expr(node.expr)
            if tipo_expr and tipo_expr != tipo:
                self.errors.append(
                    f"Error de tipos en línea {node.line}: '{node.name}' es {tipo} pero se asignó un valor {tipo_expr}"
                )

    def visit_Assign(self, node):
        tipo_var = self.lookup(node.name)
        node._ambito = "local" if self.scopes else "global"
        node._tipo = tipo_var or "desconocido"
        if not tipo_var:
            self.errors.append(f"Error en línea {node.line}: variable no declarada '{node.name}'")
            return
        tipo_expr = self.eval_expr(node.expr)
        if tipo_expr and tipo_expr != tipo_var:
            self.errors.append(
                f"Error de tipos en línea {node.line}: asignando {tipo_expr} a {tipo_var} en '{node.name}'"
            )

    def visit_IfStmt(self, node):
        node._ambito = "global"
        node._tipo = "bool"
        tipo_cond = self.eval_expr(node.cond)
        if tipo_cond != 'bool':
            self.errors.append(f"Error en línea {node.line}: la condición del 'if' debe ser booleana")

        # --- Bloque verdadero ---
        self.enter_scope()
        for stmt in node.then_block:
            self.visit(stmt)
        self.exit_scope()

        # --- Bloque falso (si existe) ---
        if node.else_block:
            self.enter_scope()
            for stmt in node.else_block:
                self.visit(stmt)
            self.exit_scope()

    def visit_WhileStmt(self, node):
        node._ambito = "global"
        node._tipo = "bool"
        tipo_cond = self.eval_expr(node.cond)
        if tipo_cond != 'bool':
            self.errors.append(f"Error en línea {node.line}: la condición del 'while' debe ser booleana")

        self.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.exit_scope()

    def visit_PrintStmt(self, node):
        node._ambito = "global"
        node._tipo = "void"
        self.eval_expr(node.expr)

    def visit_InputStmt(self, node):
        node._ambito = "global"
        node._tipo = "string"
        if not self.lookup(node.name):
            self.errors.append(f"Advertencia en línea {node.line}: '{node.name}' no está declarada antes de input()")

    # --- Evaluación de expresiones ---
    def eval_expr(self, node):
        if isinstance(node, Literal):
            node._tipo = node.value_type
            node._ambito = "local" if self.scopes else "global"
            return node.value_type

        if isinstance(node, VarRef):
            tipo = self.lookup(node.name)
            node._ambito = "local" if self.scopes else "global"
            node._tipo = tipo or "desconocido"
            if not tipo:
                self.errors.append(f"Error en línea {node.line}: variable no declarada '{node.name}'")
            return tipo

        if isinstance(node, BinaryOp):
            left = self.eval_expr(node.left)
            right = self.eval_expr(node.right)
            node._ambito = "local" if self.scopes else "global"
            
            # Operaciones aritméticas
            if node.op in ('PLUS', 'MINUS', 'MUL', 'DIV'):
                if left == right == 'int':
                    node._tipo = 'int'
                    return 'int'
                if left == right == 'float':
                    node._tipo = 'float'
                    return 'float'
                self.errors.append(f"Error: operación inválida {left} {node.op} {right}")
            
            # Operaciones de comparación (numéricas)
            elif node.op in ('LT', 'GT', 'LE', 'GE'):
                if left in ('int', 'float') and right in ('int', 'float'):
                    node._tipo = 'bool'
                    return 'bool'
                self.errors.append(f"Error: operación inválida {left} {node.op} {right}")
            
            # Operaciones de igualdad (para cualquier tipo compatible)
            elif node.op in ('EQ', 'NEQ'):
                if left == right:  # Mismo tipo
                    node._tipo = 'bool'
                    return 'bool'
                elif (left in ('int', 'float') and right in ('int', 'float')):
                    # Permitir comparación entre int y float
                    node._tipo = 'bool'
                    return 'bool'
                else:
                    self.errors.append(f"Error: operación inválida {left} {node.op} {right}")
            
            return None
        
        return None


# -----------------------
# Pretty Print del AST (legible)
# -----------------------
def ast_to_str(node, indent=0):
    pad = "  " * indent
    op_map = {
        "LT": "<", "GT": ">", "LE": "<=", "GE": ">=",
        "EQ": "==", "NEQ": "!=", "PLUS": "+", "MINUS": "-"
    }

    if isinstance(node, Program):
        s = pad + "Programa\n"
        for st in node.statements:
            s += ast_to_str(st, indent + 1)
        return s

    if isinstance(node, VarDecl):
        s = pad + "Declaración\n"
        s += pad + f"  Tipo: {node.var_type}\n"
        s += pad + f"  Variable: {node.name}\n"
        if node.expr:
            s += pad + f"  Valor asignado:\n"
            s += ast_to_str(node.expr, indent + 2)
        return s

    if isinstance(node, Assign):
        s = pad + f"Asignación\n"
        s += pad + f"  Variable: {node.name}\n"
        s += pad + f"  Valor:\n" + ast_to_str(node.expr, indent + 2)
        return s

    if isinstance(node, Literal):
        return pad + f"Valor: {node.value} ({node.value_type})\n"

    if isinstance(node, VarRef):
        return pad + f"Variable: {node.name}\n"

    if isinstance(node, BinaryOp):
        op = op_map.get(node.op, node.op)
        s = pad + f"Operación: {op}\n"
        s += pad + "  Izquierdo:\n" + ast_to_str(node.left, indent + 2)
        s += pad + "  Derecho:\n" + ast_to_str(node.right, indent + 2)
        return s

    if isinstance(node, IfStmt):
        s = pad + "Condicional (si)\n"
        s += pad + "  Condición:\n" + ast_to_str(node.cond, indent + 2)
        s += pad + "  Bloque verdadero:\n"
        for st in node.then_block:
            s += ast_to_str(st, indent + 2)
        if node.else_block:
            s += pad + "  Bloque falso:\n"
            for st in node.else_block:
                s += ast_to_str(st, indent + 2)
        return s

    if isinstance(node, WhileStmt):
        s = pad + "Bucle (mientras)\n"
        s += pad + "  Condición:\n" + ast_to_str(node.cond, indent + 2)
        s += pad + "  Cuerpo:\n"
        for st in node.body:
            s += ast_to_str(st, indent + 2)
        return s

    if isinstance(node, PrintStmt):
        s = pad + "Imprimir\n"
        s += ast_to_str(node.expr, indent + 1)
        return s

    if isinstance(node, InputStmt):
        return pad + f"Entrada de datos en variable: {node.name}\n"

    return pad + f"Desconocido ({type(node).__name__})\n"


# ---------------------------------------------------------
# Árbol Semántico Anotado
# ---------------------------------------------------------
def ast_to_semantic_str(node, indent=0):
    pad = "  " * indent
    if not isinstance(node, ASTNode):
        return ""

    tipo = getattr(node, "_tipo", None)
    ambito = getattr(node, "_ambito", "global")
    info_extra = ""
    if tipo:
        info_extra += f" [tipo={tipo}]"
    if ambito:
        info_extra += f" [ámbito={ambito}]"

    s = pad + f"{type(node).__name__}{info_extra}\n"

    for attr, value in vars(node).items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ASTNode):
                    s += ast_to_semantic_str(item, indent + 1)
        elif isinstance(value, ASTNode):
            s += ast_to_semantic_str(value, indent + 1)

    return s


# ---------------------------------------------------------
# Generador de árbol en formato Graphviz (DOT)
# ---------------------------------------------------------
def ast_to_dot(node):
    lines = [
        "digraph AST {",
        '    rankdir=LR;',
        '    node [shape=box, style=filled, fillcolor="#ffe6f2", fontname="Consolas"];'
    ]
    counter = {"n": 0}

    def escape_label(text):
        if isinstance(text, str):
            return text.replace('"', '\\"')
        return str(text)

    def add_node(node):
        nid = f"n{counter['n']}"
        counter["n"] += 1
        label_map = {
            "Program": "Programa",
            "VarDecl": "Declaración",
            "Assign": "Asignación",
            "BinaryOp": "Operación",
            "Literal": "Valor",
            "VarRef": "Variable",
            "IfStmt": "Condicional (si)",
            "WhileStmt": "Bucle (mientras)",
            "PrintStmt": "Imprimir",
            "InputStmt": "Entrada (input)"
        }
        label = label_map.get(type(node).__name__, type(node).__name__)
        if hasattr(node, "name") and node.name:
            label += f"\\n{escape_label(node.name)}"
        if hasattr(node, "value") and node.value not in (None, ""):
            label += f"\\n{escape_label(node.value)}"
        if hasattr(node, "op"):
            op_map = {
                'LT': '<', 'GT': '>', 'LE': '<=', 'GE': '>=',
                'EQ': '==', 'NEQ': '!=', 'PLUS': '+', 'MINUS': '-'
            }
            op = op_map.get(getattr(node, 'op', ''), '')
            if op:
                label += f"\\nOperador: {escape_label(op)}"
        lines.append(f'    {nid} [label="{label}"];')
        return nid

    def walk(node, parent=None):
        if node is None:
            return
        nid = add_node(node)
        if parent:
            lines.append(f"    {parent} -> {nid};")
        for attr, value in vars(node).items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ASTNode):
                        walk(item, nid)
            elif isinstance(value, ASTNode):
                walk(value, nid)
        return nid

    walk(node)
    lines.append("}")
    return "\n".join(lines)
