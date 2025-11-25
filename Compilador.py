# CompiladorFinal.py (VERSIÓN CON VALIDACIÓN SEMÁNTICA COMPLETA)
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
from AnalizadorLexico import obtener_tokens
from SintacticoSemantico import Parser, Token, SemanticAnalyzer, ast_to_str
from CodeGen import CodeGenerator
from tac_interpreter import TACInterpreter

class CompilerInterface:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title(" Compilador Mini Lenguaje ")
        self.ventana.geometry("1000x820")
        self.ventana.configure(bg="#F9E7EC")

        self.setup_styles()
        self.ultimo_programa = None
        self.ultimo_tac = None
        self.setup_ui()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background="#F9E7EC", borderwidth=0)
        style.configure("TNotebook.Tab", background="#FFFFFF", padding=[20, 8], 
                       font=("Helvetica", 10, "bold"), foreground="#C15A7D")
        style.map("TNotebook.Tab", background=[("selected", "#F7CBD8")], 
                 foreground=[("selected", "#7A2E4D")])
        style.configure("Card.TFrame", background="#FFFFFF", relief="flat")

    def setup_ui(self):
        # HEADER
        header = tk.Frame(self.ventana, bg="#F7CBD8", height=95, bd=0)
        header.pack(fill="x", padx=22, pady=18)
        header.pack_propagate(False)

        tk.Label(header, 
                 text="Compilador Mini Lenguaje",
                 bg="#F7CBD8",
                 fg="#7A2E4D",
                 font=("Helvetica", 20, "bold")).pack(pady=10)

        tk.Label(header,
                 text="Léxico • Sintáctico • Semántico • TAC",
                 bg="#F7CBD8",
                 fg="#7A2E4D",
                 font=("Helvetica", 12)).pack()

        # CÓDIGO FUENTE
        tk.Label(self.ventana, text="Código Fuente:",
                 bg="#F9E7EC", fg="#B65075",
                 font=("Helvetica", 12, "bold")).pack(pady=(5, 2))

        self.entrada = scrolledtext.ScrolledText(
            self.ventana,
            width=110, height=10,
            font=("Consolas", 11),
            bg="#FFFFFF",
            fg="#333333",
            relief="flat",
            bd=12,
            padx=12,
            pady=12
        )
        self.entrada.pack(padx=20, pady=8)

        # Código de ejemplo
        codigo_ejemplo = """print("Hola mundo!");
var x = 10;
if (x > 5) {
    print("x es mayor que 5");
}"""
        self.entrada.insert("1.0", codigo_ejemplo)

        # BOTONES
        botones_frame = tk.Frame(self.ventana, bg="#F9E7EC")
        botones_frame.pack(pady=10)

        botones_info = [
            ("🔤 Léxico", "#F4B6CC", self.analizar_lexico),
            ("🌳 Sintáctico", "#F4A2C3", self.analizar_sintactico),
            ("📊 Semántico", "#EF8AB7", self.analizar_semantico),
            ("⚡ TAC", "#DD79A7", self.compilar_tac),
            ("▶ Ejecutar", "#C86696", self.ejecutar_tac),
            ("🚀 Todo", "#B75586", self.compilar_ejecutar_todo),
            ("🧹 Limpiar", "#A64575", self.limpiar),
        ]

        for i, (texto, color, comando) in enumerate(botones_info):
            btn = tk.Button(
                botones_frame,
                text=texto,
                bg=color,
                fg="white",
                font=("Helvetica", 10, "bold"),
                relief="flat",
                activebackground="#7A2E4D",
                cursor="hand2",
                width=12,
                height=2,
                bd=0,
                highlightthickness=0,
                command=comando
            )
            btn.grid(row=0, column=i, padx=6, pady=6)

        # NOTEBOOK
        self.notebook = ttk.Notebook(self.ventana)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=15)

        self.salida = self.create_tab("📝 Análisis General")
        self.tokens_area = self.create_tab("🔤 Tokens")
        self.tac_area = self.create_tab("⚡ TAC")
        self.resultados_area = self.create_tab("📊 Resultados")

        self.setup_text_tags()

        # ESTADO
        self.estado = tk.Label(
            self.ventana,
            text="Listo para compilar…",
            bg="#F9E7EC",
            fg="#B65075",
            font=("Helvetica", 11, "italic")
        )
        self.estado.pack(pady=3)

    def create_tab(self, titulo):
        frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(frame, text=titulo)

        area = scrolledtext.ScrolledText(
            frame,
            width=100,
            height=15,
            font=("Consolas", 10),
            bg="#FFFFFF",
            relief="flat",
            bd=10
        )
        area.pack(fill="both", expand=True, padx=12, pady=12)
        return area

    def setup_text_tags(self):
        for area in [self.salida, self.tokens_area, self.tac_area, self.resultados_area]:
            area.tag_config("error", foreground="#D7263D", font=("Consolas", 10, "bold"))
            area.tag_config("success", foreground="#3FAE49", font=("Consolas", 10, "bold"))
            area.tag_config("warning", foreground="#E8A628", font=("Consolas", 10, "bold"))
            area.tag_config("info", foreground="#5A78D1", font=("Consolas", 10))
            area.tag_config("titulo", foreground="#B65075", font=("Consolas", 11, "bold"))
            area.tag_config("token", foreground="#874562")
            area.tag_config("value", foreground="#406B8E")

    # ------------------ FUNCIONES DE LOS BOTONES ------------------
    
    def get_codigo(self):
        return self.entrada.get("1.0", tk.END).strip()

    def limpiar(self):
        self.entrada.delete("1.0", tk.END)
        self.salida.delete("1.0", tk.END)
        self.tokens_area.delete("1.0", tk.END)
        self.tac_area.delete("1.0", tk.END)
        self.resultados_area.delete("1.0", tk.END)
        self.ultimo_programa = None
        self.ultimo_tac = None
        self.estado.config(text="Listo para nuevo código ✨")

    def analizar_lexico(self):
        codigo = self.get_codigo()
        if not codigo:
            messagebox.showwarning("Advertencia", "Escribe código fuente.")
            return

        self.tokens_area.delete("1.0", tk.END)

        try:
            tokens = obtener_tokens(codigo)
            self.tokens_area.insert(tk.END, " TOKENS ENCONTRADOS\n\n", "titulo")

            for token in tokens:
                tipo, valor, linea, columna = token
                self.tokens_area.insert(tk.END, f"Línea {linea}:{columna}\n", "info")
                self.tokens_area.insert(tk.END, f"  Tipo: ", "info")
                self.tokens_area.insert(tk.END, f"{tipo}\n", "token")
                self.tokens_area.insert(tk.END, f"  Valor: '{valor}'\n\n", "value")

            self.estado.config(text="Análisis léxico completado ✔")

        except Exception as e:
            self.tokens_area.insert(tk.END, f"❌ Error: {e}\n", "error")
            self.estado.config(text="Error léxico ❌")

    def analizar_sintactico(self):
        codigo = self.get_codigo()
        if not codigo:
            messagebox.showwarning("Advertencia", "Escribe código.")
            return

        self.salida.delete("1.0", tk.END)

        try:
            tokens_tuplas = obtener_tokens(codigo)
            tokens = [Token(t[0], t[1], t[2], t[3]) for t in tokens_tuplas]

            parser = Parser(tokens)
            program = parser.parse()
            self.ultimo_programa = program

            self.salida.insert(tk.END, "✅ ANÁLISIS SINTÁCTICO EXITOSO\n\n", "success")
            self.salida.insert(tk.END, "ÁRBOL SINTÁCTICO:\n", "titulo")
            self.salida.insert(tk.END, ast_to_str(program))

            self.estado.config(text="Análisis sintáctico ✔")

        except Exception as e:
            self.salida.insert(tk.END, f"❌ Error: {e}\n", "error")
            self.estado.config(text="Error sintáctico ❌")

    def analizar_semantico(self):
        if self.ultimo_programa is None:
            messagebox.showwarning("Advertencia", "Primero análisis sintáctico.")
            return

        self.salida.insert(tk.END, "\n" + "="*50 + "\n", "info")
        self.salida.insert(tk.END, "ANÁLISIS SEMÁNTICO\n", "titulo")

        try:
            sem = SemanticAnalyzer()
            errores = sem.analyze(self.ultimo_programa)

            if errores:
                for error in errores:
                    self.salida.insert(tk.END, f"⚠ {error}\n", "warning")
                self.salida.insert(tk.END, f"\n❌ Se encontraron {len(errores)} error(es) semántico(s)\n", "error")
            else:
                self.salida.insert(tk.END, "✅ Sin errores semánticos\n", "success")

            self.estado.config(text="Análisis semántico completado ✔")

        except Exception as e:
            self.salida.insert(tk.END, f"❌ Error: {e}\n", "error")
            self.estado.config(text="Error en análisis semántico ❌")

    def compilar_tac(self):
        if self.ultimo_programa is None:
            messagebox.showwarning("Advertencia", "Primero análisis sintáctico.")
            return

        # Verificar errores semánticos antes de generar TAC
        sem = SemanticAnalyzer()
        errores = sem.analyze(self.ultimo_programa)
        
        if errores:
            self.tac_area.delete("1.0", tk.END)
            self.tac_area.insert(tk.END, "❌ NO SE PUEDE GENERAR TAC - ERRORES SEMÁNTICOS:\n\n", "error")
            for error in errores:
                self.tac_area.insert(tk.END, f"⚠ {error}\n", "warning")
            self.estado.config(text="Generación TAC bloqueada por errores semánticos ❌")
            return

        self.tac_area.delete("1.0", tk.END)

        try:
            generator = CodeGenerator()
            tac_code = generator.generate(self.ultimo_programa)
            self.ultimo_tac = tac_code

            self.tac_area.insert(tk.END, "✅ CÓDIGO TAC GENERADO\n\n", "titulo")
            for i, instruction in enumerate(tac_code, 1):
                self.tac_area.insert(tk.END, f"{i:3}: {instruction}\n")

            self.estado.config(text="TAC generado ✔")

        except Exception as e:
            self.tac_area.insert(tk.END, f"❌ Error: {e}\n", "error")
            self.estado.config(text="Error generando TAC ❌")

    def ejecutar_tac(self):
        if self.ultimo_programa is None:
            messagebox.showwarning("Advertencia", "Primero análisis sintáctico.")
            return
    
        # Verificar errores semánticos antes de ejecutar
        sem = SemanticAnalyzer()
        errores = sem.analyze(self.ultimo_programa)
        
        if errores:
            self.resultados_area.delete("1.0", tk.END)
            self.resultados_area.insert(tk.END, "❌ NO SE PUEDE EJECUTAR - ERRORES SEMÁNTICOS:\n\n", "error")
            for error in errores:
                self.resultados_area.insert(tk.END, f"⚠ {error}\n", "warning")
            self.estado.config(text="Ejecución bloqueada por errores semánticos ❌")
            return

        if self.ultimo_tac is None:
            messagebox.showwarning("Advertencia", "Primero genera el TAC.")
            return

        self.resultados_area.delete("1.0", tk.END)

        try:
            interpreter = TACInterpreter()
            resultados = interpreter.execute(self.ultimo_tac)

            self.resultados_area.insert(tk.END, "--- SALIDA DEL PROGRAMA ---\n", "titulo")
            
            if resultados:
                for r in resultados:
                    if r.startswith("Error:"):
                        self.resultados_area.insert(tk.END, f"❌ {r}\n", "error")
                    else:
                        self.resultados_area.insert(tk.END, f"{r}\n", "info")
            else:
                self.resultados_area.insert(tk.END, "✅ Programa ejecutado exitosamente (sin salida)\n", "success")

            if interpreter.had_execution_errors():
                self.estado.config(text="Ejecución completada con errores ⚠")
            else:
                self.estado.config(text="Programa ejecutado exitosamente ✅")

        except Exception as e:
            self.resultados_area.insert(tk.END, f"❌ Error fatal: {e}\n", "error")
            self.estado.config(text="Error en ejecución ❌")

    def compilar_ejecutar_todo(self):
        self.estado.config(text="Compilando…")
        
        # Limpiar áreas primero
        self.salida.delete("1.0", tk.END)
        self.tac_area.delete("1.0", tk.END)
        self.resultados_area.delete("1.0", tk.END)
        
        try:
            # 1. Análisis léxico y sintáctico
            codigo = self.get_codigo()
            if not codigo:
                messagebox.showwarning("Advertencia", "Escribe código fuente.")
                return
                
            tokens_tuplas = obtener_tokens(codigo)
            tokens = [Token(t[0], t[1], t[2], t[3]) for t in tokens_tuplas]
            
            parser = Parser(tokens)
            program = parser.parse()
            self.ultimo_programa = program
            
            self.salida.insert(tk.END, "✅ ANÁLISIS SINTÁCTICO EXITOSO\n\n", "success")
            
            # 2. Análisis semántico
            sem = SemanticAnalyzer()
            errores = sem.analyze(program)
            
            if errores:
                self.salida.insert(tk.END, "❌ ERRORES SEMÁNTICOS ENCONTRADOS:\n\n", "error")
                for error in errores:
                    self.salida.insert(tk.END, f"⚠ {error}\n", "warning")
                
                self.salida.insert(tk.END, f"\n🚫 COMPILACIÓN DETENIDA: {len(errores)} error(es) semántico(s)\n", "error")
                self.estado.config(text="Compilación falló por errores semánticos ❌")
                return  # ✅ DETENER aquí
            
            self.salida.insert(tk.END, "✅ SIN ERRORES SEMÁNTICOS\n\n", "success")
            
            # 3. Generación TAC (solo si no hay errores)
            generator = CodeGenerator()
            tac_code = generator.generate(program)
            self.ultimo_tac = tac_code
            
            self.tac_area.insert(tk.END, "✅ CÓDIGO TAC GENERADO\n\n", "titulo")
            for i, instruction in enumerate(tac_code, 1):
                self.tac_area.insert(tk.END, f"{i:3}: {instruction}\n")
            
            # 4. Ejecución (solo si no hay errores)
            self.resultados_area.insert(tk.END, "--- EJECUCIÓN ---\n", "titulo")
            interpreter = TACInterpreter()
            resultados = interpreter.execute(tac_code)
            
            for r in resultados:
                if r.startswith("Error:"):
                    self.resultados_area.insert(tk.END, f"❌ {r}\n", "error")
                else:
                    self.resultados_area.insert(tk.END, f"{r}\n", "info")
            
            if interpreter.had_execution_errors():
                self.estado.config(text="Ejecución completada con errores ⚠")
            else:
                self.estado.config(text="Compilación y ejecución completadas ✅")
            
        except Exception as e:
            self.salida.insert(tk.END, f"❌ ERROR DE COMPILACIÓN: {e}\n", "error")
            self.estado.config(text="Error en compilación ❌")

    def run(self):
        self.ventana.mainloop()

if __name__ == "__main__":
    compiler = CompilerInterface()
    compiler.run()