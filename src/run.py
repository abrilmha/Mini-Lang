import sys
from AnalizadorLexico import obtener_tokens
from SintacticoSemantico import Parser, Token, SemanticAnalyzer
from CodeGen import CodeGenerator
from tac_interpreter import TACInterpreter

def run_file(path):

    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: file '{path}' not found.")
        return

    print(f"\n=== Running Mini-Lang Program: {path} ===\n")

    try:
        # 1. Lexical analysis
        tokens = obtener_tokens(code)

        # 2. Parsing
        ast = Parser([Token(*t) for t in tokens]).parse()

        # 3. Semantic analysis
        sem_analyzer = SemanticAnalyzer()
        sem_errors = sem_analyzer.analyze(ast)
        
       
        if sem_errors:
            print("❌ SEMANTIC ERRORS FOUND - COMPILATION STOPPED:")
            for error in sem_errors:
                print(f"   ⚠ {error}")
            print(f"\nCompilation failed with {len(sem_errors)} error(s)")
            return 1  

        # 4. TAC generation 
        tac = CodeGenerator().generate(ast)
        print("\n--- Generated TAC ---")
        for i, instr in enumerate(tac, 1):
            print(f"{i:03}:", instr)

        # 5. Execution 
        print("\n--- Program Output ---")
        interpreter = TACInterpreter()
        output = interpreter.execute(tac)

        for line in output:
            print(line)

        if interpreter.had_execution_errors():
            print(f"\n❌ Execution finished with errors")
            return 1
        else:
            print(f"\n✅ Execution finished successfully")
            return 0

    except Exception as e:
        print(f"❌ COMPILATION ERROR: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run.py <file.src>")
        sys.exit(1)

    exit_code = run_file(sys.argv[1])
    sys.exit(exit_code)
