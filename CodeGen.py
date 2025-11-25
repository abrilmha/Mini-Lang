# CodeGen.py (VERSIÓN MEJORADA - PRINTS SIN COMILLAS)
from SintacticoSemantico import *

class CodeGenerator:
    def __init__(self):
        self.tac_code = []
        self.temp_counter = 0
        self.label_counter = 0
        self.symbol_table = {}
    
    def new_temp(self):
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp
    
    def new_label(self):
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def generate(self, node):
        self.tac_code = []
        self.visit(node)
        return self.tac_code
    
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        return None
    
    def visit_Program(self, node):
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_VarDecl(self, node):
        if node.expr:
            temp = self.visit(node.expr)
            self.tac_code.append(f"{node.name} := {temp}")
            self.symbol_table[node.name] = node.var_type
    
    def visit_Assign(self, node):
        temp = self.visit(node.expr)
        self.tac_code.append(f"{node.name} := {temp}")
    
    def visit_BinaryOp(self, node):
        left_temp = self.visit(node.left)
        right_temp = self.visit(node.right)
        
        op_map = {
            'PLUS': '+', 'MINUS': '-', 'MUL': '*', 'DIV': '/',
            'LT': '<', 'GT': '>', 'LE': '<=', 'GE': '>=',
            'EQ': '==', 'NEQ': '!='
        }
        
        op = op_map.get(node.op, node.op)
        temp = self.new_temp()
        self.tac_code.append(f"{temp} := {left_temp} {op} {right_temp}")
        return temp
    
    def visit_Literal(self, node):
        if node.value_type == 'string':
            # Mantener comillas para asignaciones
            return f'"{node.value}"'
        return str(node.value)
    
    def visit_VarRef(self, node):
        return node.name
    
    def visit_IfStmt(self, node):
        cond_temp = self.visit(node.cond)
        else_label = self.new_label()
        end_label = self.new_label()
        
        self.tac_code.append(f"if {cond_temp} == 0 goto {else_label}")
        
        for stmt in node.then_block:
            self.visit(stmt)
        
        self.tac_code.append(f"goto {end_label}")
        self.tac_code.append(f"{else_label}:")
        
        if node.else_block:
            for stmt in node.else_block:
                self.visit(stmt)
        
        self.tac_code.append(f"{end_label}:")
    
    def visit_WhileStmt(self, node):
        start_label = self.new_label()
        end_label = self.new_label()
        
        self.tac_code.append(f"{start_label}:")
        cond_temp = self.visit(node.cond)
        self.tac_code.append(f"if {cond_temp} == 0 goto {end_label}")
        
        for stmt in node.body:
            self.visit(stmt)
        
        self.tac_code.append(f"goto {start_label}")
        self.tac_code.append(f"{end_label}:")
    
    def visit_PrintStmt(self, node):
        # Para prints, manejamos diferente según el tipo
        if isinstance(node.expr, Literal) and node.expr.value_type == 'string':
            # Para strings literales, poner el valor sin comillas en el print
            self.tac_code.append(f'print {node.expr.value}')
        else:
            # Para variables o expresiones, generar normalmente
            expr_temp = self.visit(node.expr)
            self.tac_code.append(f"print {expr_temp}")
    
    def visit_InputStmt(self, node):
        self.tac_code.append(f"input {node.name}")