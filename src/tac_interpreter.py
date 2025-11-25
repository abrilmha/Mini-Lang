# tac_interpreter.py (VERSIÓN FINAL)
class TACInterpreter:
    def __init__(self):
        self.memory = {}
        self.output = []
        self.labels = {}
        self.had_errors = False
    
    def execute(self, tac_code):
        if not tac_code:
            return ["Error: No hay código para ejecutar"]
            
        lines = [line.strip() for line in tac_code if line.strip()]
        
        # Encontrar etiquetas
        for i, line in enumerate(lines):
            if line.endswith(':'):
                label_name = line[:-1]
                self.labels[label_name] = i
        
        # Ejecutar
        pc = 0
        max_iterations = 1000
        iteration_count = 0
        
        while pc < len(lines) and iteration_count < max_iterations:
            iteration_count += 1
            line = lines[pc]
            
            if not line or line.endswith(':'):
                pc += 1
                continue

            if line.startswith("print"):
                value = line[5:].strip()
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    self.output.append(value[1:-1])
                else:
                    self.output.append(str(self.memory.get(value, 0)))
                pc += 1
            
            elif line.startswith("if"):
                parts = line.split()
                if len(parts) >= 5 and parts[2] == "==":  # Formato: if t0 == 0 goto L1
                    var_name = parts[1]
                    compare_value = int(parts[3])
                    label = parts[5]
                    
                    var_value = self.memory.get(var_name, 0)
                    
                    if var_value == compare_value:
                        if label in self.labels:
                            pc = self.labels[label]
                        else:
                            pc += 1
                    else:
                        pc += 1
                else:
                    pc += 1
            
            elif line.startswith("goto"):
                parts = line.split()
                if len(parts) >= 2:
                    label = parts[1]
                    if label in self.labels:
                        pc = self.labels[label]
                    else:
                        pc += 1
                else:
                    pc += 1
            
            elif ":=" in line:
                left, right = line.split(":=")
                left = left.strip()
                right = right.strip()
                
                if " < " in right:
                    a, b = right.split(" < ")
                    val_a = self.get_value(a)
                    val_b = self.get_value(b)
                    self.memory[left] = 1 if val_a < val_b else 0
                
                elif " > " in right:
                    a, b = right.split(" > ")
                    val_a = self.get_value(a)
                    val_b = self.get_value(b)
                    self.memory[left] = 1 if val_a > val_b else 0
                
                elif " <= " in right:
                    a, b = right.split(" <= ")
                    val_a = self.get_value(a)
                    val_b = self.get_value(b)
                    self.memory[left] = 1 if val_a <= val_b else 0
                
                elif " >= " in right:
                    a, b = right.split(" >= ")
                    val_a = self.get_value(a)
                    val_b = self.get_value(b)
                    self.memory[left] = 1 if val_a >= val_b else 0
                
                elif " == " in right:
                    a, b = right.split(" == ")
                    val_a = self.get_value(a)
                    val_b = self.get_value(b)
                    self.memory[left] = 1 if val_a == val_b else 0
                
                elif " != " in right:
                    a, b = right.split(" != ")
                    val_a = self.get_value(a)
                    val_b = self.get_value(b)
                    self.memory[left] = 1 if val_a != val_b else 0
                
                elif " + " in right:
                    a, b = right.split(" + ")
                    val_a = self.get_value(a)
                    val_b = self.get_value(b)
                    if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                        self.memory[left] = val_a + val_b
                    else:
                        self.memory[left] = str(val_a) + str(val_b)
                
                elif " - " in right:
                    a, b = right.split(" - ")
                    val_a = self.get_value(a)
                    val_b = self.get_value(b)
                    self.memory[left] = val_a - val_b
                
                elif " * " in right:
                    a, b = right.split(" * ")
                    val_a = self.get_value(a)
                    val_b = self.get_value(b)
                    self.memory[left] = val_a * val_b
                
                elif " / " in right:
                    a, b = right.split(" / ")
                    val_a = self.get_value(a)
                    val_b = self.get_value(b)
                    if val_b != 0:
                        self.memory[left] = val_a / val_b
                    else:
                        self.memory[left] = 0
                
                else:
                    self.memory[left] = self.get_value(right)
                
                pc += 1
            
            else:
                pc += 1
        
        if iteration_count >= max_iterations:
            self.output.append("Error: Bucle infinito detectado")
            self.had_errors = True
        
        return self.output
    
    def get_value(self, operand):
        if not operand:
            return 0
        
        if (operand.startswith('"') and operand.endswith('"')) or (operand.startswith("'") and operand.endswith("'")):
            return operand[1:-1]
        
        try:
            if '.' in operand:
                return float(operand)
            else:
                return int(operand)
        except:
            pass
        
        if operand in self.memory:
            return self.memory[operand]
        
        return 0
    
    def had_execution_errors(self):
        return self.had_errors
