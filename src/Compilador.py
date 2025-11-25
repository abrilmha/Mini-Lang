# Compilador.py 
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
from AnalizadorLexico import obtener_tokens
from SintacticoSemantico import Parser, Token, SemanticAnalyzer, ast_to_str
from CodeGen import CodeGenerator
from tac_interpreter import TACInterpreter

class CompilerInterface:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title(" Mini-Language Compiler ")
        self.window.geometry("1000x820")
        self.window.configure(bg="#F9E7EC")

        self.setup_styles()
        self.last_program = None
        self.last_tac = None
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
        header = tk.Frame(self.window, bg="#F7CBD8", height=95, bd=0)
        header.pack(fill="x", padx=22, pady=18)
        header.pack_propagate(False)

        tk.Label(header, 
                 text="Mini-Language Compiler",
                 bg="#F7CBD8",
                 fg="#7A2E4D",
                 font=("Helvetica", 20, "bold")).pack(pady=10)

        tk.Label(header,
                 text="Lexical • Syntactic • Semantic • TAC",
                 bg="#F7CBD8",
                 fg="#7A2E4D",
                 font=("Helvetica", 12)).pack()

        # SOURCE CODE
        tk.Label(self.window, text="Source Code:",
                 bg="#F9E7EC", fg="#B65075",
                 font=("Helvetica", 12, "bold")).pack(pady=(5, 2))

        self.input_area = scrolledtext.ScrolledText(
            self.window,
            width=110, height=10,
            font=("Consolas", 11),
            bg="#FFFFFF",
            fg="#333333",
            relief="flat",
            bd=12,
            padx=12,
            pady=12
        )
        self.input_area.pack(padx=20, pady=8)

        # BUTTONS
        buttons_frame = tk.Frame(self.window, bg="#F9E7EC")
        buttons_frame.pack(pady=10)

        buttons_info = [
            ("LEXER", "#F4B6CC", self.analizar_lexico),
            ("SYNTACTIC", "#F4A2C3", self.analizar_sintactico),
            ("SEMANTIC", "#EF8AB7", self.analizar_semantico),
            ("TAC", "#DD79A7", self.compilar_tac),
            ("▶ RUN", "#C86696", self.ejecutar_tac),
            ("ALL", "#B75586", self.compilar_ejecutar_todo),
            ("🧹 CLEAN", "#A64575", self.limpiar),
        ]

        for i, (text, color, command) in enumerate(buttons_info):
            btn = tk.Button(
                buttons_frame,
                text=text,
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
                command=command
            )
            btn.grid(row=0, column=i, padx=6, pady=6)

        # NOTEBOOK
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=15)

        self.output_area = self.create_tab("General Analysis")
        self.tokens_area = self.create_tab("Tokens")
        self.tac_area = self.create_tab("⚡ TAC")
        self.results_area = self.create_tab("Results")

        self.setup_text_tags()

        # STATUS
        self.status = tk.Label(
            self.window,
            text="Ready to compile…",
            bg="#F9E7EC",
            fg="#B65075",
            font=("Helvetica", 11, "italic")
        )
        self.status.pack(pady=3)

    def create_tab(self, title):
        frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(frame, text=title)

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
        for area in [self.output_area, self.tokens_area, self.tac_area, self.results_area]:
            area.tag_config("error", foreground="#D7263D", font=("Consolas", 10, "bold"))
            area.tag_config("success", foreground="#3FAE49", font=("Consolas", 10, "bold"))
            area.tag_config("warning", foreground="#E8A628", font=("Consolas", 10, "bold"))
            area.tag_config("info", foreground="#5A78D1", font=("Consolas", 10))
            area.tag_config("title", foreground="#B65075", font=("Consolas", 11, "bold"))
            area.tag_config("token", foreground="#874562")
            area.tag_config("value", foreground="#406B8E")

    # ------------------ BUTTON FUNCTIONS ------------------
    
    def get_code(self):
        return self.input_area.get("1.0", tk.END).strip()

    def limpiar(self):
        self.input_area.delete("1.0", tk.END)
        self.output_area.delete("1.0", tk.END)
        self.tokens_area.delete("1.0", tk.END)
        self.tac_area.delete("1.0", tk.END)
        self.results_area.delete("1.0", tk.END)
        self.last_program = None
        self.last_tac = None
        self.status.config(text="Ready for new code")

    def analizar_lexico(self):
        code = self.get_code()
        if not code:
            messagebox.showwarning("Warning", "Write source code.")
            return

        self.tokens_area.delete("1.0", tk.END)

        try:
            tokens = obtener_tokens(code)
            self.tokens_area.insert(tk.END, " FOUND TOKENS\n\n", "title")

            for token in tokens:
                tipo, valor, linea, columna = token
                self.tokens_area.insert(tk.END, f"Line {linea}:{columna}\n", "info")
                self.tokens_area.insert(tk.END, f"  Type: ", "info")
                self.tokens_area.insert(tk.END, f"{tipo}\n", "token")
                self.tokens_area.insert(tk.END, f"  Value: '{valor}'\n\n", "value")

            self.status.config(text="LEXICAL ANALYSIS COMPLETE ✔")

        except Exception as e:
            self.tokens_area.insert(tk.END, f"❌ Error: {e}\n", "error")
            self.status.config(text="LEXICAL ERROR ❌")

    def analizar_sintactico(self):
        code = self.get_code()
        if not code:
            messagebox.showwarning("Warning", "Write source code.")
            return

        self.output_area.delete("1.0", tk.END)

        try:
            tokens_tuples = obtener_tokens(code)
            tokens = [Token(t[0], t[1], t[2], t[3]) for t in tokens_tuples]

            parser = Parser(tokens)
            program = parser.parse()
            self.last_program = program

            self.output_area.insert(tk.END, "SUCCESSFUL SYNTACTIC ANALYSIS\n\n", "success")
            self.output_area.insert(tk.END, "SYNTACTIC TREE:\n", "title")
            self.output_area.insert(tk.END, ast_to_str(program))

            self.status.config(text="Syntactic analysis completed ✔")

        except Exception as e:
            self.output_area.insert(tk.END, f"❌ Error: {e}\n", "error")
            self.status.config(text="Syntactic error ❌")

    def analizar_semantico(self):
        if self.last_program is None:
            messagebox.showwarning("Warning", "Syntactic analysis first.")
            return

        self.output_area.insert(tk.END, "\n" + "="*50 + "\n", "info")
        self.output_area.insert(tk.END, "SEMANTIC ANALYSIS\n", "title")

        try:
            sem = SemanticAnalyzer()
            errors = sem.analyze(self.last_program)

            if errors:
                for error in errors:
                    self.output_area.insert(tk.END, f"⚠ {error}\n", "warning")
                self.output_area.insert(tk.END, f"\n❌ Found {len(errors)} semantic error(s)\n", "error")
            else:
                self.output_area.insert(tk.END, "✅ No semantic errors\n", "success")

            self.status.config(text="Semantic analysis completed ✔")

        except Exception as e:
            self.output_area.insert(tk.END, f"❌ Error: {e}\n", "error")
            self.status.config(text="Semantic analysis error ❌")

    def compilar_tac(self):
        if self.last_program is None:
            messagebox.showwarning("Warning", "Syntactic analysis first.")
            return

        # Check semantic errors before generating TAC
        sem = SemanticAnalyzer()
        errors = sem.analyze(self.last_program)
        
        if errors:
            self.tac_area.delete("1.0", tk.END)
            self.tac_area.insert(tk.END, "❌ CANNOT GENERATE TAC - SEMANTIC ERRORS:\n\n", "error")
            for error in errors:
                self.tac_area.insert(tk.END, f"⚠ {error}\n", "warning")
            self.status.config(text="TAC generation blocked by semantic errors ❌")
            return

        self.tac_area.delete("1.0", tk.END)

        try:
            generator = CodeGenerator()
            tac_code = generator.generate(self.last_program)
            self.last_tac = tac_code

            self.tac_area.insert(tk.END, "✅ TAC CODE GENERATED\n\n", "title")
            for i, instruction in enumerate(tac_code, 1):
                self.tac_area.insert(tk.END, f"{i:3}: {instruction}\n")

            self.status.config(text="TAC generated ✔")

        except Exception as e:
            self.tac_area.insert(tk.END, f"❌ Error: {e}\n", "error")
            self.status.config(text="Error generating TAC ❌")

    def ejecutar_tac(self):
        if self.last_program is None:
            messagebox.showwarning("Warning", "Syntactic analysis first.")
            return
    
        # Check semantic errors before execution
        sem = SemanticAnalyzer()
        errors = sem.analyze(self.last_program)
        
        if errors:
            self.results_area.delete("1.0", tk.END)
            self.results_area.insert(tk.END, "❌ CANNOT EXECUTE - SEMANTIC ERRORS:\n\n", "error")
            for error in errors:
                self.results_area.insert(tk.END, f"⚠ {error}\n", "warning")
            self.status.config(text="Execution blocked by semantic errors ❌")
            return

        if self.last_tac is None:
            messagebox.showwarning("Warning", "Generate TAC first.")
            return

        self.results_area.delete("1.0", tk.END)

        try:
            interpreter = TACInterpreter()
            results = interpreter.execute(self.last_tac)

            self.results_area.insert(tk.END, "--- PROGRAM OUTPUT ---\n", "title")
            
            if results:
                for r in results:
                    if r.startswith("Error:"):
                        self.results_area.insert(tk.END, f"❌ {r}\n", "error")
                    else:
                        self.results_area.insert(tk.END, f"{r}\n", "info")
            else:
                self.results_area.insert(tk.END, "✅ Program executed successfully (no output)\n", "success")

            if interpreter.had_execution_errors():
                self.status.config(text="Execution completed with errors ⚠")
            else:
                self.status.config(text="Program executed successfully ✅")

        except Exception as e:
            self.results_area.insert(tk.END, f"❌ Fatal error: {e}\n", "error")
            self.status.config(text="Execution error ❌")

    def compilar_ejecutar_todo(self):
        self.status.config(text="Compiling…")
        
        # Clear areas first
        self.output_area.delete("1.0", tk.END)
        self.tac_area.delete("1.0", tk.END)
        self.results_area.delete("1.0", tk.END)
        
        try:
            # 1. Lexical and syntactic analysis
            code = self.get_code()
            if not code:
                messagebox.showwarning("Warning", "Write source code.")
                return
                
            tokens_tuples = obtener_tokens(code)
            tokens = [Token(t[0], t[1], t[2], t[3]) for t in tokens_tuples]
            
            parser = Parser(tokens)
            program = parser.parse()
            self.last_program = program
            
            self.output_area.insert(tk.END, "✅ SUCCESSFUL SYNTACTIC ANALYSIS\n\n", "success")
            
            # 2. Semantic analysis
            sem = SemanticAnalyzer()
            errors = sem.analyze(program)
            
            if errors:
                self.output_area.insert(tk.END, "❌ SEMANTIC ERRORS FOUND:\n\n", "error")
                for error in errors:
                    self.output_area.insert(tk.END, f"⚠ {error}\n", "warning")
                
                self.output_area.insert(tk.END, f"\n🚫 COMPILATION HALTED: {len(errors)} semantic error(s)\n", "error")
                self.status.config(text="Compilation failed due to semantic errors ❌")
                return
            
            self.output_area.insert(tk.END, "✅ NO SEMANTIC ERRORS\n\n", "success")
            
            # 3. TAC generation (only if no errors)
            generator = CodeGenerator()
            tac_code = generator.generate(program)
            self.last_tac = tac_code
            
            self.tac_area.insert(tk.END, "✅ TAC CODE GENERATED\n\n", "title")
            for i, instruction in enumerate(tac_code, 1):
                self.tac_area.insert(tk.END, f"{i:3}: {instruction}\n")
            
            # 4. Execution (only if no errors)
            self.results_area.insert(tk.END, "--- EXECUTION ---\n", "title")
            interpreter = TACInterpreter()
            results = interpreter.execute(tac_code)
            
            for r in results:
                if r.startswith("Error:"):
                    self.results_area.insert(tk.END, f"❌ {r}\n", "error")
                else:
                    self.results_area.insert(tk.END, f"{r}\n", "info")
            
            if interpreter.had_execution_errors():
                self.status.config(text="Execution completed with errors ⚠")
            else:
                self.status.config(text="Compilation and execution completed ✅")
            
        except Exception as e:
            self.output_area.insert(tk.END, f"❌ COMPILATION ERROR: {e}\n", "error")
            self.status.config(text="Compilation error ❌")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    compiler = CompilerInterface()
    compiler.run()
