import sys
from lexer import AnalisadorLexico, ErroLexico
from parser import AnalisadorSintatico, ErroSintatico, Pipeline, Tarefa
from semantic import Task, SymbolTable, SemanticAnalyzer, dump_symbol_table
from codegen import IRGenerator, generate_pseudo_code


class ASTConverter:
    def convert_pipeline_to_tasks(self, pipeline: Pipeline):
        tasks = []
        for tarefa in pipeline.tarefas:
            task = self._convert_tarefa(tarefa)
            tasks.append(task)
        return tasks

    def _convert_tarefa(self, tarefa: Tarefa):
        depends = tarefa.dependencias if tarefa.dependencias else []
        kind = self._infer_task_kind(tarefa)

        if kind == "EXTRACT":
            inputs = []
            outputs = [tarefa.saida.destino] if tarefa.saida else []
        elif kind == "LOAD":
            inputs = [tarefa.origem.fonte] if tarefa.origem else []
            outputs = []
        else:
            inputs = [tarefa.origem.fonte] if tarefa.origem else []
            outputs = [tarefa.saida.destino] if tarefa.saida else []

        return Task(
            name=tarefa.nome,
            kind=kind,
            inputs=inputs,
            outputs=outputs,
            depends=depends,
            lineno=0
        )

    def _infer_task_kind(self, tarefa: Tarefa):
        if tarefa.transformacao:
            return "TRANSFORM"
        elif tarefa.origem and not tarefa.dependencias:
            return "EXTRACT"
        elif tarefa.saida and tarefa.dependencias:
            return "LOAD"
        else:
            return "TRANSFORM"


class PipeLangCompiler:
    def __init__(self):
        self.lexer = None
        self.parser = None
        self.ast = None
        self.tasks = None
        self.symbol_table = None
        self.errors = []

    def compile_from_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        return self.compile(source_code, file_path)

    def compile(self, source_code, source_name="<input>"):
        print(f"[1/5] Analise Lexica...")
        try:
            self.lexer = AnalisadorLexico(source_code)
            tokens = self.lexer.analisar()
            print(f"      {len(tokens) - 1} tokens identificados")
        except ErroLexico as e:
            print(f"[ERRO] {e}")
            return False

        print(f"[2/5] Analise Sintatica...")
        try:
            self.parser = AnalisadorSintatico(tokens)
            self.ast = self.parser.analisar()
            print(f"      Pipeline '{self.ast.nome}' com {len(self.ast.tarefas)} tarefa(s)")
        except ErroSintatico as e:
            print(f"[ERRO] {e}")
            return False

        print(f"[3/5] Conversao AST -> Tabela de Simbolos...")
        converter = ASTConverter()
        self.tasks = converter.convert_pipeline_to_tasks(self.ast)

        self.symbol_table = SymbolTable()
        for task in self.tasks:
            self.symbol_table.add(task, self.errors)

        if self.errors:
            print(f"[ERRO] Erros na construcao da tabela de simbolos:")
            for err in self.errors:
                print(f"       {err}")
            return False

        print(f"      {len(self.tasks)} tarefa(s) na tabela de simbolos")

        print(f"[4/5] Analise Semantica...")
        analyzer = SemanticAnalyzer(self.symbol_table)
        sem_errors = analyzer.run()

        if sem_errors:
            print(f"[ERRO] Erros semanticos encontrados:")
            for err in sem_errors:
                print(f"       {err}")
            self.errors.extend(sem_errors)
            return False

        print(f"      Nenhum erro semantico encontrado")

        print(f"[5/5] Geracao de Codigo Intermediario...")
        generator = IRGenerator(self.symbol_table, source_name)
        self.ir = generator.generate()
        print(f"      IR gerada com sucesso")

        return True

    def print_symbol_table(self):
        if self.symbol_table:
            print("\n" + "=" * 60)
            print(dump_symbol_table(self.symbol_table))

    def print_ir(self):
        if hasattr(self, 'ir'):
            print("\n" + "=" * 60)
            print("CODIGO INTERMEDIARIO (JSON):")
            print("=" * 60)
            generator = IRGenerator(self.symbol_table, "<compiled>")
            print(generator.to_json())

    def print_pseudo_code(self):
        if hasattr(self, 'ir'):
            print("\n" + "=" * 60)
            print(generate_pseudo_code(self.ir))

    def save_ir(self, output_path):
        if hasattr(self, 'ir'):
            generator = IRGenerator(self.symbol_table, "<compiled>")
            generator.save_to_file(output_path)
            print(f"\n[SAVE] IR salva em: {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Uso: python src/compiler.py <arquivo.pipe> [saida.json]")
        print("  arquivo.pipe: arquivo fonte PipeLang")
        print("  saida.json:   (opcional) arquivo de saida para IR")
        sys.exit(1)

    source_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    print("=" * 60)
    print("COMPILADOR PIPELANG")
    print("=" * 60)
    print(f"Arquivo: {source_path}\n")

    compiler = PipeLangCompiler()

    if compiler.compile_from_file(source_path):
        print("\n" + "=" * 60)
        print("[OK] COMPILACAO CONCLUIDA COM SUCESSO!")
        print("=" * 60)

        compiler.print_symbol_table()
        compiler.print_pseudo_code()

        if output_path:
            compiler.save_ir(output_path)

        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("[FALHA] COMPILACAO FALHOU")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
