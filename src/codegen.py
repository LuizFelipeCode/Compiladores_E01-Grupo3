import json
import sys
from datetime import datetime
from collections import deque, defaultdict
from semantic import ParserNaive, build_symbol_table, SemanticAnalyzer


class IRGenerator:

    def __init__(self, symbol_table, source_file):
        self.symtab = symbol_table
        self.source_file = source_file

    def generate(self):
        ir = {
            "metadata": self._generate_metadata(),
            "artifacts": self._generate_artifacts(),
            "tasks": self._generate_tasks(),
            "dependencies": self._generate_dependency_graph(),
            "execution_order": self._calculate_execution_order()
        }
        return ir

    def _generate_metadata(self):
        return {
            "compiler": "PipeLang Compiler v0.2",
            "source_file": self.source_file,
            "generated_at": datetime.now().isoformat(),
            "total_tasks": len(self.symtab.all()),
            "format_version": "1.0"
        }

    def _generate_artifacts(self):
        artifacts = {}

        for task in self.symtab.all():
            for output in task.outputs:
                if output not in artifacts:
                    artifacts[output] = {
                        "name": output,
                        "produced_by": task.name,
                        "consumed_by": []
                    }

        for task in self.symtab.all():
            for input_artifact in task.inputs:
                if input_artifact in artifacts:
                    artifacts[input_artifact]["consumed_by"].append(task.name)
                else:
                    artifacts[input_artifact] = {
                        "name": input_artifact,
                        "produced_by": None,
                        "consumed_by": [task.name],
                        "warning": "No producer found"
                    }

        return artifacts

    def _generate_tasks(self):
        tasks = []

        for task in self.symtab.all():
            task_ir = {
                "id": task.name,
                "type": task.kind,
                "inputs": task.inputs,
                "outputs": task.outputs,
                "depends_on": task.depends,
                "source_line": task.lineno,
                "state": "pending"
            }
            tasks.append(task_ir)

        return tasks

    def _generate_dependency_graph(self):
        graph = {}

        for task in self.symtab.all():
            graph[task.name] = task.depends[:]

        return graph

    def _calculate_execution_order(self):
        in_degree = defaultdict(int)
        adj_list = defaultdict(list)

        all_tasks = set()
        for task in self.symtab.all():
            all_tasks.add(task.name)
            for dep in task.depends:
                adj_list[dep].append(task.name)
                in_degree[task.name] += 1

        queue = deque([task for task in all_tasks if in_degree[task] == 0])
        execution_order = []

        while queue:
            current = queue.popleft()
            execution_order.append(current)

            for neighbor in adj_list[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(execution_order) != len(all_tasks):
            return {
                "error": "Cycle detected - cannot determine execution order",
                "partial_order": execution_order
            }

        return execution_order

    def to_json(self, indent=2):
        ir = self.generate()
        return json.dumps(ir, indent=indent, ensure_ascii=False)

    def save_to_file(self, output_path, indent=2):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json(indent=indent))


def generate_pseudo_code(ir):
    lines = []
    lines.append("=" * 60)
    lines.append("PSEUDO-CODIGO DO PIPELINE")
    lines.append("=" * 60)
    lines.append(f"# Fonte: {ir['metadata']['source_file']}")
    lines.append(f"# Tarefas: {ir['metadata']['total_tasks']}")
    lines.append("")

    if isinstance(ir['execution_order'], list):
        lines.append("ORDEM DE EXECUCAO:")
        for i, task_name in enumerate(ir['execution_order'], 1):
            lines.append(f"  {i}. {task_name}")
        lines.append("")

    lines.append("TAREFAS:")
    for task in ir['tasks']:
        lines.append(f"\nTASK {task['id']} ({task['type']}):")

        if task['depends_on']:
            lines.append(f"  WAIT_FOR: {', '.join(task['depends_on'])}")

        if task['inputs']:
            lines.append(f"  READ: {', '.join(task['inputs'])}")

        lines.append(f"  EXECUTE: {task['type'].lower()}_operation()")

        if task['outputs']:
            lines.append(f"  WRITE: {', '.join(task['outputs'])}")

        lines.append(f"  MARK_COMPLETE: {task['id']}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Uso: python src/codegen.py <arquivo.pipe> [saida.json]")
        print("  arquivo.pipe: arquivo fonte PipeLang")
        print("  saida.json:   (opcional) arquivo de saida para IR")
        sys.exit(1)

    source_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"[1/4] Analisando arquivo: {source_path}")
    parser = ParserNaive()
    tasks = parser.parse_file(source_path)

    print(f"[2/4] Construindo tabela de simbolos...")
    sym, sym_errors = build_symbol_table(tasks)

    print(f"[3/4] Executando analise semantica...")
    analyzer = SemanticAnalyzer(sym)
    sem_errors = analyzer.run()

    errors = sym_errors + sem_errors

    if errors:
        print("\n[ERRO] Encontrados erros semanticos:")
        for e in errors:
            print(f"  - {e}")
        print("\nNao e possivel gerar codigo intermediario com erros.")
        sys.exit(2)

    print(f"[4/4] Gerando representacao intermediaria (IR)...")
    generator = IRGenerator(sym, source_path)
    ir = generator.generate()

    print("\n" + "=" * 60)
    print("CODIGO INTERMEDIARIO GERADO COM SUCESSO")
    print("=" * 60)

    print("\n[JSON] REPRESENTACAO JSON:")
    print(generator.to_json())

    print("\n[PSEUDO] REPRESENTACAO EM PSEUDO-CODIGO:")
    print(generate_pseudo_code(ir))

    if output_path:
        generator.save_to_file(output_path)
        print(f"\n[SAVE] IR salva em: {output_path}")

    print("\n[OK] Geracao de codigo intermediario concluida!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
