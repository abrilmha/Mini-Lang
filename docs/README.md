# Mini-Lang Compiler v1.0

Mini-Lang is a small educational programming language implemented as a full compiler pipeline, including lexical analysis, parsing, semantic analysis, TAC (Three-Address Code) generation, and execution via a custom virtual machine.

This repository contains the final release of the Mini-Lang compiler for the course project.

---

##  Features

Mini-Lang supports:

- Variable declarations (`int`, `bool`, `float`)
- Assignments
- Arithmetic and boolean expressions
- Conditionals (`if`, `if-else`)
- Loops (`while`)
- Scoping rules and semantic checks
- TAC generation (Three-Address Code)
- TAC interpreter / Virtual Machine
- GUI runner implemented in Tkinter

---

## Repository Structure
```text
Mini-Lang/
│
├── docs/
│   ├── README.md
│   ├── language-spec.md
│   └── demo-scripts.md
│
├── src/
│   ├── AnalizadorLexico.py
│   ├── SintacticoSemantico.py
│   ├── CodeGen.py
│   ├── tac_interpreter.py
│   ├── Compilador.py
│   └── run.py
│
├── tests/
│   ├── arithmetic.src
│   ├── bool_expr.src
│   ├── decl_assign.src
│   ├── full_program.src
│   ├── if_else.src
│   ├── io.src
│   ├── loop_break.src
│   ├── multi_scope.src
│   ├── nested_if.src
│   ├── type_mismatch.src
│   ├── udeclared.src
│   └── while_loop.src
│
├── requirements.txt
├── .gitignore
└── LICENSE
```
## How to Run
1. GUI Interface (Recommended)
```bash
python src/Compilador.py
```
2. Command Line Execution
```bash
ython run.py <path-to-program-test.src>
```
## Requirements
- Python 3.6+
- No external dependencies (uses only built-in libraries)

##  Development Journey

The compiler evolved through three main iterations:

### v0.1 – Lexical Analyzer
- Token pattern development
- Regex-based scanning  
- Basic error reporting

### v0.2 – Full Parser & Semantic Analyzer
- AST construction
- Scope validation
- Type checking system

### v1.0 – Complete Compiler  **CURRENT RELEASE**
- TAC code generation
- Virtual machine execution  
- GUI interface
- Automated testing suite
- End-to-end compilation pipeline

## Reproducibility Appendix 

Exact commands to reproduce results (ready to paste):

### Clone repository

```bash
git clone https://github.com/abrilmha/Mini-Lang.git
cd Mini-Lang
```

Environment

OS: Windows 10 / macOS / Linux

Python: 3.11+

No external dependencies

Dataset / Inputs

All test programs are located in:

Mini-Lang/src/tests/
