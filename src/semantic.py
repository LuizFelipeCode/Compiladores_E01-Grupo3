import sys
import re
from collections import defaultdict

class Task:
    def __init__(self, name, kind, inputs=None, outputs=None, depends=None, lineno=0):
        self.name = name
        self.kind = kind  
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.depends = depends or []
        self.lineno = lineno

    def __repr__(self):
        return f"Task({self.name}, {self.kind}, in={self.inputs}, out={self.outputs}, dep={self.depends})"

class SymbolTable:
    def __init__(self):
        self.tasks = {}  

    def add(self, task, errors):
        if task.name in self.tasks:
            errors.append(f"[E-DUP] Tarefa '{task.name}' já foi declarada (linha {task.lineno}).")
        else:
            self.tasks[task.name] = task

    def __contains__(self, name):
        return name in self.tasks

    def __getitem__(self, name):
        return self.tasks[name]

    def all(self):
        return list(self.tasks.values())

class ParserNaive:
    TASK_HEADER = re.compile(r'^\s*task\s+([A-Za-z_][\w]*)\s*:\s*(EXTRACT|TRANSFORM|LOAD)\s*$', re.IGNORECASE)
    KV_LINE = re.compile(r'^\s*(inputs|outputs|depends_on)\s*:\s*(.+)$', re.IGNORECASE)

    @staticmethod
    def remove_comment(text):
        comment_pos = text.find('#')
        if comment_pos != -1:
            return text[:comment_pos].strip()
        return text.strip()

    def parse_file(self, path):
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        tasks = []
        cur = None
        for idx, line in enumerate(lines, start=1):
            line_stripped = self.remove_comment(line)

            if not line_stripped:
                continue
            if line_stripped.lower() == "end":
                if cur:
                    tasks.append(cur)
                    cur = None
                continue

            m = self.TASK_HEADER.match(line_stripped)
            if m:
                name, kind = m.group(1), m.group(2).upper()
                cur = Task(name=name, kind=kind, lineno=idx)
                continue

            m = self.KV_LINE.match(line_stripped)
            if m and cur:
                key = m.group(1).lower()
                value_part = self.remove_comment(m.group(2))
                vals = [v.strip() for v in value_part.split(",") if v.strip()]
                if key == "inputs":
                    cur.inputs.extend(vals)
                elif key == "outputs":
                    cur.outputs.extend(vals)
                elif key == "depends_on":
                    cur.depends.extend(vals)
                continue
        return tasks

class SemanticAnalyzer:
    def __init__(self, symtab):
        self.symtab = symtab
        self.errors = []

    def run(self):
        self._check_undeclared_dependencies()
        self._check_input_producers()
        self._check_cycles()
        return self.errors

    def _check_undeclared_dependencies(self):
        for t in self.symtab.all():
            for d in t.depends:
                if d not in self.symtab:
                    self.errors.append(f"[E-DEP] '{t.name}' depende de '{d}', que não existe (linha {t.lineno}).")

    def _check_input_producers(self):
        produced_by = defaultdict(list)
        for t in self.symtab.all():
            for o in t.outputs:
                produced_by[o].append(t.name)

        for t in self.symtab.all():
            for i in t.inputs:
                if i not in produced_by:
                    self.errors.append(f"[E-IN] Input '{i}' de '{t.name}' não é produzido por nenhuma tarefa (linha {t.lineno}).")

    def _check_cycles(self):
        graph = {t.name: t.depends for t in self.symtab.all()}
        visited, stack = set(), set()

        def dfs(u):
            if u in stack:
                return True
            if u in visited:
                return False
            visited.add(u)
            stack.add(u)
            for v in graph.get(u, []):
                if v in graph and dfs(v):
                    return True
            stack.remove(u)
            return False

        for node in graph:
            if dfs(node):
                self.errors.append("[E-CYCLE] Ciclo detectado no grafo de dependências.")
                break

def build_symbol_table(tasks):
    sym = SymbolTable()
    errors = []
    for t in tasks:
        sym.add(t, errors)
    return sym, errors

def dump_symbol_table(sym):
    lines = ["== Tabela de Símbolos =="]
    for t in sym.all():
        lines.append(f"- {t.name} : {t.kind}")
        if t.inputs:  lines.append(f"    inputs:  {', '.join(t.inputs)}")
        if t.outputs: lines.append(f"    outputs: {', '.join(t.outputs)}")
        if t.depends: lines.append(f"    deps:    {', '.join(t.depends)}")
    return "\n".join(lines)

def main():
    if len(sys.argv) < 2:
        print("Uso: python src/semantic.py <arquivo.pipe>")
        sys.exit(1)

    path = sys.argv[1]
    parser = ParserNaive()
    tasks = parser.parse_file(path)

    sym, sym_errors = build_symbol_table(tasks)
    analyzer = SemanticAnalyzer(sym)
    sem_errors = analyzer.run()

    errors = sym_errors + sem_errors

    print(dump_symbol_table(sym))
    print("\n== Relatório de Análise Semântica ==")
    if errors:
        for e in errors:
            print(f"- {e}")
        print("\nStatus: FALHA (corrija os erros acima)")
        sys.exit(2)
    else:
        print("- Nenhum erro semântico encontrado.")
        print("Status: OK")
        sys.exit(0)

if __name__ == "__main__":
    main()
